import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

from models.data_manager import DataManager
from services.assessment_service import AssessmentService


def build_subject_performance_summary(marks_df):
    if marks_df is None or marks_df.empty:
        return []

    data = marks_df.copy()
    required = {"SubjectID", "ExamType", "MarksObtained", "MaxMarks"}
    if not required.issubset(data.columns):
        return []

    data["MarksObtained"] = pd.to_numeric(data["MarksObtained"], errors="coerce")
    data["MaxMarks"] = pd.to_numeric(data["MaxMarks"], errors="coerce")
    data = data.dropna(subset=["MarksObtained", "MaxMarks"]) 

    if data.empty:
        return []

    grouped = data.groupby("SubjectID", as_index=False).agg(
        total_obtained=("MarksObtained", "sum"),
        total_max=("MaxMarks", "sum")
    )

    summary = []
    exam_order = ["Mid-1", "Mid-2", "End Semester"]

    for _, row in grouped.iterrows():
        subject_id = str(row["SubjectID"])
        subject_marks = data[data["SubjectID"].astype(str) == subject_id].copy()

        exam_values = {}
        for exam in exam_order:
            exam_rows = subject_marks[subject_marks["ExamType"].astype(str).str.strip() == exam]
            if exam_rows.empty:
                exam_values[exam] = 0.0
                continue
            exam_total = float(exam_rows["MarksObtained"].sum())
            exam_max = float(exam_rows["MaxMarks"].sum())
            exam_values[exam] = float(
                (Decimal(str(exam_total)) / Decimal(str(exam_max)) * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            ) if exam_max else 0.0

            total_percent = float(
                (Decimal(str(row["total_obtained"])) / Decimal(str(row["total_max"])) * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            ) if float(row["total_max"]) else 0.0

            cgpa = float((Decimal(str(total_percent)) / Decimal('10')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        summary.append({
            "SubjectID": subject_id,
            "Mid-1": exam_values.get("Mid-1", 0.0),
            "Mid-2": exam_values.get("Mid-2", 0.0),
            "End Semester": exam_values.get("End Semester", 0.0),
            "OverallPercent": total_percent,
            "CGPA": cgpa,
        })

    return sorted(summary, key=lambda x: x["SubjectID"])


def get_student(reference_id):

    students = DataManager.get("students")

    if students is None or students.empty:
        return None

    if "StudentID" not in students.columns:
        return None

    student_rows = students[
        students["StudentID"].astype(str)
        == str(reference_id)
    ]

    if student_rows.empty:
        return None

    return student_rows.iloc[0]

def get_student_marks(reference_id):

    marks = DataManager.get("marks")

    if marks is None or marks.empty:
        return pd.DataFrame()

    if "StudentID" not in marks.columns:
        return pd.DataFrame()

    return marks[
        marks["StudentID"].astype(str)
        == str(reference_id)
    ].copy()


def get_performance(reference_id):
    student = get_student(reference_id)
    marks = get_student_marks(reference_id)

    average = 0
    highest = 0
    lowest = 0

    if not marks.empty:

        if "MarksObtained" in marks.columns:

            values = pd.to_numeric(
                marks["MarksObtained"],
                errors="coerce"
            ).dropna()

            if not values.empty:

                average = round(
                    values.mean(),
                    2
                )

                highest = values.max()

                lowest = values.min()

    overall_cgpa = 0
    if not marks.empty and "MarksObtained" in marks.columns and "MaxMarks" in marks.columns:
        scores = pd.to_numeric(marks["MarksObtained"], errors="coerce")
        max_scores = pd.to_numeric(marks["MaxMarks"], errors="coerce")
        valid = pd.concat([scores, max_scores], axis=1).dropna()
        if not valid.empty:
            total_percent = (valid["MarksObtained"].sum() / valid["MaxMarks"].sum()) * 100 if valid["MaxMarks"].sum() else 0
            overall_cgpa = float((Decimal(str(total_percent)) / Decimal('10')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    subject_summary = build_subject_performance_summary(marks)

    return {

        # Student information
        "student": student,

        # Marks
        "marks": marks,
        "subject_summary": subject_summary,

        # Overall statistics
        "average": average,
        "highest": highest,
        "lowest": lowest,
        "cgpa": overall_cgpa,

    }

def get_analytics(reference_id):

    marks = get_student_marks(reference_id)

    subject_summary = []

    if not marks.empty:

        if (
            "SubjectID" in marks.columns
            and "MarksObtained" in marks.columns
        ):

            marks["MarksObtained"] = pd.to_numeric(
                marks["MarksObtained"],
                errors="coerce"
            )

            marks = marks.dropna(
                subset=["MarksObtained"]
            )

            grouped = (
                marks.groupby("SubjectID")["MarksObtained"]
                .mean()
            )

            for subject_id, value in grouped.items():

                subject_summary.append({

                    "SubjectID": str(subject_id),

                    "Average": round(
                        float(value),
                        2
                    )

                })

    return {

        "marks": marks,

        "subject_summary": subject_summary

    }