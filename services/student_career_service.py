from models.data_manager import DataManager


def get_career_recommendations(reference_id):

    career = DataManager.get("career")

    students = DataManager.get("students")

    student = None

    if (
        students is not None
        and not students.empty
        and "StudentID" in students.columns
    ):

        row = students[
            students["StudentID"].astype(str)
            == str(reference_id)
        ]

        if not row.empty:
            student = row.iloc[0]

    return {
        "student": student,
        "career": career
    }