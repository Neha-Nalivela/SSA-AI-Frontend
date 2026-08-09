from models.data_manager import DataManager
from models.file_paths import FEEDBACK

from models.excel_manager import append_row


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