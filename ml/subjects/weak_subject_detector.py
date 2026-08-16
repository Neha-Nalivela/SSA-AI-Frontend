import pandas as pd

from models.data_manager import DataManager


# --------------------------------------------------
# Configuration
# --------------------------------------------------

WEAK_PERCENTAGE_THRESHOLD = 50.0
WARNING_PERCENTAGE_THRESHOLD = 60.0


# --------------------------------------------------
# Utility
# --------------------------------------------------

def _numeric(series):
    """Safely convert a pandas Series to numeric."""
    return pd.to_numeric(series, errors="coerce")


# --------------------------------------------------
# Student Subject Performance
# --------------------------------------------------

def get_student_subject_performance(student_id):
    """
    Calculate subject-wise performance for a student.

    Returns:
        List of dictionaries containing:
        SubjectID, Subject, ObtainedMarks,
        MaximumMarks, Percentage, Status
    """

    student_id = str(student_id)

    marks = DataManager.get("marks")
    question_bank = DataManager.get("question_bank")
    subjects = DataManager.get("subjects")

    if marks is None or marks.empty:
        return []

    if "StudentID" not in marks.columns:
        return []

    student_marks = marks[
        marks["StudentID"].astype(str) == student_id
    ].copy()

    if student_marks.empty:
        return []

    # Convert marks to numeric
    student_marks["MarksObtained"] = _numeric(
        student_marks["MarksObtained"]
    )

    student_marks["MaxMarks"] = _numeric(
        student_marks["MaxMarks"]
    )

    student_marks = student_marks.dropna(
        subset=["MarksObtained", "MaxMarks"]
    )

    if student_marks.empty:
        return []

    # --------------------------------------------------
    # Subject-wise aggregation
    # --------------------------------------------------

    grouped = student_marks.groupby("SubjectID").agg(
        ObtainedMarks=("MarksObtained", "sum"),
        MaximumMarks=("MaxMarks", "sum")
    ).reset_index()

    results = []

    for _, row in grouped.iterrows():

        subject_id = str(row["SubjectID"])

        obtained = float(row["ObtainedMarks"])
        maximum = float(row["MaximumMarks"])

        if maximum <= 0:
            continue

        percentage = round(
            (obtained / maximum) * 100,
            2
        )

        # --------------------------------------------------
        # Subject name
        # --------------------------------------------------

        subject_name = subject_id

        # First try Subjects dataset
        if (
            subjects is not None
            and not subjects.empty
            and "SubjectID" in subjects.columns
        ):

            subject_rows = subjects[
                subjects["SubjectID"].astype(str)
                == subject_id
            ]

            if not subject_rows.empty:

                subject_row = subject_rows.iloc[0]

                subject_name = subject_row.get(
                    "SubjectName",
                    subject_id
                )

        # Fallback to Question Bank
        if subject_name == subject_id:

            if (
                question_bank is not None
                and not question_bank.empty
                and "SubjectID" in question_bank.columns
            ):

                question_rows = question_bank[
                    question_bank["SubjectID"].astype(str)
                    == subject_id
                ]

                if (
                    not question_rows.empty
                    and "Subject" in question_rows.columns
                ):

                    subject_name = question_rows.iloc[0].get(
                        "Subject",
                        subject_id
                    )

        # --------------------------------------------------
        # Status
        # --------------------------------------------------

        if percentage < WEAK_PERCENTAGE_THRESHOLD:
            status = "Weak"

        elif percentage < WARNING_PERCENTAGE_THRESHOLD:
            status = "Needs Improvement"

        else:
            status = "Good"

        results.append({
            "SubjectID": subject_id,
            "Subject": str(subject_name),
            "ObtainedMarks": round(obtained, 2),
            "MaximumMarks": round(maximum, 2),
            "Percentage": percentage,
            "Status": status
        })

    # Weak subjects first
    results.sort(
        key=lambda x: x["Percentage"]
    )

    return results


# --------------------------------------------------
# Weak Subject Detector
# --------------------------------------------------

def detect_weak_subjects(student_id):
    """
    Identify weak subjects for a student.

    Returns:
        Dictionary containing subject performance
        and weak subjects.
    """

    performance = get_student_subject_performance(
        student_id
    )

    weak_subjects = [
        subject
        for subject in performance
        if subject["Percentage"]
        < WEAK_PERCENTAGE_THRESHOLD
    ]

    improvement_subjects = [
        subject
        for subject in performance
        if (
            WEAK_PERCENTAGE_THRESHOLD
            <= subject["Percentage"]
            < WARNING_PERCENTAGE_THRESHOLD
        )
    ]

    return {
        "StudentID": str(student_id),
        "subjects": performance,
        "weak_subjects": weak_subjects,
        "needs_improvement": improvement_subjects,
        "weak_subject_count": len(weak_subjects)
    }


# --------------------------------------------------
# Single Weak Subject
# --------------------------------------------------

def get_weakest_subject(student_id):
    """
    Return the student's weakest subject.
    """

    performance = get_student_subject_performance(
        student_id
    )

    if not performance:
        return None

    return performance[0]