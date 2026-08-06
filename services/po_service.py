from models.data_manager import DataManager
from models.file_paths import PO

from models.excel_manager import (
    append_row,
    update_row,
    delete_row,
    archive_row
)


def get_all_po():

    return DataManager.get("po")



def get_po(po_id):

    po = DataManager.get("po")

    row = po[
        po["POID"] == po_id
    ]

    if row.empty:
        return None

    return row.iloc[0]


def save_po(form):

    po = DataManager.get("po")

    exists = po[
        po["POID"] == form["POID"]
    ]

    if not exists.empty:
        return False

    row = {

        "POID": form["POID"],

        "POCode": form["POCode"],

        "Description": form["Description"],

        "Status": form["Status"]

    }

    append_row(PO, row)

    DataManager.refresh()

    return True


def update_po(po_id, form):

    row = {

        "POID": po_id,

        "POCode": form["POCode"],

        "Description": form["Description"],

        "Status": form["Status"]

    }

    success = update_row(

        PO,

        "POID",

        po_id,

        row

    )

    if success:
        DataManager.refresh()

    return success


def archive_po(po_id):

    archive_row(

        PO,

        "POID",

        po_id

    )

    DataManager.refresh()


def delete_po(po_id):

    delete_row(

        PO,

        "POID",

        po_id

    )

    DataManager.refresh()