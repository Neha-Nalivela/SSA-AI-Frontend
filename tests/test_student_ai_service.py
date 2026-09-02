import pandas as pd

from services import student_ai_service


def test_ai_recommendations_are_unique_and_have_learning_path(monkeypatch):
    monkeypatch.setattr(
        student_ai_service.DataManager,
        "get",
        lambda key: {
            "students": pd.DataFrame([{"StudentID": "S1"}]),
            "marks": pd.DataFrame(),
            "attendance": pd.DataFrame(),
            "recommendations": pd.DataFrame(),
            "resources": pd.DataFrame(),
            "remedial": pd.DataFrame(),
        }.get(key),
    )
    monkeypatch.setattr(
        student_ai_service,
        "recommend_resources",
        lambda student_id: [
            {"SubjectID": "SUB1", "Subject": "Python", "Topic": "Loops", "URL": "https://one.example"},
            {"SubjectID": "SUB1", "Subject": "Python", "Topic": "Loops", "URL": "https://two.example"},
            {"SubjectID": "SUB1", "Subject": "Python", "Topic": "Functions", "URL": "https://three.example"},
        ],
    )

    result = student_ai_service.get_ai_recommendations("S1")

    assert len(result["recommendations"]) == 2
    platforms = [item["Platform"] for item in result["recommendations"][0]["LearningPath"]]
    assert platforms == ["W3Schools", "YouTube", "GeeksforGeeks"]
    assert all(item["URL"].startswith("https://") for item in result["recommendations"][0]["LearningPath"])
