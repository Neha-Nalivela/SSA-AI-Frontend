from models.data_manager import DataManager

def get_faculty_subjects(reference_id):

    subjects = DataManager.get("subjects")

    subjects["FacultyID"] = subjects["FacultyID"].astype(str).str.strip()

    reference_id = str(reference_id).strip()

    return subjects[
        subjects["FacultyID"] == reference_id
    ]

def get_subject_dashboard(reference_id, subject_id):
    subjects = DataManager.get("subjects")
    students = DataManager.get("students")
    question_bank = DataManager.get("question_bank")
    attendance = DataManager.get("attendance")
    student_marks = DataManager.get("marks")
    subject = subjects[
        subjects["SubjectID"] == subject_id
    ].iloc[0]
    total_students = len(
        students[
            students["Semester"] == subject["Semester"]
        ]
    )
    total_questions = len(
        question_bank[
            question_bank["SubjectID"] == subject_id
        ]
    )
    attendance_records = len(
        attendance[
            attendance["SubjectID"] == subject_id
        ]
    )
    marks = student_marks[
        student_marks["SubjectID"] == subject_id
    ]
    average_marks = 0
    if not marks.empty:
        average_marks = round(
            marks["MarksObtained"].mean(),
            2
        )
    return {
        "subject": subject,
        "total_students": total_students,
        "total_questions": total_questions,
        "attendance_records": attendance_records,
        "average_marks": average_marks
    }