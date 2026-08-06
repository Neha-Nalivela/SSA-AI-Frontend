from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from services.subject_service import get_all_subjects
from services.co_service import get_all_co
from services.po_service import get_all_po
from services.co_po_service import *

co_po_admin = Blueprint(
    "co_po_admin",
    __name__
)
@co_po_admin.route("/admin/co-po")
def mappings():

    mappings = get_all_mappings()

    return render_template(

        "admin/co_po/index.html",

        mappings=get_all_mappings(),

        subjects=get_all_subjects(),

        co=get_all_co(),

        po=get_all_po()

    )
@co_po_admin.route(
    "/admin/co-po/add",
    methods=["POST"]
)
def add_mapping():

    success = save_mapping(request.form)

    if success:

        flash(
            "CO-PO Mapping Added Successfully.",
            "success"
        )

    else:

        flash(
            "Mapping ID already exists.",
            "danger"
        )

    return redirect(
        url_for("co_po_admin.mappings")
    )
@co_po_admin.route(
    "/admin/co-po/edit/<mapping_id>"
)
def edit_mapping(mapping_id):

    mapping = get_mapping(mapping_id)

    return render_template(

        "admin/co_po/edit.html",

        mapping=mapping,

        subjects=get_all_subjects(),

        co=get_all_co(),

        po=get_all_po()

    )
@co_po_admin.route(
    "/admin/co-po/update/<mapping_id>",
    methods=["POST"]
)
def update(mapping_id):

    update_mapping(

        mapping_id,

        request.form

    )

    flash(

        "Mapping Updated Successfully.",

        "success"

    )

    return redirect(

        url_for("co_po_admin.mappings")

    )
@co_po_admin.route(
    "/admin/co-po/archive/<mapping_id>"
)
def archive(mapping_id):

    archive_mapping(mapping_id)

    flash(

        "Mapping Archived Successfully.",

        "success"

    )

    return redirect(

        url_for("co_po_admin.mappings")

    )
@co_po_admin.route(
    "/admin/co-po/delete/<mapping_id>"
)
def delete(mapping_id):

    delete_mapping(mapping_id)

    flash(

        "Mapping Deleted Successfully.",

        "success"

    )

    return redirect(

        url_for("co_po_admin.mappings")

    )
    