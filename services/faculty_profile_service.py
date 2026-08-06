from models.data_manager import DataManager
from models.file_paths import FACULTY
from models.excel_manager import update_row

def get_faculty_profile(reference_id):
    faculty = DataManager.get("faculty")
    row = faculty[
        faculty["FacultyID"] == reference_id
    ]
    if row.empty:
        return None
    return row.iloc[0]

def update_faculty_profile(
    reference_id,
    form
):
    row = {
        "FacultyID": reference_id,
        "Name": form["Name"],
        "Department": form["Department"],
        "Designation": form["Designation"],
        "Qualification": form["Qualification"],
        "Experience": form["Experience"],
        "Phone": form["Phone"],
        "Email": form["Email"],
        "JoiningDate": form["JoiningDate"],
        "Status": form["Status"]
    }
    success = update_row(
        FACULTY,
        "FacultyID",
        reference_id,
        row
    )
    if success:
        DataManager.refresh()
    return success