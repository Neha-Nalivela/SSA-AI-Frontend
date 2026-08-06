from models.data_manager import DataManager
from models.file_paths import SUBJECTS
from models.excel_manager import (
    append_row,
    update_row,
    delete_row,
    archive_row
)
def get_all_subjects():

    return DataManager.get("subjects")

def save_subject(form):

    subjects = DataManager.get("subjects")

    exists = subjects[
        subjects["SubjectID"] == form["SubjectID"]
    ]

    if not exists.empty:
        return False

    row = {

        "SubjectID": form["SubjectID"],

        "SubjectCode": form["SubjectCode"],

        "SubjectName": form["SubjectName"],

        "Department": form["Department"],

        "Year": int(form["Year"]),

        "Semester": int(form["Semester"]),

        "Credits": int(form["Credits"]),

        "SubjectType": form["SubjectType"],

        "FacultyID": form["FacultyID"],

        "Regulation": form["Regulation"],

        "Status": form["Status"]

    }

    append_row(
        SUBJECTS,
        row
    )

    DataManager.refresh()

    return True
def get_subject(subject_id):

    subjects = DataManager.get("subjects")

    subject = subjects[
        subjects["SubjectID"] == subject_id
    ]

    if subject.empty:
        return None

    return subject.iloc[0]
def update_subject(subject_id, form):

    row = {

        "SubjectID": subject_id,

        "SubjectCode": form["SubjectCode"],

        "SubjectName": form["SubjectName"],

        "Department": form["Department"],

        "Year": int(float(form["Year"])),

        "Semester": int(float(form["Semester"])),

        "Credits": int(float(form["Credits"])),

        "SubjectType": form["SubjectType"],

        "FacultyID": form["FacultyID"],

        "Regulation": form["Regulation"],

        "Status": form["Status"]

    }

    success = update_row(

        SUBJECTS,

        "SubjectID",

        subject_id,

        row

    )

    if success:
        DataManager.refresh()

    return success
def archive_subject(subject_id):

    archive_row(

        SUBJECTS,

        "SubjectID",

        subject_id

    )

    DataManager.refresh()
def delete_subject(subject_id):

    delete_row(

        SUBJECTS,

        "SubjectID",

        subject_id

    )

    DataManager.refresh()

