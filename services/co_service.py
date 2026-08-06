from models.data_manager import DataManager
from models.file_paths import CO

from models.excel_manager import (
    append_row,
    update_row,
    delete_row,
    archive_row
)


def get_all_co():

    return DataManager.get("co")


def get_co(co_id):

    co = DataManager.get("co")

    row = co[
        co["COID"] == co_id
    ]

    if row.empty:
        return None

    return row.iloc[0]


def save_co(form):

    co = DataManager.get("co")

    exists = co[
        co["COID"] == form["COID"]
    ]

    if not exists.empty:
        return False

    row = {
    "COID": form["COID"],

    "SubjectID": form["SubjectID"],

    "COCode": form["COCode"],

    "Description": form["Description"],

    "BTLLevel": form["BTLLevel"],

    "Status": form["Status"]
    }

    append_row(CO, row)

    DataManager.refresh()

    return True


def update_co(co_id, form):

    row = {
        "COID": form["COID"],
        "SubjectID": form["SubjectID"],
        "COCode": form["COCode"],
        "Description": form["Description"],
        "BTLLevel": form["BTLLevel"],
        "Status": form["Status"]
    }

    success = update_row(
        CO, "COID", co_id, row
    )

    if success:
        DataManager.refresh()
    return success

def archive_co(co_id):
    archive_row( 
        CO, "COID", co_id)
    DataManager.refresh()

def delete_co(co_id):
    delete_row(
        CO, "COID", co_id
    )
    DataManager.refresh()