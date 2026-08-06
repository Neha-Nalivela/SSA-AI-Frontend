from models.data_manager import DataManager
from models.file_paths import FACULTY
from models.excel_manager import (
    append_row,
    update_row,
    delete_row,
    archive_row
)

def get_all_faculty():
    return DataManager.get("faculty")

def save_faculty(form):
    faculty = DataManager.get("faculty")
    exists = faculty[
        faculty["FacultyID"] == form["FacultyID"]
    ]
    if not exists.empty:
        return False
    row = {
        "FacultyID": form["FacultyID"],
        "Name": form["Name"],
        "Department": form["Department"],
        "Designation": form["Designation"],
        "Qualification": form["Qualification"],
        "Experience": int(form["Experience"]),
        "Phone": form["Phone"],
        "Email": form["Email"],
        "JoiningDate": form["JoiningDate"],
        "Status": form["Status"]
    }
    append_row(
        FACULTY,
        row
    )
    DataManager.refresh()
    return True

def get_faculty(faculty_id):
    faculty = DataManager.get("faculty")
    data = faculty[
        faculty["FacultyID"] == faculty_id
    ]
    if data.empty:
        return None
    return data.iloc[0]


def update_faculty(
    faculty_id,
    form
):
    row = {
        "FacultyID": faculty_id,
        "Name": form["Name"],
        "Department": form["Department"],
        "Designation": form["Designation"],
        "Qualification": form["Qualification"],
        "Experience": int(float(form["Experience"])),
        "Phone": form["Phone"],
        "Email": form["Email"],
        "JoiningDate": form["JoiningDate"],
        "Status": form["Status"]
    }
    success = update_row(
        FACULTY,
        "FacultyID",
        faculty_id,
        row
    )
    if success:
        DataManager.refresh()
    return success

def archive_faculty(faculty_id):
    archive_row(
        FACULTY,
        "FacultyID",
        faculty_id
    )
    DataManager.refresh()

def delete_faculty(faculty_id):
    delete_row(
        FACULTY,
        "FacultyID",
        faculty_id
    )
    DataManager.refresh()