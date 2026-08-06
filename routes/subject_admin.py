from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from models.data_manager import DataManager

from services.subject_service import (
    get_all_subjects,
    save_subject,
    get_subject,
    update_subject,
    archive_subject,
    delete_subject
)

subject_admin = Blueprint(
    "subject_admin",
    __name__
)


# ==========================
# Subject List
# ==========================

@subject_admin.route("/admin/subjects")
def subjects():

    subjects = get_all_subjects()

    faculty = DataManager.get("faculty")

    return render_template(
        "admin/subjects/index.html",
        subjects=subjects,
        faculty=faculty
    )


# ==========================
# Add Subject
# ==========================

@subject_admin.route(
    "/admin/subjects/add",
    methods=["POST"]
)
def add_subject():

    success = save_subject(request.form)

    if not success:

        flash(
            "Subject ID already exists.",
            "danger"
        )

    else:

        flash(
            "Subject Added Successfully.",
            "success"
        )

    return redirect(
        url_for("subject_admin.subjects")
    )


# ==========================
# Edit Subject
# ==========================

@subject_admin.route(
    "/admin/subjects/edit/<subject_id>"
)
def edit_subject(subject_id):

    subject = get_subject(subject_id)

    faculty = DataManager.get("faculty")

    return render_template(
        "admin/subjects/edit.html",
        subject=subject,
        faculty=faculty
    )


# ==========================
# Update Subject
# ==========================

@subject_admin.route(
    "/admin/subjects/update/<subject_id>",
    methods=["POST"]
)
def update_subject_route(subject_id):

    update_subject(
        subject_id,
        request.form
    )

    flash(
        "Subject Updated Successfully.",
        "success"
    )

    return redirect(
        url_for("subject_admin.subjects")
    )


# ==========================
# Archive Subject
# ==========================

@subject_admin.route(
    "/admin/subjects/archive/<subject_id>"
)
def archive(subject_id):

    archive_subject(subject_id)

    flash(
        "Subject Archived Successfully.",
        "success"
    )

    return redirect(
        url_for("subject_admin.subjects")
    )


# ==========================
# Delete Subject
# ==========================

@subject_admin.route(
    "/admin/subjects/delete/<subject_id>"
)
def delete(subject_id):

    delete_subject(subject_id)

    flash(
        "Subject Deleted Successfully.",
        "success"
    )

    return redirect(
        url_for("subject_admin.subjects")
    )