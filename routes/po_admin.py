from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from services.po_service import *

po_admin = Blueprint(
    "po_admin",
    __name__
)
@po_admin.route("/admin/po")
def po():

    po = get_all_po()
    print("========== PO DATA ==========")
    print(po.columns)
    print(po.head())
    print("=============================")
    return render_template(

        "admin/po/index.html",

        po=po

    )
@po_admin.route(
    "/admin/po/add",
    methods=["POST"]
)
def add_po():

    success = save_po(request.form)

    if success:

        flash(
            "PO Added Successfully.",
            "success"
        )

    else:

        flash(
            "PO ID already exists.",
            "danger"
        )

    return redirect(
        url_for("po_admin.po")
    )
@po_admin.route(
    "/admin/po/update/<po_id>",
    methods=["POST"]
)
def update(po_id):

    update_po(
        po_id,
        request.form
    )

    flash(
        "PO Updated Successfully.",
        "success"
    )

    return redirect(
        url_for("po_admin.po")
    )
@po_admin.route("/admin/po/edit/<po_id>")
def edit_po(po_id):

    po = get_po(po_id)

    return render_template(

        "admin/po/edit.html",

        po=po

    )
@po_admin.route("/admin/po/archive/<po_id>")
def archive(po_id):

    archive_po(po_id)

    flash(
        "PO Archived Successfully.",
        "success"
    )

    return redirect(
        url_for("po_admin.po")
    )
@po_admin.route("/admin/po/delete/<po_id>")
def delete(po_id):

    delete_po(po_id)

    flash(
        "PO Deleted Successfully.",
        "success"
    )

    return redirect(
        url_for("po_admin.po")
    )
