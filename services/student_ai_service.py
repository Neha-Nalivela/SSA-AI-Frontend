import pandas as pd
import re
from urllib.parse import quote_plus
from urllib.parse import urlparse

from models.data_manager import DataManager
from ml.recomendations.resource_recommender import recommend_resources
from ml.attainment.co_po_btl_analyzer import (
    analyze_co_performance,
    analyze_btl_performance,
)


def _usable_resource_url(url):
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return False
    return urlparse(url).netloc.lower() not in {"example.com", "www.example.com"}


def _learning_path(subject, topic, resource_url="", resource_title=""):
    query = quote_plus(f"{subject} {topic}")
    w3_query = quote_plus(f"site:w3schools.com {subject} {topic}")
    return [
        {
            "Platform": "W3Schools",
            "Title": f"{subject} {topic} tutorials",
            "URL": f"https://duckduckgo.com/?q={w3_query}",
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
    if _usable_resource_url(resource_url):
        learning_path[1]["Title"] = resource_title or f"{subject} {topic} resource"
        learning_path[1]["URL"] = resource_url
    return learning_path


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
    record["LearningPath"] = _learning_path(
        record["Subject"], record["Topic"], record["ResourceURL"], record["Resource"]
    )
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


def _subject_key(value):
    match = re.search(r"(\d+)", str(value))
    return match.group(1) if match else str(value).strip().lower()


def _align_student_subjects(reference_id, records):
    students = DataManager.get("students")
    subjects = DataManager.get("subjects")
    if students is None or subjects is None or students.empty or subjects.empty:
        return records

    student_rows = students[students["StudentID"].astype(str) == str(reference_id)]
    if student_rows.empty:
        return records

    student = student_rows.iloc[0]
    catalog = subjects.copy()
    if "Semester" in student.index and "Semester" in catalog.columns:
        try:
            semester = int(float(student["Semester"]))
            catalog = catalog[
                pd.to_numeric(catalog["Semester"], errors="coerce") == semester
            ]
        except (TypeError, ValueError):
            pass

    names = {
        _subject_key(row["SubjectID"]): str(row.get("SubjectName", row["SubjectID"]))
        for _, row in catalog.iterrows()
        if "SubjectID" in row
    }
    aligned = []
    for record in records:
        subject_name = names.get(_subject_key(record.get("SubjectID")))
        if subject_name is None:
            continue
        record["Subject"] = subject_name
        record["LearningPath"] = _learning_path(
            subject_name,
            record["Topic"],
            record.get("ResourceURL", ""),
            record.get("Resource", ""),
        )
        aligned.append(record)
    return aligned


def _merge_subject_recommendations(records):
    merged = {}
    for record in records:
        key = str(record.get("SubjectID") or record.get("Subject")).strip().lower()
        if key not in merged:
            record["WeakTopics"] = [record.get("Topic", "General")]
            merged[key] = record
            continue
        topic = record.get("Topic", "General")
        if topic not in merged[key]["WeakTopics"]:
            merged[key]["WeakTopics"].append(topic)
    return list(merged.values())


def _weakest_result(results, subject_id, identifier):
    subject_results = [
        item for item in results
        if str(item.get("SubjectID", "")).strip() == str(subject_id).strip()
    ]
    if not subject_results:
        return None
    return min(subject_results, key=lambda item: float(item.get("Percentage", 100) or 100))


def _subject_evidence(reference_id, subject_id, marks):
    co_result = _weakest_result(analyze_co_performance(reference_id), subject_id, "COID")
    btl_result = _weakest_result(analyze_btl_performance(reference_id), subject_id, "BTL")
    po_result = None

    co_scores = {
        item.get("COID"): item.get("Percentage")
        for item in analyze_co_performance(reference_id)
        if str(item.get("SubjectID", "")).strip() == str(subject_id).strip()
    }
    co_po = DataManager.get("co_po")
    if co_po is not None and not co_po.empty and {"COID", "POID"}.issubset(co_po.columns):
        mapped = []
        for _, mapping in co_po.iterrows():
            if str(mapping.get("SubjectID", "")).strip() != str(subject_id).strip():
                continue
            score = co_scores.get(mapping.get("COID"))
            if score is not None:
                level = pd.to_numeric(mapping.get("Level", 1), errors="coerce")
                mapped.append((str(mapping["POID"]).strip(), float(score), float(level) if pd.notna(level) else 1))
        if mapped:
            po_scores = {}
            for po_id, score, level in mapped:
                po_scores.setdefault(po_id, []).append((score, level))
            po_result = min(
                ({"POID": po_id, "Percentage": round(sum(score * level for score, level in values) / sum(level for _, level in values), 2)}
                 for po_id, values in po_scores.items()),
                key=lambda item: item["Percentage"]
            )

    subject_marks = marks[
        marks["SubjectID"].astype(str).str.strip() == str(subject_id).strip()
    ].copy() if marks is not None and not marks.empty and "SubjectID" in marks.columns else pd.DataFrame()
    latest_label = None
    latest_marks = None
    if not subject_marks.empty and "MarksObtained" in subject_marks.columns:
        if "ExamType" in subject_marks.columns:
            end_semester = subject_marks[subject_marks["ExamType"].astype(str).str.strip().str.lower() == "end semester"]
            subject_marks = end_semester if not end_semester.empty else subject_marks
            latest_label = "End Semester" if not end_semester.empty else "Latest recorded exam"
        obtained = pd.to_numeric(subject_marks["MarksObtained"], errors="coerce").sum()
        maximum = pd.to_numeric(subject_marks.get("MaxMarks", 0), errors="coerce").sum()
        if maximum > 0:
            latest_marks = f"{obtained:g}/{maximum:g} ({obtained / maximum * 100:.2f}%)"

    evidence = {
        "WeakCO": co_result.get("COID") if co_result else None,
        "WeakCOPercentage": co_result.get("Percentage") if co_result else None,
        "WeakPO": po_result.get("POID") if po_result else None,
        "WeakPOPercentage": po_result.get("Percentage") if po_result else None,
        "WeakBTL": btl_result.get("BTL") if btl_result else None,
        "WeakBTLPercentage": btl_result.get("Percentage") if btl_result else None,
        "LatestExam": latest_label,
        "LatestMarks": latest_marks,
    }
    reasons = []
    if evidence["WeakCO"]:
        reasons.append(f"CO {evidence['WeakCO']} ({evidence['WeakCOPercentage']}%)")
    if evidence["WeakPO"]:
        reasons.append(f"PO {evidence['WeakPO']} ({evidence['WeakPOPercentage']}%)")
    if evidence["WeakBTL"]:
        reasons.append(f"BTL {evidence['WeakBTL']} ({evidence['WeakBTLPercentage']}%)")
    if evidence["LatestMarks"]:
        reasons.append(f"{evidence['LatestExam']} marks {evidence['LatestMarks']}")
    evidence["WeaknessReason"] = "; ".join(reasons) or "Insufficient mapped performance data"
    return evidence


def _add_subject_evidence(reference_id, records, marks):
    evidence_cache = {}
    for record in records:
        subject_id = record.get("SubjectID") or record.get("Subject")
        if subject_id not in evidence_cache:
            evidence_cache[subject_id] = _subject_evidence(reference_id, subject_id, marks)
        record.update(evidence_cache[subject_id])
    return records


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
            result["recommendations"] = _align_student_subjects(
                reference_id, result["recommendations"]
            )
            result["recommendations"] = _merge_subject_recommendations(
                result["recommendations"]
            )
            result["recommendations"] = _add_subject_evidence(
                reference_id, result["recommendations"], marks
            )
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
                result["recommendations"] = _align_student_subjects(
                    reference_id, result["recommendations"]
                )
                result["recommendations"] = _merge_subject_recommendations(
                    result["recommendations"]
                )
                result["recommendations"] = _add_subject_evidence(
                    reference_id, result["recommendations"], marks
                )

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