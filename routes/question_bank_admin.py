from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from services.question_bank_service import *
from services.subject_service import get_all_subjects
from services.co_service import get_all_co


question_bank_admin = Blueprint(
    "question_bank_admin",
    __name__
)


@question_bank_admin.route("/admin/question-bank")
def questions():

    questions = get_all_questions()

    subjects = get_all_subjects()

    co = get_all_co()

    return render_template(

        "admin/question_bank/index.html",

        questions=questions,

        subjects=subjects,

        co=co

    )


@question_bank_admin.route(
    "/admin/question-bank/add",
    methods=["POST"]
)
def add_question():

    success = save_question(request.form)

    if success:

        flash(
            "Question Added Successfully.",
            "success"
        )

    else:

        flash(
            "Question ID already exists.",
            "danger"
        )

    return redirect(
        url_for("question_bank_admin.questions")
    )


@question_bank_admin.route(
    "/admin/question-bank/edit/<question_id>"
)
def edit_question(question_id):

    question = get_question(question_id)

    subjects = get_all_subjects()

    co = get_all_co()

    return render_template(

        "admin/question_bank/edit.html",

        question=question,

        subjects=subjects,

        co=co

    )
@question_bank_admin.route(
    "/admin/question-bank/update/<question_id>",
    methods=["POST"]
)
def update(question_id):

    update_question(

        question_id,

        request.form

    )

    flash(

        "Question Updated Successfully.",

        "success"

    )

    return redirect(

        url_for("question_bank_admin.questions")

    )


@question_bank_admin.route(
    "/admin/question-bank/archive/<question_id>"
)
def archive(question_id):

    archive_question(question_id)

    flash(

        "Question Archived Successfully.",

        "success"

    )

    return redirect(

        url_for("question_bank_admin.questions")

    )


@question_bank_admin.route(
    "/admin/question-bank/delete/<question_id>"
)
def delete(question_id):

    delete_question(question_id)

    flash(

        "Question Deleted Successfully.",

        "success"

    )

    return redirect(

        url_for("question_bank_admin.questions")

    )
