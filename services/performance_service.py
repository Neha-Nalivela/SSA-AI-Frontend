import os
import re

import pandas as pd

from models.data_manager import DataManager

try:
    from config import ACADEMIC_FOLDER
except Exception:  # pragma: no cover
    ACADEMIC_FOLDER = os.path.join(os.getcwd(), "data", "academic")


def _numeric_key(value):
    value = str(value)
    match = re.search(r"(\d+)", value)
    return match.group(1) if match else value.strip()


def _normalize_subject_key(df, column="SubjectID"):
    df = df.copy()
    df[column] = df[column].astype(str).str.strip()
    df["_SubjectKey"] = df[column].apply(_numeric_key)
    return df


def save_remedial_action(subject_id, student_id, category, remedial_classes, assessment, youtube_link, notes):
    file_path = os.path.join(ACADEMIC_FOLDER, "18_RemedialClasses.xlsx")
    os.makedirs(ACADEMIC_FOLDER, exist_ok=True)

    if os.path.exists(file_path):
        try:
            existing = pd.read_excel(file_path)
        except Exception:
            existing = pd.DataFrame()
    else:
        existing = pd.DataFrame()

    new_row = pd.DataFrame([{
        "SubjectID": str(subject_id).strip(),
        "StudentID": str(student_id).strip(),
        "Category": str(category).strip(),
        "RemedialClasses": str(remedial_classes).strip(),
        "Assessment": str(assessment).strip(),
        "YouTubeLink": str(youtube_link).strip(),
        "Notes": str(notes).strip(),
    }])

    if existing.empty:
        combined = new_row
    else:
        combined = pd.concat([existing, new_row], ignore_index=True)

    combined.to_excel(file_path, index=False)
    return new_row.iloc[0].to_dict()


def get_remedial_actions(subject_id=None):
    file_path = os.path.join(ACADEMIC_FOLDER, "18_RemedialClasses.xlsx")
    if not os.path.exists(file_path):
        return []

    try:
        actions = pd.read_excel(file_path)
    except Exception:
        return []

    if actions.empty:
        return []

    if subject_id is not None:
        actions = actions[actions["SubjectID"].astype(str).str.strip() == str(subject_id).strip()]

    return actions.to_dict(orient="records")


def _build_remedial_recommendation(student_percent, category, subject_name, subject_id=None):
    subject_label = str(subject_name).strip() or "subject"
    subject_key = str(subject_id).strip()
    query_parts = [subject_label]

    # use CO/PO and BTL context if available in the workbook
    co_info = []
    po_info = []
    btl_info = []

    try:
        cos = DataManager.get("co")
        if cos is not None and not cos.empty:
            cos = cos.copy()
            cos["SubjectID"] = cos["SubjectID"].astype(str).str.strip()
            cos["_SubjectKey"] = cos["SubjectID"].apply(_numeric_key)
            subject_cos = cos[cos["_SubjectKey"] == _numeric_key(subject_key)]
            if not subject_cos.empty:
                co_info = subject_cos["COID"].astype(str).tolist()[:2]
                query_parts.extend(co_info)
    except Exception:
        co_info = []

    try:
        pos = DataManager.get("po")
        if pos is not None and not pos.empty:
            pos = pos.copy()
            pos["POID"] = pos["POID"].astype(str).str.strip()
            if not pos.empty:
                po_info = pos["POID"].astype(str).tolist()[:2]
                query_parts.extend(po_info)
    except Exception:
        po_info = []

    try:
        mapping = DataManager.get("co_po")
        if mapping is not None and not mapping.empty:
            mapping = mapping.copy()
            mapping["SubjectID"] = mapping["SubjectID"].astype(str).str.strip()
            mapping["_SubjectKey"] = mapping["SubjectID"].apply(_numeric_key)
            subject_mapping = mapping[mapping["_SubjectKey"] == _numeric_key(subject_key)]
            if not subject_mapping.empty:
                btl_values = subject_mapping.get("BTL", [])
                if len(btl_values):
                    btl_info = [str(v) for v in btl_values.dropna().tolist()[:2]]
                    query_parts.extend(btl_info)
    except Exception:
        btl_info = []

    query = " ".join([p for p in query_parts if str(p).strip()])
    youtube_link = "https://www.youtube.com/results?search_query=" + query.replace(" ", "+")

    if category == "Weak":
        remedial_classes = "Daily revision and doubt-clearing sessions"
        assessment = "Short quiz on weak topics"
        notes = "Focus on foundational concepts and repeated practice."
    else:
        remedial_classes = "Weekly practice and concept reinforcement"
        assessment = "Topic-wise assignment and oral test"
        notes = "Improve consistency and strengthen moderate-level topics."

    if student_percent < 30:
        remedial_classes = "Intensive remedial coaching and one-to-one doubt sessions"
        assessment = "Diagnostic test followed by retest"
    elif student_percent < 40 and category == "Weak":
        remedial_classes = "Focused revision classes on core concepts"
        assessment = "Mini test on important topics"

    return {
        "RemedialClasses": remedial_classes,
        "Assessment": assessment,
        "YouTubeLink": youtube_link,
        "Notes": notes,
    }


def get_subject_performance_analysis(reference_id, subject_id):
    subjects = DataManager.get("subjects")
    students = DataManager.get("students")
    marks = DataManager.get("marks")
    question_bank = DataManager.get("question_bank")

    if any(df is None for df in [subjects, students, marks, question_bank]):
        DataManager.refresh()
        subjects = DataManager.get("subjects")
        students = DataManager.get("students")
        marks = DataManager.get("marks")
        question_bank = DataManager.get("question_bank")

    subjects = subjects.copy()
    students = students.copy()
    marks = marks.copy()
    question_bank = question_bank.copy()

    subjects = _normalize_subject_key(subjects, "SubjectID")
    marks = _normalize_subject_key(marks, "SubjectID")
    question_bank = _normalize_subject_key(question_bank, "SubjectID")
    students["StudentID"] = students["StudentID"].astype(str).str.strip()

    subject_key = _numeric_key(subject_id)
    reference_id = str(reference_id).strip()

    subject_match = subjects[(subjects["_SubjectKey"] == subject_key) & (subjects.get("FacultyID", "") == reference_id)]
    if subject_match.empty:
        return None, {}

    subject = subject_match.iloc[0]
    subj_marks = marks[marks["_SubjectKey"] == subject_key].copy()
    if subj_marks.empty:
        return subject, {
            "weak_students": [],
            "avg_students": [],
            "top_students": [],
            "lagging_subjects": []
        }

    subj_marks["MarksObtained"] = pd.to_numeric(subj_marks["MarksObtained"], errors="coerce").fillna(0)
    subj_marks["MaxMarks"] = pd.to_numeric(subj_marks["MaxMarks"], errors="coerce").fillna(0)
    subj_marks["Percent"] = (subj_marks["MarksObtained"] / subj_marks["MaxMarks"].replace(0, pd.NA) * 100).fillna(0)

    student_totals = subj_marks.groupby("StudentID").agg(
        TotalObtained=("MarksObtained", "sum"),
        TotalMax=("MaxMarks", "sum"),
        AvgPercent=("Percent", "mean")
    ).reset_index()
    student_totals["AvgPercent"] = student_totals["AvgPercent"].round(2)
    student_totals["OverallPercent"] = (student_totals["TotalObtained"] / student_totals["TotalMax"].replace(0, pd.NA) * 100).fillna(0).round(2)

    students_map = students.copy()
    students_map["StudentID"] = students_map["StudentID"].astype(str).str.strip()
    student_totals = student_totals.merge(
        students_map[["StudentID", "Name"]],
        on="StudentID",
        how="left"
    ).rename(columns={"Name": "StudentName"})

    # classify by overall percent
    weak_threshold = 40
    avg_threshold = 70
    weak = student_totals[student_totals["OverallPercent"] < weak_threshold]
    avg = student_totals[(student_totals["OverallPercent"] >= weak_threshold) & (student_totals["OverallPercent"] < avg_threshold)]
    top = student_totals[student_totals["OverallPercent"] >= avg_threshold]

    def select_students(df, reverse=False):
        order = ["OverallPercent", "StudentID"]
        ascending = [not reverse, True]
        df = df.sort_values(order, ascending=ascending)
        return df.head(5)[["StudentID", "StudentName", "OverallPercent"]].to_dict(orient="records")

    weak_students = select_students(weak)
    avg_students = select_students(avg)
    top_students = select_students(top, reverse=True)

    # lagging subjects uses all marks across subjects per student
    all_marks = marks.copy()
    all_marks["MarksObtained"] = pd.to_numeric(all_marks["MarksObtained"], errors="coerce").fillna(0)
    all_marks["MaxMarks"] = pd.to_numeric(all_marks["MaxMarks"], errors="coerce").fillna(0)
    all_marks["Percent"] = (all_marks["MarksObtained"] / all_marks["MaxMarks"].replace(0, pd.NA) * 100).fillna(0)

    subject_avgs = all_marks.groupby(["_SubjectKey"]).agg(
        SubjectPercent=("Percent", "mean")
    ).reset_index()
    subject_avgs["SubjectPercent"] = subject_avgs["SubjectPercent"].round(2)

    # compute per-student per-subject percent and compare to subject average
    student_subject = all_marks.groupby(["StudentID", "_SubjectKey"]).agg(
        StudentPercent=("Percent", "mean")
    ).reset_index()
    merged = student_subject.merge(subject_avgs, on="_SubjectKey", how="left")
    merged["Lag"] = merged["StudentPercent"] - merged["SubjectPercent"]
    lagging = merged[merged["Lag"] < 0].copy()
    lagging = lagging.sort_values(["Lag", "StudentID"], ascending=[True, True])

    # join subject names for display
    subject_name_map = subjects.set_index("_SubjectKey")["SubjectName"].to_dict()
    lagging["SubjectName"] = lagging["_SubjectKey"].map(subject_name_map)
    lagging = lagging[lagging["SubjectName"].notna()]

    lagging_rows = lagging.head(10)[["StudentID", "SubjectName", "StudentPercent", "SubjectPercent", "Lag"]].to_dict(orient="records")

    remedial_actions = get_remedial_actions(subject_id)
    action_map = {}
    for action in remedial_actions:
        action_map[(str(action.get("SubjectID", "")).strip(), str(action.get("StudentID", "")).strip())] = action

    for student_group in [weak_students, avg_students]:
        for student in student_group:
            student_id = str(student.get("StudentID", "")).strip()
            existing_action = action_map.get((str(subject_id).strip(), student_id), {})
            if existing_action:
                student["RemedialAction"] = existing_action
            else:
                category = "Weak" if student in weak_students else "Average"
                student_percent = float(student.get("OverallPercent", 0) or 0)
                student["RemedialAction"] = _build_remedial_recommendation(
                    student_percent,
                    category,
                    subject.get("SubjectName", ""),
                    subject_id=subject_id,
                )

    return subject, {
        "weak_students": weak_students,
        "avg_students": avg_students,
        "top_students": top_students,
        "lagging_subjects": lagging_rows,
        "remedial_actions": remedial_actions
    }
