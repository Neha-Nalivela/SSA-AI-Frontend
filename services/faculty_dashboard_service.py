from models.data_manager import DataManager


def get_dashboard(reference_id):

    faculty = DataManager.get("faculty")
    subjects = DataManager.get("subjects")
    question_bank = DataManager.get("question_bank")
    faculty_row = faculty[
        faculty["FacultyID"] == reference_id
    ]
    if faculty_row.empty:
        return None
    faculty_data = faculty_row.iloc[0]
    # Temporary
    # Later we will filter only assigned subjects
    total_subjects = len(subjects)
    total_students = 0
    total_questions = len(question_bank)
    data = {
        "faculty": faculty_data,
        "total_subjects": total_subjects,
        "total_students": total_students,
        "total_questions": total_questions

    }

    return data