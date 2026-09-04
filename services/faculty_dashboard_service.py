from models.data_manager import DataManager


def get_dashboard(reference_id):

    faculty = DataManager.get("faculty")
    subjects = DataManager.get("subjects")
    question_bank = DataManager.get("question_bank")
    marks = DataManager.get("marks")
    faculty_row = faculty[
        faculty["FacultyID"].astype(str).str.strip() == str(reference_id).strip()
    ]
    if faculty_row.empty:
        return None
    faculty_data = faculty_row.iloc[0]
    assigned_subjects = subjects[
        subjects["FacultyID"].astype(str).str.strip() == str(reference_id).strip()
    ].copy()
    assigned_keys = assigned_subjects["SubjectID"].astype(str).str.extract(
        r"(\d+)", expand=False
    ).fillna(assigned_subjects["SubjectID"].astype(str).str.strip())

    total_subjects = len(assigned_subjects)
    total_students = 0
    if marks is not None and not marks.empty and "SubjectID" in marks.columns and "StudentID" in marks.columns:
        mark_keys = marks["SubjectID"].astype(str).str.extract(r"(\d+)", expand=False).fillna(
            marks["SubjectID"].astype(str).str.strip()
        )
        total_students = marks.loc[mark_keys.isin(set(assigned_keys)), "StudentID"].astype(str).str.strip().nunique()

    total_questions = 0
    if question_bank is not None and not question_bank.empty and "SubjectID" in question_bank.columns:
        question_keys = question_bank["SubjectID"].astype(str).str.extract(r"(\d+)", expand=False).fillna(
            question_bank["SubjectID"].astype(str).str.strip()
        )
        total_questions = int(question_keys.isin(set(assigned_keys)).sum())
    data = {
        "faculty": faculty_data,
        "total_subjects": total_subjects,
        "total_students": total_students,
        "total_questions": total_questions

    }

    return data