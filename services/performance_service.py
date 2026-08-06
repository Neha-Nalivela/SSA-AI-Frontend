from models.data_manager import DataManager
import pandas as pd
import re


def _numeric_key(value):
    value = str(value)
    match = re.search(r"(\d+)", value)
    return match.group(1) if match else value.strip()


def _normalize_subject_key(df, column="SubjectID"):
    df = df.copy()
    df[column] = df[column].astype(str).str.strip()
    df["_SubjectKey"] = df[column].apply(_numeric_key)
    return df


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

    return subject, {
        "weak_students": weak_students,
        "avg_students": avg_students,
        "top_students": top_students,
        "lagging_subjects": lagging_rows
    }
