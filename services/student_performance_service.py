import pandas as pd

from models.data_manager import DataManager


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