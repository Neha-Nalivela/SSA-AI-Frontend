import pandas as pd

from models.data_manager import DataManager
def get_ai_recommendations(reference_id):

    students = DataManager.get("students")
    marks = DataManager.get("marks")
    attendance = DataManager.get("attendance")
    recommendations = DataManager.get("recommendations")
    resources = DataManager.get("resources")
    remedial = DataManager.get("remedial")

    result = {
        "weak_subjects": [],
        "recommendations": [],
        "resources": [],
        "remedial_classes": []
    }

    if students is None or students.empty:
        return result

    student = students[
        students["StudentID"].astype(str) == str(reference_id)
    ]

    if student.empty:
        return result

    # ---------------------------------
    # Student Marks Analysis
    # ---------------------------------

    if marks is not None and not marks.empty:

        student_marks = marks[
            marks["StudentID"].astype(str) == str(reference_id)
        ].copy()

        if not student_marks.empty:

            # Identify weak subjects
            if "MarksObtained" in student_marks.columns:

                weak_marks = student_marks[
                    student_marks["MarksObtained"] < 50
                ]

                for _, row in weak_marks.iterrows():

                    result["weak_subjects"].append({
                        "subject_id": row.get("SubjectID", ""),
                        "marks": row.get("MarksObtained", 0)
                    })

    # ---------------------------------
    # Existing AI Recommendations
    # ---------------------------------

    if recommendations is not None and not recommendations.empty:

        if "StudentID" in recommendations.columns:

            student_recommendations = recommendations[
                recommendations["StudentID"].astype(str)
                == str(reference_id)
            ]

            result["recommendations"] = (
                student_recommendations.to_dict("records")
            )

    # ---------------------------------
    # Learning Resources
    # ---------------------------------

    if resources is not None and not resources.empty:

        result["resources"] = resources.to_dict("records")

    # ---------------------------------
    # Remedial Classes
    # ---------------------------------

    if remedial is not None and not remedial.empty:

        if "StudentID" in remedial.columns:

            student_remedial = remedial[
                remedial["StudentID"].astype(str)
                == str(reference_id)
            ]

            result["remedial_classes"] = (
                student_remedial.to_dict("records")
            )

    return result

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

    return {
        "marks": marks,
        "average": average,
        "highest": highest,
        "lowest": lowest
    }


def get_analytics(reference_id):

    marks = get_student_marks(reference_id)

    subject_summary = []

    if not marks.empty:

        if (
            "SubjectID" in marks.columns
            and "MarksObtained" in marks.columns
        ):

            grouped = marks.groupby(
                "SubjectID"
            )["MarksObtained"].mean()

            for subject_id, value in grouped.items():

                subject_summary.append({
                    "SubjectID": subject_id,
                    "Average": round(
                        float(value),
                        2
                    )
                })

    return {
        "marks": marks,
        "subject_summary": subject_summary
    }