from models.data_manager import DataManager
import pandas as pd
from models.file_paths import QUESTION_BANK

from models.excel_manager import (
    append_row,
    update_row,
    delete_row,
    archive_row
)


def get_all_questions():

    return DataManager.get("question_bank")


def get_questions_by_subject(subject_id):

    questions = DataManager.get("question_bank")

    if questions is None:
        return pd.DataFrame()

    return questions[
        questions["SubjectID"] == subject_id
    ]


def get_question(question_id):

    questions = DataManager.get("question_bank")

    row = questions[
        questions["QuestionID"] == question_id
    ]

    if row.empty:
        return None

    return row.iloc[0]


def save_question(form):

    questions = DataManager.get("question_bank")

    exists = questions[
        questions["QuestionID"] == form["QuestionID"]
    ]

    if not exists.empty:
        return False

    row = {

        "QuestionID": form["QuestionID"],

        "SubjectID": form["SubjectID"],

        "Subject": form["Subject"],

        "Topic": form["Topic"],

        "Subtopic": form["Subtopic"],

        "COID": form["COID"],

        "BTL": form["BTL"],

        "Exam": form["Exam"],

        "MaxMarks": form["MaxMarks"],

        "Question": form["Question"],

        "QuestionType": form["QuestionType"],

        "Difficulty": form["Difficulty"],

        "Status": form["Status"]

    }

    append_row(QUESTION_BANK, row)

    DataManager.refresh()

    return True


def update_question(question_id, form):

    row = {

        "QuestionID": question_id,

        "SubjectID": form["SubjectID"],

        "Subject": form["Subject"],

        "Topic": form["Topic"],

        "Subtopic": form["Subtopic"],

        "COID": form["COID"],

        "BTL": form["BTL"],

        "Exam": form["Exam"],

        "MaxMarks": form["MaxMarks"],

        "Question": form["Question"],

        "QuestionType": form["QuestionType"],

        "Difficulty": form["Difficulty"],

        "Status": form["Status"]

    }

    success = update_row(

        QUESTION_BANK,

        "QuestionID",

        question_id,

        row

    )

    if success:

        DataManager.refresh()

    return success


def archive_question(question_id):

    archive_row(

        QUESTION_BANK,

        "QuestionID",

        question_id

    )

    DataManager.refresh()


def delete_question(question_id):

    delete_row(

        QUESTION_BANK,

        "QuestionID",

        question_id

    )

    DataManager.refresh()