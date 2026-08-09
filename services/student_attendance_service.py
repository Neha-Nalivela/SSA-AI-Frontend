from models.data_manager import DataManager


def get_attendance(reference_id):

    attendance = DataManager.get("attendance")

    if attendance is None or attendance.empty:
        return attendance

    if "StudentID" not in attendance.columns:
        return attendance.iloc[0:0]

    return attendance[
        attendance["StudentID"].astype(str)
        == str(reference_id)
    ]