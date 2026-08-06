from models.data_manager import DataManager
from models.file_paths import STUDENTS
from models.excel_manager import append_row, update_row, delete_row, archive_row

def get_all_students():
    return DataManager.get("students")


def save_student(form):

    students = DataManager.get("students")

    # Check duplicate Student ID
    exists = students[
        students["StudentID"] == form["StudentID"]
    ]

    if not exists.empty:
        return False

    row = {
        "StudentID": form["StudentID"],
        "Name": form["Name"],
        "Year": int(form["Year"]),
        "Semester": int(form["Semester"]),
        "Section": form["Section"],
        "Department": form["Department"],
        "Email": form["Email"]
    }

    append_row(STUDENTS, row)

    DataManager.refresh()

    return True
def get_student(student_id):

    students = DataManager.get("students")

    student = students[
        students["StudentID"] == student_id
    ]

    if student.empty:
        return None

    return student.iloc[0]


def update_student(student_id, form):

    row = {

        "StudentID": student_id,

        "Name": form["Name"],

        "Department": form["Department"],

        "Year": int(float(form["Year"])),
        
        "Semester": int(float(form["Semester"])),

        "Section": form["Section"],

        "Email": form["Email"]

    }

    success = update_row(

        STUDENTS,

        "StudentID",

        student_id,

        row

    )

    if success:
        DataManager.refresh()

    return success
def archive_student(student_id):

    archive_row(

        STUDENTS,

        "StudentID",

        student_id

    )

    DataManager.refresh()
def delete_student(student_id):

    delete_row(

        STUDENTS,

        "StudentID",

        student_id

    )

    DataManager.refresh()