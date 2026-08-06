from models.data_manager import DataManager
import pandas as pd

# CO and PO attainment calculations
# Basic approach:
# - For CO attainment: group questions by CO, compute per-student CO score (% of max),
#   then compute percentage of students who reached `pass_percent` threshold.
# - For PO attainment: map CO -> PO via co_po mapping; compute PO score as weighted
#   aggregation of CO scores (weights from mapping Level), then compute attainment.


def _numeric_key(x):
    import re
    x = str(x)
    m = re.search(r"(\d+)", x)
    return m.group(1) if m else x.strip()


def compute_co_attainment_for_subject(reference_id, subject_id, exam_types=None, pass_percent=40, use_btl=False):
    # Loads required datasets
    questions = DataManager.get("question_bank")
    marks = DataManager.get("marks")
    cos = DataManager.get("co")
    subjects = DataManager.get("subjects")
    students = DataManager.get("students")

    if questions is None or marks is None or cos is None or subjects is None or students is None:
        DataManager.refresh()
        questions = DataManager.get("question_bank")
        marks = DataManager.get("marks")
        cos = DataManager.get("co")
        subjects = DataManager.get("subjects")
        students = DataManager.get("students")

    # normalize keys
    questions = questions.copy()
    marks = marks.copy()
    cos = cos.copy()
    subjects = subjects.copy()
    students = students.copy()

    questions["SubjectID"] = questions["SubjectID"].astype(str).str.strip()
    marks["SubjectID"] = marks["SubjectID"].astype(str).str.strip()
    cos["SubjectID"] = cos["SubjectID"].astype(str).str.strip()
    subjects["SubjectID"] = subjects["SubjectID"].astype(str).str.strip()
    students["StudentID"] = students["StudentID"].astype(str).str.strip()

    questions["_SubjectKey"] = questions["SubjectID"].apply(_numeric_key)
    marks["_SubjectKey"] = marks["SubjectID"].apply(_numeric_key)
    cos["_SubjectKey"] = cos["SubjectID"].apply(_numeric_key)
    subjects["_SubjectKey"] = subjects["SubjectID"].apply(_numeric_key)

    subject_key = _numeric_key(subject_id)
    reference_id = str(reference_id).strip()

    # verify subject belongs to faculty
    match = subjects[(subjects["_SubjectKey"] == subject_key) & (subjects.get("FacultyID","") == reference_id)]
    if match.empty:
        return pd.DataFrame()

    # filter questions and marks for the subject
    subj_questions = questions[questions["_SubjectKey"] == subject_key]
    subj_marks = marks[marks["_SubjectKey"] == subject_key].copy()

    if exam_types:
        subj_marks = subj_marks[subj_marks["ExamType"].isin(exam_types)].copy()

    if subj_questions.empty:
        return pd.DataFrame()

    # join marks to questions to know COID and MaxMarks per question
    q_meta = subj_questions[["QuestionID", "COID", "MaxMarks"]].copy()
    q_meta["QuestionID"] = q_meta["QuestionID"].astype(str).str.strip()

    # prepare marks
    subj_marks.loc[:, "QuestionID"] = subj_marks["QuestionID"].astype(str).str.strip()
    # merge while preserving MaxMarks from marks (exam) and question bank
    subj_marks = subj_marks.merge(q_meta, on="QuestionID", how="left", suffixes=("","_q"))
    # compute effective MaxMarks: prefer marks' MaxMarks if present and >0, else question bank MaxMarks
    subj_marks.loc[:, "MarksObtained"] = pd.to_numeric(subj_marks.get("MarksObtained"), errors="coerce").fillna(0)
    subj_marks.loc[:, "MaxMarks_marks"] = pd.to_numeric(subj_marks.get("MaxMarks"), errors="coerce")
    subj_marks.loc[:, "MaxMarks_q"] = pd.to_numeric(subj_marks.get("MaxMarks_q"), errors="coerce")
    subj_marks.loc[:, "EffMax"] = subj_marks["MaxMarks_marks"].where(subj_marks["MaxMarks_marks"] > 0, subj_marks["MaxMarks_q"]).fillna(0)
    # If merge yields no CO mapping (all COID null), fall back to subject-level estimation
    if subj_marks["COID"].isna().all():
        # estimate per-student percent using total obtained over subject total max
        student_total = subj_marks.groupby("StudentID")["MarksObtained"].sum()
        subject_total_max = subj_questions["MaxMarks"].sum()
        if subject_total_max == 0:
            return pd.DataFrame()
        student_percent = (student_total / subject_total_max * 100).round(2)
        # build grouped DataFrame: each student repeats for every CO with same estimated percent
        subject_cos = cos[cos["_SubjectKey"] == subject_key]
        co_list = subject_cos["COID"].tolist() if not subject_cos.empty else []
        rows = []
        for sid, pct in student_percent.items():
            for coid in co_list:
                rows.append({"StudentID": sid, "COID": coid, "Percent": pct})
        grouped = pd.DataFrame(rows)
    else:
        subj_marks = subj_marks[~subj_marks["COID"].isna()].copy()

        if subj_marks.empty:
            return pd.DataFrame()

    # compute per-student per-CO obtained and max
    if subj_marks["COID"].isna().all():
        student_total = subj_marks.groupby("StudentID")["MarksObtained"].sum()
        subject_total_max = subj_questions["MaxMarks"].sum()
        if subject_total_max == 0:
            return pd.DataFrame()
        student_percent = (student_total / subject_total_max * 100).round(2)
        subject_cos = cos[cos["_SubjectKey"] == subject_key]
        co_list = subject_cos["COID"].tolist() if not subject_cos.empty else []
        rows = []
        for sid, pct in student_percent.items():
            for coid in co_list:
                rows.append({"StudentID": sid, "COID": coid, "Percent": pct})
        grouped = pd.DataFrame(rows)
    else:
        subj_marks = subj_marks[~subj_marks["COID"].isna()].copy()

        if subj_marks.empty:
            return pd.DataFrame()

        subj_marks.loc[:, "MarksObtained"] = pd.to_numeric(subj_marks["MarksObtained"], errors="coerce").fillna(0)
        subj_marks.loc[:, "EffMax"] = pd.to_numeric(subj_marks["EffMax"], errors="coerce").fillna(0)
        grouped = subj_marks.groupby(["StudentID", "COID"]).agg(
            Obtained=("MarksObtained", "sum"),
            Max=("EffMax", "sum")
        ).reset_index()

        # compute percent per student per CO
        grouped["Percent"] = (grouped["Obtained"] / grouped["Max"].replace(0, pd.NA) * 100).fillna(0).round(2)

    # pivot to students x CO
    pivot = grouped.pivot(index="StudentID", columns="COID", values="Percent").fillna(0)

    # for CO list, use cos for this subject
    subject_cos = cos[cos["_SubjectKey"] == subject_key]
    if subject_cos.empty:
        return pd.DataFrame()

    results = []
    # prefer counting students who actually have marks for this subject
    try:
        total_students = int(pivot.shape[0]) if 'pivot' in locals() and pivot.shape[0] > 0 else (
            len(students[students["Semester"] == match.iloc[0]["Semester"]]) if "Semester" in match.iloc[0].index else len(students)
        )
    except Exception:
        total_students = len(students)

    for _, co_row in subject_cos.iterrows():
        coid = co_row["COID"]
        co_desc = co_row.get("Description", "")
        # students who have percent entry for this co
        if coid in pivot.columns:
            percents = pivot[coid]
        else:
            percents = pd.Series(0, index=pivot.index)

        num_reached = (percents >= pass_percent).sum()
        attainment_percent = round(num_reached / max(1, total_students) * 100, 2)
        avg_percent = round(percents.mean(), 2) if len(percents) > 0 else 0

        results.append({
            "COID": coid,
            "Description": co_desc,
            "Target": pass_percent,
            "Attainment%": attainment_percent,
            "Avg%": avg_percent,
            "NumReached": int(num_reached),
            "TotalStudents": int(total_students)
        })

    return pd.DataFrame(results)


def compute_po_attainment_for_subject(reference_id, subject_id, exam_types=None, pass_percent=40):
    # PO attainment computed by mapping CO->PO using co_po mapping and combining CO scores
    co_po = DataManager.get("co_po")
    if co_po is None:
        DataManager.refresh()
        co_po = DataManager.get("co_po")

    # get CO attainment per student (raw percent per CO)
    # reuse logic from compute_co_attainment_for_subject but return pivot
    questions = DataManager.get("question_bank")
    marks = DataManager.get("marks")
    cos = DataManager.get("co")
    subjects = DataManager.get("subjects")
    students = DataManager.get("students")

    if any(x is None for x in [questions, marks, cos, subjects, students, co_po]):
        DataManager.refresh()
        questions = DataManager.get("question_bank")
        marks = DataManager.get("marks")
        cos = DataManager.get("co")
        subjects = DataManager.get("subjects")
        students = DataManager.get("students")
        co_po = DataManager.get("co_po")

    questions = questions.copy()
    marks = marks.copy()
    co_po = co_po.copy()
    subjects = subjects.copy()
    students = students.copy()

    questions["SubjectID"] = questions["SubjectID"].astype(str).str.strip()
    marks["SubjectID"] = marks["SubjectID"].astype(str).str.strip()
    co_po["SubjectID"] = co_po["SubjectID"].astype(str).str.strip()
    subjects["SubjectID"] = subjects["SubjectID"].astype(str).str.strip()
    students["StudentID"] = students["StudentID"].astype(str).str.strip()

    questions["_SubjectKey"] = questions["SubjectID"].apply(_numeric_key)
    marks["_SubjectKey"] = marks["SubjectID"].apply(_numeric_key)
    co_po["_SubjectKey"] = co_po["SubjectID"].apply(_numeric_key)
    subjects["_SubjectKey"] = subjects["SubjectID"].apply(_numeric_key)

    subject_key = _numeric_key(subject_id)
    reference_id = str(reference_id).strip()

    match = subjects[(subjects["_SubjectKey"] == subject_key) & (subjects.get("FacultyID","") == reference_id)]
    if match.empty:
        return pd.DataFrame()

    subj_questions = questions[questions["_SubjectKey"] == subject_key]
    subj_marks = marks[marks["_SubjectKey"] == subject_key].copy()

    if exam_types:
        subj_marks = subj_marks[subj_marks["ExamType"].isin(exam_types)].copy()

    q_meta = subj_questions[["QuestionID", "COID", "MaxMarks"]].copy()
    q_meta["QuestionID"] = q_meta["QuestionID"].astype(str).str.strip()
    subj_marks.loc[:, "QuestionID"] = subj_marks["QuestionID"].astype(str).str.strip()
    subj_marks = subj_marks.merge(q_meta, on="QuestionID", how="left", suffixes=("","_q"))
    subj_marks.loc[:, "MarksObtained"] = pd.to_numeric(subj_marks.get("MarksObtained"), errors="coerce").fillna(0)
    subj_marks.loc[:, "MaxMarks_marks"] = pd.to_numeric(subj_marks.get("MaxMarks"), errors="coerce")
    subj_marks.loc[:, "MaxMarks_q"] = pd.to_numeric(subj_marks.get("MaxMarks_q"), errors="coerce")
    subj_marks.loc[:, "EffMax"] = subj_marks["MaxMarks_marks"].where(subj_marks["MaxMarks_marks"] > 0, subj_marks["MaxMarks_q"]).fillna(0)
    subj_marks = subj_marks.copy()

    # For PO function fallback: if COID missing for all rows we create grouped later; here we just keep rows

    if subj_marks.empty:
        return pd.DataFrame()

    subj_marks.loc[:, "MarksObtained"] = pd.to_numeric(subj_marks["MarksObtained"], errors="coerce").fillna(0)
    subj_marks.loc[:, "EffMax"] = pd.to_numeric(subj_marks["EffMax"], errors="coerce").fillna(0)
    grouped = subj_marks.groupby(["StudentID", "COID"]).agg(Obtained=("MarksObtained", "sum"), Max=("EffMax", "sum")).reset_index()
    grouped["Percent"] = (grouped["Obtained"] / grouped["Max"].replace(0, pd.NA) * 100).fillna(0).round(2)

    # bring CO->PO mapping for subject
    mapping = co_po[co_po["_SubjectKey"] == subject_key]
    if mapping.empty:
        return pd.DataFrame()

    # mapping has COID, POID, Level (weight)
    mapping = mapping[["COID", "POID", "Level"]].copy()
    mapping["Level"] = pd.to_numeric(mapping["Level"], errors="coerce").fillna(1)

    # merge grouped with mapping to get PO contribution
    merged = grouped.merge(mapping, on="COID", how="inner")
    if merged.empty:
        return pd.DataFrame()

    # compute weighted percent per student per PO: Percent * Level
    merged["Weighted"] = merged["Percent"] * merged["Level"]

    # aggregate per student per PO: sum(weighted) / sum(levels)
    agg = merged.groupby(["StudentID", "POID"]).agg(
        WeightedSum=("Weighted", "sum"),
        LevelSum=("Level", "sum")
    ).reset_index()
    agg["POPercent"] = (agg["WeightedSum"] / agg["LevelSum"]).fillna(0).round(2)

    # pivot to students x PO
    pivot_po = agg.pivot(index="StudentID", columns="POID", values="POPercent").fillna(0)

    # compute attainment per PO
    results = []
    try:
        total_students = int(pivot_po.shape[0]) if 'pivot_po' in locals() and pivot_po.shape[0] > 0 else (
            len(students[students.get("Semester") == match.iloc[0].get("Semester")]) if "Semester" in match.iloc[0].index else len(students)
        )
    except Exception:
        total_students = len(students)
    po_list = mapping["POID"].unique()

    for po in po_list:
        if po in pivot_po.columns:
            percents = pivot_po[po]
        else:
            percents = pd.Series(0, index=pivot_po.index)
        num_reached = (percents >= pass_percent).sum()
        attainment_percent = round(num_reached / max(1, total_students) * 100, 2)
        avg_percent = round(percents.mean(), 2) if len(percents) > 0 else 0
        results.append({
            "POID": po,
            "Target": pass_percent,
            "Attainment%": attainment_percent,
            "Avg%": avg_percent,
            "NumReached": int(num_reached),
            "TotalStudents": int(total_students)
        })

    return pd.DataFrame(results)
