import pandas as pd

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
    # normalize keys for subject matching (handles S001 vs SUB001 etc.)
    subjects, student_marks = _normalize_subject_keys(subjects, student_marks)
    question_bank = question_bank.copy()
    question_bank["SubjectID"] = question_bank["SubjectID"].astype(str).str.strip()
    question_bank["_SubjectKey"] = question_bank["SubjectID"].apply(lambda v: str(v)
                                                                    and __import__('re').search(r"(\d+)", str(v)).group(1) if __import__('re').search(r"(\d+)", str(v)) else str(v).strip())

    attendance = attendance.copy()
    attendance["SubjectID"] = attendance["SubjectID"].astype(str).str.strip()
    attendance["_SubjectKey"] = attendance["SubjectID"].apply(lambda v: str(v)
                                                                  and __import__('re').search(r"(\d+)", str(v)).group(1) if __import__('re').search(r"(\d+)", str(v)) else str(v).strip())

    subject = subjects[subjects["SubjectID"] == subject_id].iloc[0]
    # numeric key for comparisons
    import re
    match = re.search(r"(\d+)", str(subject_id).strip())
    subject_key = match.group(1) if match else str(subject_id).strip()

    # filter marks/questions/attendance by normalized subject key
    filtered_marks = student_marks[student_marks["_SubjectKey"] == subject_key]
    if not filtered_marks.empty:
        total_students = filtered_marks["StudentID"].astype(str).str.strip().nunique()
    else:
        total_students = len(students[students["Semester"] == subject["Semester"]])

    total_questions = len(question_bank[question_bank["_SubjectKey"] == subject_key])
    attendance_records = len(attendance[attendance["_SubjectKey"] == subject_key])
    marks = filtered_marks
    average_marks = 0
    if not marks.empty:
        average_marks = round(marks["MarksObtained"].mean(), 2)
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
    if students is None:
        students = pd.DataFrame(columns=["StudentID", "Name"])

    students = students.copy()
    students["StudentID"] = students["StudentID"].astype(str).str.strip()

    marks = marks.copy()
    marks["StudentID"] = marks["StudentID"].astype(str).str.strip()
    marks["ExamType"] = marks["ExamType"].astype(str).str.strip()
    marks["MarksObtained"] = pd.to_numeric(marks.get("MarksObtained"), errors="coerce").fillna(0)

    if marks.empty:
        student_summary = pd.DataFrame(columns=["StudentID", *exam_labels, "Total", "Average", "Name"])
        student_summary = student_summary.merge(students[["StudentID", "Name"]], on="StudentID", how="outer")
        for label in exam_labels:
            student_summary[label] = pd.to_numeric(student_summary.get(label), errors="coerce").fillna(0)
        student_summary["Total"] = student_summary[exam_labels].sum(axis=1)
        student_summary["Average"] = student_summary[exam_labels].mean(axis=1)
        return subject, student_summary.sort_values(["Total", "StudentID"], ascending=[False, True]).reset_index(drop=True)

    aggregated = marks.groupby(["StudentID", "ExamType"], as_index=False)["MarksObtained"].sum()
    student_summary = aggregated.pivot(index="StudentID", columns="ExamType", values="MarksObtained").fillna(0).reset_index()

    for label in exam_labels:
        student_summary[label] = pd.to_numeric(student_summary.get(label), errors="coerce").fillna(0)

    student_summary["Total"] = student_summary[exam_labels].sum(axis=1)
    student_summary["Average"] = student_summary[exam_labels].mean(axis=1)

    student_summary = student_summary.merge(
        students[["StudentID", "Name"]],
        on="StudentID",
        how="left"
    )
    student_summary["Name"] = student_summary["Name"].fillna("")

    return subject, student_summary.sort_values(["Total", "StudentID"], ascending=[False, True]).reset_index(drop=True)


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


def get_subject_attendance_students(reference_id, subject_id):
    subjects = DataManager.get("subjects")
    attendance = DataManager.get("attendance")

    if subjects is None or attendance is None:
        DataManager.refresh()
        subjects = DataManager.get("subjects")
        attendance = DataManager.get("attendance")

    # normalize keys using the same helper
    subjects, attendance = _normalize_subject_keys(subjects, attendance)

    reference_id = str(reference_id).strip()
    import re
    subject_key = str(subject_id).strip()
    match = re.search(r"(\d+)", subject_key)
    subject_key = match.group(1) if match else subject_key

    subject_match = subjects[
        (subjects["_SubjectKey"] == subject_key) &
        (subjects["FacultyID"] == reference_id)
    ]

    if subject_match.empty:
        return None, attendance.iloc[0:0]

    subject = subject_match.iloc[0]
    filtered = attendance[attendance["_SubjectKey"] == subject_key]

    if filtered.empty:
        return subject, filtered.iloc[0:0]

    # Determine attendance schema and compute present/absent
    filtered = filtered.copy()
    filtered["StudentID"] = filtered["StudentID"].astype(str).str.strip()

    if "Status" in filtered.columns:
        present_mask = filtered["Status"].astype(str).str.lower().isin(["present", "p", "1", "true"])
        present = filtered[present_mask].groupby("StudentID").size()
        total = filtered.groupby("StudentID").size()
        present = present.reindex(total.index, fill_value=0)
        absent = total - present
    elif "Present" in filtered.columns:
        # numeric present field
        present = filtered.groupby("StudentID")["Present"].sum()
        total = filtered.groupby("StudentID").size()
        absent = total - present
    else:
        # fallback: count rows as total sessions; assume non-empty means present
        total = filtered.groupby("StudentID").size()
        present = total
        absent = total - present

    summary = present.to_frame(name="Present").join(total.to_frame(name="Total"))
    summary["Absent"] = summary["Total"] - summary["Present"]
    summary["Percentage"] = (summary["Present"] / summary["Total"] * 100).round(2)
    summary = summary.reset_index()

    students = DataManager.get("students")
    students["StudentID"] = students["StudentID"].astype(str).str.strip()

    summary = summary.merge(
        students[["StudentID", "Name"]],
        on="StudentID",
        how="left"
    )

    return subject, summary.sort_values(["Percentage", "StudentID"], ascending=[False, True])


def get_attendance_for_student(reference_id, subject_id, student_id):
    # return raw attendance rows for a student in a subject
    subjects = DataManager.get("subjects")
    attendance = DataManager.get("attendance")

    if subjects is None or attendance is None:
        DataManager.refresh()
        subjects = DataManager.get("subjects")
        attendance = DataManager.get("attendance")

    subjects, attendance = _normalize_subject_keys(subjects, attendance)

    reference_id = str(reference_id).strip()
    import re
    subject_key = str(subject_id).strip()
    match = re.search(r"(\d+)", subject_key)
    subject_key = match.group(1) if match else subject_key

    subject_match = subjects[
        (subjects["_SubjectKey"] == subject_key) &
        (subjects["FacultyID"] == reference_id)
    ]

    if subject_match.empty:
        return None, attendance.iloc[0:0]

    subject = subject_match.iloc[0]
    attendance["StudentID"] = attendance["StudentID"].astype(str).str.strip()
    records = attendance[(attendance["_SubjectKey"] == subject_key) & (attendance["StudentID"] == str(student_id).strip())]

    return subject, records