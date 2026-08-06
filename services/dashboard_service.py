from models.data_manager import DataManager
def get_dashboard_summary():
    students = DataManager.get("students")
    faculty = DataManager.get("faculty")
    subjects = DataManager.get("subjects")
    users = DataManager.get("users")

    return {
        "total_students": len(students),
        "total_faculty": len(faculty),
        "total_subjects": len(subjects),
        "active_users": len(users[users["Status"] == "Active"])
    }