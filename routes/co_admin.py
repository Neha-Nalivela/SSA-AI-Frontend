from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from services.co_service import *

co_admin = Blueprint(
    "co_admin",
    __name__
)

@co_admin.route("/admin/co")
def co():

    co = get_all_co()

    return render_template(

        "admin/co/index.html",

        co=co

    )
    
@co_admin.route(
    "/admin/co/add",
    methods=["POST"]
)
def add_co():

    success = save_co(request.form)

    if success:

        flash(
            "CO Added Successfully.",
            "success"
        )

    else:

        flash(
            "CO ID already exists.",
            "danger"
        )

    return redirect(
        url_for("co_admin.co")
    )
@co_admin.route(
    "/admin/co/edit/<co_id>"
)
def edit_co(co_id):

    co = get_co(co_id)

    return render_template(

        "admin/co/edit.html",

        co=co

    )
@co_admin.route(
    "/admin/co/update/<co_id>",
    methods=["POST"]
)
def update(co_id):

    update_co(

        co_id,

        request.form

    )

    flash(

        "CO Updated Successfully.",

        "success"

    )

    return redirect(

        url_for("co_admin.co")

    )
@co_admin.route(
    "/admin/co/archive/<co_id>"
)
def archive(co_id):

    archive_co(co_id)

    flash(

        "CO Archived Successfully.",

        "success"

    )

    return redirect(

        url_for("co_admin.co")

    )
@co_admin.route(
    "/admin/co/delete/<co_id>"
)
def delete(co_id):

    delete_co(co_id)

    flash(

        "CO Deleted Successfully.",

        "success"

    )

    return redirect(

        url_for("co_admin.co")

    )
