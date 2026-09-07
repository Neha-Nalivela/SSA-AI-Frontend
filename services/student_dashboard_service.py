import json
import re

import pandas as pd

from models.data_manager import DataManager

def get_dashboard(reference_id):

    # Load datasets
    students = DataManager.get("students")
    marks = DataManager.get("marks")
    attendance = DataManager.get("attendance")
    subjects = DataManager.get("subjects")
    question_bank = DataManager.get("question_bank")
    skills = DataManager.get("skills")
    interests = DataManager.get("interests")

    # ---------------------------------
    # Find logged-in student
    # ---------------------------------

    if students is None or students.empty:
        return None

    student_row = students[
        students["StudentID"].astype(str) == str(reference_id)
    ]

    if student_row.empty:
        return None

    student = student_row.iloc[0]

    # ---------------------------------
    # Student Marks
    # ---------------------------------

    if marks is not None and not marks.empty:

        student_marks = marks[
            marks["StudentID"].astype(str) == str(reference_id)
        ]

    else:

        student_marks = marks

    # ---------------------------------
    # Attendance
    # ---------------------------------

    if attendance is not None and not attendance.empty:

        student_attendance = attendance[
            attendance["StudentID"].astype(str) == str(reference_id)
        ]

    else:

        student_attendance = attendance

    # ---------------------------------
    # Calculate average marks
    # ---------------------------------

    average_marks = 0

    if (
        student_marks is not None
        and not student_marks.empty
        and {"ExamType", "MarksObtained"}.issubset(student_marks.columns)
    ):

        midterm_marks = student_marks[
            student_marks["ExamType"].astype(str).str.strip().isin(["Mid-1", "Mid-2"])
        ]

        average_marks = round(
            pd.to_numeric(
                midterm_marks["MarksObtained"],
                errors="coerce"
            ).mean(),
            2
        )

    # ---------------------------------
    # Calculate attendance percentage
    # ---------------------------------

    attendance_percentage = 0

    if student_attendance is not None and not student_attendance.empty:

        if {"ClassesConducted", "ClassesAttended"}.issubset(student_attendance.columns):

            total = pd.to_numeric(
                student_attendance["ClassesConducted"],
                errors="coerce"
            ).fillna(0).sum()
            present = pd.to_numeric(
                student_attendance["ClassesAttended"],
                errors="coerce"
            ).fillna(0).sum()

            if total > 0:
                attendance_percentage = round(
                    (present / total) * 100,
                    2
                )

        elif "Status" in student_attendance.columns:

            total = len(student_attendance)

            present = len(
                student_attendance[
                    student_attendance["Status"]
                    .astype(str)
                    .str.lower()
                    .isin(["present", "p", "1"])
                ]
            )

            if total > 0:
                attendance_percentage = round(
                    (present / total) * 100,
                    2
                )

    # Count active subjects for the student's department, year, and semester.
    total_subjects = 0
    if subjects is not None and not subjects.empty:
        student_subjects = subjects.copy()
        for column in ["Department", "Year", "Semester"]:
            if column in student_subjects.columns and column in student.index:
                expected = str(student[column]).strip()
                actual = student_subjects[column].astype(str).str.strip()
                try:
                    expected = str(int(float(expected)))
                    actual = pd.to_numeric(actual, errors="coerce").astype("Int64").astype(str)
                except (TypeError, ValueError):
                    pass
                student_subjects = student_subjects[actual == expected]
        if "Status" in student_subjects.columns:
            student_subjects = student_subjects[
                student_subjects["Status"].astype(str).str.strip().str.lower() == "active"
            ]
        total_subjects = student_subjects["SubjectID"].nunique() if "SubjectID" in student_subjects.columns else len(student_subjects)

    # ---------------------------------
    # Question Bank
    # ---------------------------------

    total_questions = 0

    if question_bank is not None and not question_bank.empty:

        total_questions = len(question_bank)

    # ---------------------------------
    # Skills
    # ---------------------------------

    total_skills = 0

    if skills is not None and not skills.empty:

        student_skills = skills[
            skills["StudentID"].astype(str)
            == str(reference_id)
        ]

        total_skills = len(student_skills)

    # ---------------------------------
    # Interests
    # ---------------------------------

    total_interests = 0

    if interests is not None and not interests.empty:

        student_interests = interests[
            interests["StudentID"].astype(str)
            == str(reference_id)
        ]

        total_interests = len(student_interests)

    # ---------------------------------
    # Dashboard Data
    # ---------------------------------

    performance = build_mapped_performance(reference_id, marks, DataManager.get("assessments"), question_bank, DataManager.get("co"), DataManager.get("co_po"))

    return {

        "student": student,

        "average_marks": average_marks,

        "attendance_percentage":
            attendance_percentage,

        "total_subjects":
            total_subjects,

        "total_questions":
            total_questions,

        "total_skills":
            total_skills,

        "total_interests":
            total_interests,

        "marks":
            student_marks,

        "attendance":
            student_attendance,

        "co_performance": performance["co"],
        "po_performance": performance["po"],
        "btl_performance": performance["btl"]

    }


def _key(value):
    match = re.search(r"(\d+)", str(value))
    return match.group(1) if match else str(value).strip().lower()


def _performance_rows(reference_id, marks, assessments, question_bank):
    """Return question-level scores for regular exams and completed assessments."""
    rows = []
    if marks is not None and not marks.empty and {"StudentID", "QuestionID", "MarksObtained", "MaxMarks"}.issubset(marks.columns):
        student_marks = marks[marks["StudentID"].astype(str).str.strip() == str(reference_id).strip()]
        metadata = question_bank.copy() if question_bank is not None else pd.DataFrame()
        if not metadata.empty and "QuestionID" in metadata.columns:
            metadata["QuestionID"] = metadata["QuestionID"].astype(str).str.strip()
            for _, mark in student_marks.iterrows():
                question = metadata[metadata["QuestionID"] == str(mark["QuestionID"]).strip()]
                if question.empty:
                    continue
                item = question.iloc[0].to_dict()
                item.update({"Obtained": mark["MarksObtained"], "Maximum": mark["MaxMarks"]})
                rows.append(item)

    if assessments is not None and not assessments.empty and "StudentID" in assessments.columns:
        student_assessments = assessments[
            (assessments["StudentID"].astype(str).str.strip() == str(reference_id).strip())
            & (assessments.get("Status", pd.Series(index=assessments.index, data="Completed")).astype(str).str.strip().str.lower().isin(["completed", "submitted"]))
        ]
        for _, assessment in student_assessments.iterrows():
            try:
                questions = json.loads(assessment.get("AssessmentQuestions", ""))
            except (TypeError, ValueError, json.JSONDecodeError):
                questions = []
            if not questions:
                continue
            assessment_max = float(pd.to_numeric(assessment.get("MaxMarks"), errors="coerce") or 0)
            assessment_obtained = float(pd.to_numeric(assessment.get("MarksObtained"), errors="coerce") or 0)
            question_max = sum(float(pd.to_numeric(item.get("MaxMarks"), errors="coerce") or 0) for item in questions)
            if not question_max:
                continue
            for item in questions:
                item = dict(item)
                maximum = float(pd.to_numeric(item.get("MaxMarks"), errors="coerce") or 0)
                item.update({"Obtained": assessment_obtained * maximum / question_max, "Maximum": maximum})
                rows.append(item)
    return pd.DataFrame(rows)


def build_mapped_performance(reference_id, marks, assessments, question_bank, cos, co_po):
    rows = _performance_rows(reference_id, marks, assessments, question_bank)
    empty = {"co": [], "po": [], "btl": []}
    if rows.empty or "COID" not in rows.columns:
        return empty
    rows["Obtained"] = pd.to_numeric(rows["Obtained"], errors="coerce").fillna(0)
    rows["Maximum"] = pd.to_numeric(rows["Maximum"], errors="coerce").fillna(0)
    rows = rows[rows["Maximum"] > 0].copy()
    if rows.empty:
        return empty

    def summarise(column, label_column=None):
        if column not in rows.columns:
            return []
        grouped = rows.groupby(column).agg(obtained=("Obtained", "sum"), maximum=("Maximum", "sum")).reset_index()
        result = []
        for _, item in grouped.iterrows():
            name = str(item[column]).strip()
            if not name or name.lower() == "nan":
                continue
            result.append({"id": name, "name": name, "percentage": round(float(item.obtained / item.maximum * 100), 2)})
        return sorted(result, key=lambda item: item["id"])

    co_result = summarise("COID")
    btl_result = summarise("BTL")
    po_result = []
    if co_po is not None and not co_po.empty:
        co_scores = {item["id"]: item["percentage"] for item in co_result}
        mapping = co_po.copy()
        mapping["COKey"] = mapping["COID"].astype(str).str.strip()
        mapping["POKey"] = mapping["POID"].apply(_key)
        mapped = []
        for _, item in mapping.iterrows():
            score = co_scores.get(item["COKey"])
            if score is not None:
                mapped.append((item["POKey"], str(item["POID"]).strip(), score, float(item.get("Level", 1) or 1)))
        for po_key in sorted({item[0] for item in mapped}):
            values = [item for item in mapped if item[0] == po_key]
            weight = sum(item[3] for item in values) or 1
            po_result.append({"id": values[0][1], "name": values[0][1], "percentage": round(sum(item[2] * item[3] for item in values) / weight, 2)})
    return {"co": co_result, "po": po_result, "btl": btl_result}