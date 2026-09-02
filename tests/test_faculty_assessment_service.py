import pandas as pd

from services.assessment_marks_service import AssessmentMarksService


def test_faculty_assessment_uses_only_subject_question_bank(monkeypatch, tmp_path):
    question_bank = pd.DataFrame([
        {"QuestionID": "Q1", "SubjectID": "SUB1", "Question": "Choose one", "QuestionType": "MCQ", "MaxMarks": 1, "Status": "Active"},
        {"QuestionID": "Q2", "SubjectID": "SUB2", "Question": "Other subject", "QuestionType": "MCQ", "MaxMarks": 1, "Status": "Active"},
    ])
    monkeypatch.setattr(
        AssessmentMarksService,
        "_assessment_file_path",
        lambda: str(tmp_path / "assessments.xlsx"),
    )
    monkeypatch.setattr(
        "services.assessment_marks_service.DataManager.get",
        lambda key: {"question_bank": question_bank, "assessments": pd.DataFrame()}.get(key),
    )

    prepared = AssessmentMarksService.prepare_faculty_assessment("F1", "S1", "SUB1")

    assert prepared["Status"] == "Pending"
    assert prepared["PreparedBy"] == "F1"
    assert [item["QuestionID"] for item in prepared["Questions"]] == ["Q1"]
    assert len(prepared["Questions"][0]["Options"]) == 4
