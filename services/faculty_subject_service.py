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


def _normalize_subject_keys(subjects, marks):
    import re

    def numeric_key(value):
        value = str(value)
        match = re.search(r"(\d+)", value)
        return match.group(1) if match else value.strip()

    subjects["SubjectID"] = subjects["SubjectID"].astype(str).str.strip()
    subjects["FacultyID"] = subjects["FacultyID"].astype(str).str.strip()
    marks["SubjectID"] = marks["SubjectID"].astype(str).str.strip()

    subjects["_SubjectKey"] = subjects["SubjectID"].apply(numeric_key)
    marks["_SubjectKey"] = marks["SubjectID"].apply(numeric_key)

    return subjects, marks


def _resolve_subject_and_marks(reference_id, subject_id, exam_types):
    subjects = DataManager.get("subjects")
    marks = DataManager.get("marks")

    if subjects is None or marks is None:
        DataManager.refresh()
        subjects = DataManager.get("subjects")
        marks = DataManager.get("marks")

    subjects, marks = _normalize_subject_keys(subjects, marks)

    reference_id = str(reference_id).strip()
    subject_key = str(subject_id).strip()
    import re
    match = re.search(r"(\d+)", subject_key)
    subject_key = match.group(1) if match else subject_key

    subject_match = subjects[
        (subjects["_SubjectKey"] == subject_key) &
        (subjects["FacultyID"] == reference_id)
    ]

    if subject_match.empty:
        return None, marks.iloc[0:0]

    subject = subject_match.iloc[0]
    filtered = marks[
        (marks["_SubjectKey"] == subject_key) &
        (marks["ExamType"].isin(exam_types))
    ]

    return subject, filtered


def _build_student_summary(subject, marks, exam_labels):
    if subject is None:
        return None, marks

    students = DataManager.get("students")
    students["StudentID"] = students["StudentID"].astype(str).str.strip()

    student_summary = marks.groupby(["StudentID", "ExamType"]).size().unstack(fill_value=0)
    student_summary = student_summary.reset_index()

    for label in exam_labels:
        student_summary[label] = student_summary.get(label, 0)

    summary_total = sum(student_summary[label] for label in exam_labels)
    student_summary["Total"] = summary_total

    student_summary = student_summary.merge(
        students[["StudentID", "Name"]],
        on="StudentID",
        how="left"
    )

    order_cols = ["Total", "StudentID"]
    return subject, student_summary.sort_values(order_cols, ascending=[False, True])


def get_subject_internal_mark_students(reference_id, subject_id):
    subject, internal_marks = _resolve_subject_and_marks(
        reference_id,
        subject_id,
        ["Mid-1", "Mid-2"]
    )

    return _build_student_summary(subject, internal_marks, ["Mid-1", "Mid-2"])


def get_internal_marks_for_student(reference_id, subject_id, student_id):
    subject, internal_marks = _resolve_subject_and_marks(
        reference_id,
        subject_id,
        ["Mid-1", "Mid-2"]
    )

    if subject is None:
        return None, internal_marks.iloc[0:0]

    student_id = str(student_id).strip()
    student_marks = internal_marks[internal_marks["StudentID"] == student_id]

    return subject, student_marks


def get_subject_external_mark_students(reference_id, subject_id):
    subject, external_marks = _resolve_subject_and_marks(
        reference_id,
        subject_id,
        ["End Semester"]
    )

    return _build_student_summary(subject, external_marks, ["End Semester"])


def get_external_marks_for_student(reference_id, subject_id, student_id):
    subject, external_marks = _resolve_subject_and_marks(
        reference_id,
        subject_id,
        ["End Semester"]
    )

    if subject is None:
        return None, external_marks.iloc[0:0]

    student_id = str(student_id).strip()
    student_marks = external_marks[external_marks["StudentID"] == student_id]

    return subject, student_marks