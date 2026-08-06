from models.data_manager import DataManager
from models.file_paths import CO_PO

from models.excel_manager import (
    append_row,
    update_row,
    delete_row,
    archive_row
)


def get_all_mappings():

    return DataManager.get("co_po")


def get_mapping(mapping_id):

    mapping = DataManager.get("co_po")

    row = mapping[
        mapping["MappingID"] == mapping_id
    ]

    if row.empty:
        return None

    return row.iloc[0]


def save_mapping(form):

    mapping = DataManager.get("co_po")

    exists = mapping[
        mapping["MappingID"] == form["MappingID"]
    ]

    if not exists.empty:
        return False

    row = {

        "MappingID": form["MappingID"],

        "SubjectID": form["SubjectID"],

        "COID": form["COID"],

        "POID": form["POID"],

        "Level": form["Level"],

        "Status": form["Status"]

    }

    append_row(CO_PO, row)

    DataManager.refresh()

    return True


def update_mapping(mapping_id, form):

    row = {

        "MappingID": mapping_id,

        "SubjectID": form["SubjectID"],

        "COID": form["COID"],

        "POID": form["POID"],

        "Level": form["Level"],

        "Status": form["Status"]

    }

    success = update_row(

        CO_PO,

        "MappingID",

        mapping_id,

        row

    )

    if success:
        DataManager.refresh()

    return success


def archive_mapping(mapping_id):

    archive_row(

        CO_PO,

        "MappingID",

        mapping_id

    )

    DataManager.refresh()


def delete_mapping(mapping_id):

    delete_row(

        CO_PO,

        "MappingID",

        mapping_id

    )

    DataManager.refresh()