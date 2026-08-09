from models.data_manager import DataManager


def get_profile(reference_id):

    students = DataManager.get("students")

    if students is None or students.empty:
        return None

    if "StudentID" not in students.columns:
        return None

    row = students[
        students["StudentID"].astype(str)
        == str(reference_id)
    ]

    if row.empty:
        return None

    return row.iloc[0]