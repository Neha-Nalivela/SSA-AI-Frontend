import pandas as pd

from models.data_manager import DataManager

def get_dashboard(reference_id):

    # Load datasets
    students = DataManager.get("students")
    marks = DataManager.get("marks")
    attendance = DataManager.get("attendance")
    subjects = DataManager.get("subjects")
    question_bank = DataManager.get("question_bank")
    skills = DataManager.get("skills")
    interests = DataManager.get("interests")

    # ---------------------------------
    # Find logged-in student
    # ---------------------------------

    if students is None or students.empty:
        return None

    student_row = students[
        students["StudentID"].astype(str) == str(reference_id)
    ]

    if student_row.empty:
        return None

    student = student_row.iloc[0]

    # ---------------------------------
    # Student Marks
    # ---------------------------------

    if marks is not None and not marks.empty:

        student_marks = marks[
            marks["StudentID"].astype(str) == str(reference_id)
        ]

    else:

        student_marks = marks

    # ---------------------------------
    # Attendance
    # ---------------------------------

    if attendance is not None and not attendance.empty:

        student_attendance = attendance[
            attendance["StudentID"].astype(str) == str(reference_id)
        ]

    else:

        student_attendance = attendance

    # ---------------------------------
    # Calculate average marks
    # ---------------------------------

    average_marks = 0

    if (
        student_marks is not None
        and not student_marks.empty
        and "MarksObtained" in student_marks.columns
    ):

        average_marks = round(
            pd.to_numeric(
                student_marks["MarksObtained"],
                errors="coerce"
            ).mean(),
            2
        )

    # ---------------------------------
    # Calculate attendance percentage
    # ---------------------------------

    attendance_percentage = 0

    if student_attendance is not None and not student_attendance.empty:

        if "Status" in student_attendance.columns:

            total = len(student_attendance)

            present = len(
                student_attendance[
                    student_attendance["Status"]
                    .astype(str)
                    .str.lower()
                    .isin(["present", "p", "1"])
                ]
            )

            if total > 0:
                attendance_percentage = round(
                    (present / total) * 100,
                    2
                )

    # ---------------------------------
    # Total subjects
    # ---------------------------------

    total_subjects = 0

    if subjects is not None and not subjects.empty:

        if "Semester" in subjects.columns and "Semester" in student.index:

            student_semester = student["Semester"]

            student_subjects = subjects[
                subjects["Semester"].astype(str)
                == str(student_semester)
            ]

            total_subjects = len(student_subjects)

        else:

            total_subjects = len(subjects)

    # ---------------------------------
    # Question Bank
    # ---------------------------------

    total_questions = 0

    if question_bank is not None and not question_bank.empty:

        total_questions = len(question_bank)

    # ---------------------------------
    # Skills
    # ---------------------------------

    total_skills = 0

    if skills is not None and not skills.empty:

        student_skills = skills[
            skills["StudentID"].astype(str)
            == str(reference_id)
        ]

        total_skills = len(student_skills)

    # ---------------------------------
    # Interests
    # ---------------------------------

    total_interests = 0

    if interests is not None and not interests.empty:

        student_interests = interests[
            interests["StudentID"].astype(str)
            == str(reference_id)
        ]

        total_interests = len(student_interests)

    # ---------------------------------
    # Dashboard Data
    # ---------------------------------

    return {

        "student": student,

        "average_marks": average_marks,

        "attendance_percentage":
            attendance_percentage,

        "total_subjects":
            total_subjects,

        "total_questions":
            total_questions,

        "total_skills":
            total_skills,

        "total_interests":
            total_interests,

        "marks":
            student_marks,

        "attendance":
            student_attendance

    }