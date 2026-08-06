from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from services.faculty_service import *

faculty_admin = Blueprint(
    "faculty_admin",
    __name__
)


@faculty_admin.route("/admin/faculty")
def faculty():

    faculty = get_all_faculty()

    return render_template(

        "admin/faculty/index.html",

        faculty=faculty

    )


@faculty_admin.route(
    "/admin/faculty/add",
    methods=["POST"]
)
def add_faculty():

    success = save_faculty(request.form)

    if success:

        flash(
            "Faculty Added Successfully.",
            "success"
        )

    else:

        flash(
            "Faculty ID already exists.",
            "danger"
        )

    return redirect(
        url_for("faculty_admin.faculty")
    )


@faculty_admin.route(
    "/admin/faculty/edit/<faculty_id>"
)
def edit_faculty(faculty_id):

    faculty = get_faculty(faculty_id)

    return render_template(

        "admin/faculty/edit.html",

        faculty=faculty

    )


@faculty_admin.route(
    "/admin/faculty/update/<faculty_id>",
    methods=["POST"]
)
def update_faculty_route(faculty_id):

    update_faculty(

        faculty_id,

        request.form

    )

    flash(
        "Faculty Updated Successfully.",
        "success"
    )

    return redirect(
        url_for("faculty_admin.faculty")
    )


@faculty_admin.route(
    "/admin/faculty/archive/<faculty_id>"
)
def archive(faculty_id):

    archive_faculty(faculty_id)

    flash(
        "Faculty Archived Successfully.",
        "success"
    )

    return redirect(
        url_for("faculty_admin.faculty")
    )


@faculty_admin.route(
    "/admin/faculty/delete/<faculty_id>"
)
def delete(faculty_id):

    delete_faculty(faculty_id)

    flash(
        "Faculty Deleted Successfully.",
        "success"
    )

    return redirect(
        url_for("faculty_admin.faculty")
    )