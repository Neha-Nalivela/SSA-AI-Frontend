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


def get_questions_for_faculty_subject(faculty_ref, subject_id):

    questions = DataManager.get("question_bank")
    subjects = DataManager.get("subjects")

    # try to reload if missing
    if questions is None or subjects is None:
        DataManager.refresh()
        questions = DataManager.get("question_bank")
        subjects = DataManager.get("subjects")

    if questions is None or subjects is None:
        return pd.DataFrame()

    # normalize id columns and create numeric keys to handle different prefixes (e.g., S001 vs SUB001)
    import re

    def numeric_key(x):
        x = str(x)
        m = re.search(r"(\d+)", x)
        return m.group(1) if m else x.strip()

    if "SubjectID" in questions.columns:
        questions["SubjectID"] = questions["SubjectID"].astype(str).str.strip()
        questions["_SubjectKey"] = questions["SubjectID"].apply(numeric_key)
    else:
        questions["_SubjectKey"] = ""

    if "SubjectID" in subjects.columns:
        subjects["SubjectID"] = subjects["SubjectID"].astype(str).str.strip()
        subjects["_SubjectKey"] = subjects["SubjectID"].apply(numeric_key)
    else:
        subjects["_SubjectKey"] = ""

    if "FacultyID" in subjects.columns:
        subjects["FacultyID"] = subjects["FacultyID"].astype(str).str.strip()

    subject_key = numeric_key(subject_id)
    faculty_ref = str(faculty_ref).strip()

    # ensure subject belongs to faculty (compare numeric keys)
    match = subjects[
        (subjects["_SubjectKey"] == subject_key) &
        (subjects["FacultyID"] == faculty_ref)
    ]

    if match.empty:
        return pd.DataFrame()

    return questions[questions["_SubjectKey"] == subject_key]


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