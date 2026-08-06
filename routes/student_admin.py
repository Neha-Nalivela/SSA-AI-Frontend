from flask import Blueprint, flash, render_template, request, redirect, url_for

from services.student_service import get_all_students, save_student, get_student, update_student, archive_student, delete_student

student_admin = Blueprint(
    "student_admin",
    __name__
)


@student_admin.route("/admin/students")
def students():

    students = get_all_students()

    return render_template(
        "admin/students/index.html",
        students=students
    )

@student_admin.route(
    "/admin/students/add",
    methods=["POST"]
)
def add_student():
    success = save_student(request.form)
    if not success:
        flash(
            "Student ID already exists.",
            "danger"
        )
    else:
        flash(
            "Student Added Successfully.",
            "success"
        )
        return redirect(
    url_for("student_admin.students")
)
@student_admin.route("/admin/students/edit/<student_id>")
def edit_student(student_id):

    student = get_student(student_id)

    return render_template(

        "admin/students/edit.html",

        student=student

    )


@student_admin.route(

    "/admin/students/update/<student_id>",

    methods=["POST"]

)
def update_student_route(student_id):

    update_student(

        student_id,

        request.form

    )

    flash(

        "Student Updated Successfully.",

        "success"

    )

    return redirect(

        url_for("student_admin.students")

    )
@student_admin.route(
    "/admin/students/archive/<student_id>"
)
def archive(student_id):

    archive_student(student_id)

    flash(
        "Student Archived Successfully.",
        "success"
    )

    return redirect(
        url_for("student_admin.students")
    )
@student_admin.route(
    "/admin/students/delete/<student_id>"
)
def delete(student_id):

    delete_student(student_id)

    flash(

        "Student Deleted Successfully.",

        "success"

    )

    return redirect(

        url_for("student_admin.students")

    )