from models.data_manager import DataManager
from models.file_paths import FEEDBACK

from models.excel_manager import append_row


FEEDBACK_QUESTION_LABELS = {
    "Q1": "The faculty explains concepts clearly.",
    "Q2": "The faculty encourages student participation.",
    "Q3": "The faculty uses examples and practical applications.",
    "Q4": "The faculty is regular and punctual.",
    "Q5": "The faculty clarifies doubts effectively."
}


def save_feedback(reference_id, form):

    row = {

        "StudentID": reference_id,

        "FeedbackType":
            form.get("FeedbackType", ""),

        "Subject":
            form.get("Subject", ""),

        "Rating":
            form.get("Rating", ""),

        "Comments":
            form.get("Comments", "")

    }

    try:

        append_row(
            FEEDBACK,
            row
        )

        DataManager.refresh()

        return True

    except Exception as e:

        print(
            "Feedback Error:",
            e
        )

        return False


def get_all_feedback():
    feedback = DataManager.get("feedback")

    if feedback is None or feedback.empty:
        return []

    return feedback.fillna("").to_dict(orient="records")


def get_feedback_analytics(subject_id=None):
    feedback = DataManager.get("feedback")

    if feedback is None or feedback.empty:
        return {
            "total": 0,
            "subjects": [],
            "ratings": [],
            "questions": [],
            "comments": []
        }

    data = feedback.fillna("").copy()

    def selected_counts(column):
        if column not in data.columns:
            return []
        counts = data[column].astype(str).str.strip()
        counts = counts[counts != ""].value_counts()
        return [
            {"label": label, "count": int(count)}
            for label, count in counts.items()
        ]

    comments = []
    if "Comment" in data.columns:
        comment_rows = data[data["Comment"].astype(str).str.strip() != ""]
        if subject_id:
            comment_rows = comment_rows[
                comment_rows["SubjectID"].astype(str).str.strip()
                == str(subject_id).strip()
            ]
        comments = comment_rows.to_dict(orient="records")

    question_summary = []
    for column in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
        if column not in data.columns:
            continue
        values = data[column].astype(str).str.strip()
        values = values[values != ""].astype(float)
        if not values.empty:
            question_summary.append({
                "label": FEEDBACK_QUESTION_LABELS.get(column, column),
                "average": round(float(values.mean()), 2),
                "responses": len(values)
            })

    return {
        "total": len(data),
        "subjects": selected_counts("SubjectID"),
        "questions": question_summary,
        "ratings": selected_counts("Overall"),
        "comments": comments
    }