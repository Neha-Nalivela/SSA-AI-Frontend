import pandas as pd
from urllib.parse import quote_plus

from models.data_manager import DataManager
from ml.recomendations.resource_recommender import recommend_resources


def _learning_path(subject, topic):
    query = quote_plus(f"{subject} {topic}")
    return [
        {
            "Platform": "W3Schools",
            "Title": f"{subject} {topic} tutorials",
            "URL": f"https://www.w3schools.com/search/search.php?search={query}",
        },
        {
            "Platform": "YouTube",
            "Title": f"{subject} {topic} videos",
            "URL": f"https://www.youtube.com/results?search_query={query}",
        },
        {
            "Platform": "GeeksforGeeks",
            "Title": f"{subject} {topic} articles",
            "URL": f"https://www.geeksforgeeks.org/?s={query}",
        },
    ]


def _normalize_ai_record(item):
    if not isinstance(item, dict):
        return {}

    recommendation_text = item.get("Recommendation") or item.get("Reason") or "Focus on this learning area."
    subject_name = item.get("Subject") or item.get("SubjectID") or "Subject"
    resource_url = item.get("URL") or item.get("ResourceURL") or ""
    resource_title = item.get("ResourceTitle") or item.get("Resource") or "Recommended learning resource"

    record = {
        "Subject": subject_name,
        "SubjectID": item.get("SubjectID") or subject_name,
        "Topic": item.get("Topic") or "General",
        "Recommendation": recommendation_text,
        "Reason": item.get("Reason") or "AI-based academic guidance",
        "CO": item.get("WeakestCO") or item.get("CO"),
        "BTL": item.get("WeakestBTL") or item.get("BTL"),
        "Marks": item.get("TopicPercentage") or item.get("Marks"),
        "Resource": resource_title,
        "ResourceURL": resource_url,
        "Priority": item.get("Priority") or "Medium",
    }
    record["LearningPath"] = _learning_path(record["Subject"], record["Topic"])
    return record


def _deduplicate_recommendations(records):
    unique = {}
    for record in records:
        if not record:
            continue
        key = (
            str(record.get("SubjectID") or record.get("Subject") or "").strip().lower(),
            str(record.get("Topic") or "General").strip().lower(),
        )
        if key not in unique:
            unique[key] = record
    return list(unique.values())


def get_ai_recommendations(reference_id):

    students = DataManager.get("students")
    marks = DataManager.get("marks")
    attendance = DataManager.get("attendance")
    recommendations = DataManager.get("recommendations")
    resources = DataManager.get("resources")
    remedial = DataManager.get("remedial")

    result = {
        "weak_subjects": [],
        "recommendations": [],
        "resources": [],
        "remedial_classes": []
    }

    if students is None or students.empty:
        return result

    student = students[
        students["StudentID"].astype(str) == str(reference_id)
    ]

    if student.empty:
        return result

    # ---------------------------------
    # Student Marks Analysis
    # ---------------------------------

    if marks is not None and not marks.empty:

        student_marks = marks[
            marks["StudentID"].astype(str) == str(reference_id)
        ].copy()

        if not student_marks.empty:

            if "MarksObtained" in student_marks.columns:

                weak_marks = student_marks[
                    student_marks["MarksObtained"] < 50
                ]

                for _, row in weak_marks.iterrows():

                    result["weak_subjects"].append({
                        "subject_id": row.get("SubjectID", ""),
                        "marks": row.get("MarksObtained", 0)
                    })

    # ---------------------------------
    # AI-generated recommendations
    # ---------------------------------

    try:
        ai_recommendations = recommend_resources(reference_id)
        if ai_recommendations:
            result["recommendations"] = _deduplicate_recommendations([
                _normalize_ai_record(item) for item in ai_recommendations
            ])
    except Exception:
        result["recommendations"] = []

    # ---------------------------------
    # Existing AI Recommendations
    # ---------------------------------

    if recommendations is not None and not recommendations.empty:

        if "StudentID" in recommendations.columns:

            student_recommendations = recommendations[
                recommendations["StudentID"].astype(str)
                == str(reference_id)
            ]

            existing_records = student_recommendations.to_dict("records")
            if existing_records and not result["recommendations"]:
                result["recommendations"] = _deduplicate_recommendations([
                    _normalize_ai_record(item) for item in existing_records
                ])

    # ---------------------------------
    # Learning Resources
    # ---------------------------------

    if resources is not None and not resources.empty:

        result["resources"] = resources.to_dict("records")

    # ---------------------------------
    # Remedial Classes
    # ---------------------------------

    if remedial is not None and not remedial.empty:

        if "StudentID" in remedial.columns:

            student_remedial = remedial[
                remedial["StudentID"].astype(str)
                == str(reference_id)
            ]

            result["remedial_classes"] = (
                student_remedial.to_dict("records")
            )

    return result

def get_student_marks(reference_id):

    marks = DataManager.get("marks")

    if marks is None or marks.empty:
        return pd.DataFrame()

    if "StudentID" not in marks.columns:
        return pd.DataFrame()

    return marks[
        marks["StudentID"].astype(str)
        == str(reference_id)
    ].copy()


def get_performance(reference_id):

    marks = get_student_marks(reference_id)

    average = 0
    highest = 0
    lowest = 0

    if not marks.empty:

        if "MarksObtained" in marks.columns:

            values = pd.to_numeric(
                marks["MarksObtained"],
                errors="coerce"
            ).dropna()

            if not values.empty:

                average = round(
                    values.mean(),
                    2
                )

                highest = values.max()
                lowest = values.min()

    return {
        "marks": marks,
        "average": average,
        "highest": highest,
        "lowest": lowest
    }


def get_analytics(reference_id):

    marks = get_student_marks(reference_id)

    subject_summary = []

    if not marks.empty:

        if (
            "SubjectID" in marks.columns
            and "MarksObtained" in marks.columns
        ):

            grouped = marks.groupby(
                "SubjectID"
            )["MarksObtained"].mean()

            for subject_id, value in grouped.items():

                subject_summary.append({
                    "SubjectID": subject_id,
                    "Average": round(
                        float(value),
                        2
                    )
                })

    return {
        "marks": marks,
        "subject_summary": subject_summary
    }