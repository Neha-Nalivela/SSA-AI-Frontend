from flask import Blueprint
from flask import render_template
from flask import session
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from services.faculty_dashboard_service import get_dashboard

from services.faculty_profile_service import (
    get_faculty_profile,
    update_faculty_profile
)

from services.question_bank_service import (
    get_all_questions,
    get_question,
    save_question,
    update_question,
    archive_question,
    delete_question
)
from services.faculty_subject_service import (
    get_faculty_subjects,
    get_subject_dashboard
)

faculty = Blueprint(
    "faculty",
    __name__
)


@faculty.route("/faculty/dashboard")
def dashboard():

    reference_id = session.get("reference_id")

    data = get_dashboard(reference_id)

    return render_template(

        "faculty/dashboard.html",

        data=data

    )


@faculty.route("/faculty/profile")
def profile():

    reference_id = session.get("reference_id")

    faculty_data = get_faculty_profile(reference_id)

    return render_template(

        "faculty/profile.html",

        faculty=faculty_data

    )


@faculty.route(
    "/faculty/profile/update",
    methods=["POST"]
)
def update_profile():

    reference_id = session.get("reference_id")

    update_faculty_profile(

        reference_id,

        request.form

    )

    flash(

        "Profile Updated Successfully.",

        "success"

    )

    return redirect(

        url_for("faculty.profile")

    )


@faculty.route("/faculty/subjects")
def subjects():

    reference_id = session.get("reference_id")

    subjects = get_faculty_subjects(reference_id)

    return render_template(

        "faculty/subjects/index.html",

        subjects=subjects

    )
@faculty.route("/faculty/question-bank")
def question_bank():

    questions = get_all_questions()

    return render_template(
        "faculty/question_bank/index.html",
        questions=questions
    )
@faculty.route("/faculty/question-bank/add")
def add_question_page():

    return render_template(

        "faculty/question_bank/add.html"

    )
@faculty.route(
    "/faculty/question-bank/save",
    methods=["POST"]
)
def save_question_route():

    success = save_question(

        request.form

    )

    if success:

        flash(

            "Question Added Successfully.",

            "success"

        )

    else:

        flash(

            "Question ID Already Exists.",

            "danger"

        )

    return redirect(

        url_for("faculty.question_bank")

    )
@faculty.route(
    "/faculty/question-bank/edit/<question_id>"
)
def edit_question(question_id):

    question = get_question(

        question_id

    )

    return render_template(

        "faculty/question_bank/edit.html",

        question=question

    )
@faculty.route(
    "/faculty/question-bank/update/<question_id>",
    methods=["POST"]
)
def update_question_route(question_id):

    update_question(

        question_id,

        request.form

    )

    flash(

        "Question Updated Successfully.",

        "success"

    )

    return redirect(

        url_for("faculty.question_bank")

    )
@faculty.route(
    "/faculty/question-bank/archive/<question_id>"
)
def archive_question_route(question_id):

    archive_question(

        question_id

    )

    flash(

        "Question Archived Successfully.",

        "warning"

    )

    return redirect(

        url_for("faculty.question_bank")

    )
@faculty.route(
    "/faculty/question-bank/delete/<question_id>"
)
def delete_question_route(question_id):

    delete_question(

        question_id

    )

    flash(

        "Question Deleted Successfully.",

        "danger"

    )

    return redirect(

        url_for("faculty.question_bank")

    )
@faculty.route("/faculty/question-bank/view/<question_id>")

@faculty.route("/faculty/subject/<subject_id>")
def subject_dashboard(subject_id):

    reference_id = session.get("reference_id")

    data = get_subject_dashboard(
        reference_id,
        subject_id
    )

    return render_template(

        "faculty/subjects/dashboard.html",

        data=data

    )
