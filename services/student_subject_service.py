from models.data_manager import DataManager


def get_subjects(reference_id):

    students = DataManager.get("students")
    subjects = DataManager.get("subjects")

    if subjects is None:
        return subjects

    student = None

    if (
        students is not None
        and not students.empty
        and "StudentID" in students.columns
    ):

        row = students[
            students["StudentID"].astype(str)
            == str(reference_id)
        ]

        if not row.empty:
            student = row.iloc[0]

    # If student cannot be found,
    # return all active subjects for now.
    if student is None:
        return subjects

    result = subjects.copy()

    # Filter using semester if available
    if (
        "Semester" in student.index
        and "Semester" in result.columns
    ):

        try:

            semester = int(
                float(student["Semester"])
            )

            result = result[
                result["Semester"].astype(str)
                == str(semester)
            ]

        except:
            pass

    return result