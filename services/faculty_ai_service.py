import re

from models.data_manager import DataManager
from ml.recomendations.resource_recommender import recommend_resources


def _normalize_subject_key(value):
    text = str(value).strip()
    match = re.search(r"(\d+)", text)
    return match.group(1) if match else text


def _subject_matches(subject_id, candidate):
    left = str(subject_id or "").strip()
    right = str(candidate or "").strip()
    return left == right or _normalize_subject_key(left) == _normalize_subject_key(right)


def get_faculty_ai_recommendations(reference_id):
    subjects = DataManager.get("subjects")
    marks = DataManager.get("marks")

    if subjects is None or subjects.empty:
        return {"subjects": []}

    faculty_subjects = subjects[
        subjects["FacultyID"].astype(str).str.strip() == str(reference_id).strip()
    ].copy()

    if faculty_subjects.empty:
        return {"subjects": []}

    result = {"subjects": []}

    for _, subject in faculty_subjects.iterrows():
        subject_id = str(subject.get("SubjectID", "")).strip()
        subject_name = str(subject.get("SubjectName", subject_id))

        student_ids = []
        if marks is not None and not marks.empty and "StudentID" in marks.columns:
            for student_id in marks["StudentID"].astype(str).str.strip().unique():
                if student_id:
                    student_marks = marks[
                        marks["StudentID"].astype(str).str.strip() == student_id
                    ]
                    if not student_marks.empty and any(
                        _subject_matches(subject_id, row)
                        for row in student_marks["SubjectID"].astype(str).str.strip().tolist()
                    ):
                        student_ids.append(student_id)

        recommendations = []
        seen = set()

        for student_id in sorted(set(student_ids)):
            try:
                for item in recommend_resources(student_id):
                    if not _subject_matches(subject_id, item.get("SubjectID")):
                        continue

                    key = (
                        str(item.get("SubjectID", "")),
                        str(item.get("Topic", "")),
                        str(item.get("Priority", ""))
                    )
                    if key in seen:
                        continue
                    seen.add(key)

                    recommendations.append({
                        "StudentID": student_id,
                        "Subject": item.get("Subject") or subject_name,
                        "SubjectID": item.get("SubjectID") or subject_id,
                        "Topic": item.get("Topic") or "General",
                        "Priority": item.get("Priority") or "Medium",
                        "Reason": item.get("Reason") or "AI-based remedial suggestion",
                        "ResourceTitle": item.get("ResourceTitle") or item.get("Resource") or "Learning resource",
                        "ResourceURL": item.get("URL") or item.get("ResourceURL") or "",
                    })
            except Exception:
                continue

        result["subjects"].append({
            "subject_id": subject_id,
            "subject_name": subject_name,
            "student_count": len(student_ids),
            "ai_recommendations": recommendations[:10],
        })

    return result
