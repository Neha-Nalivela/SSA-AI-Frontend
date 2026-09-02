import json

import pandas as pd

from models.data_manager import DataManager
from services.assessment_marks_service import AssessmentMarksService


def test_submit_assessment_evaluates_and_saves_answers(monkeypatch, tmp_path):
    questions = [{
        "QuestionID": "Q1",
        "Question": "Pick the correct option",
        "Options": ["A", "B"],
        "CorrectAnswer": "1",
        "MaxMarks": 2,
    }]
    assessments = pd.DataFrame([{
        "AssessmentID": "FAC1",
        "StudentID": "S1",
        "SubjectID": "SUB1",
        "AssessmentNo": 1,
        "MaxMarks": 2,
        "MarksObtained": 0,
        "Status": "Pending",
        "AssessmentQuestions": json.dumps(questions),
        "CreatedAt": "2026-09-01T10:00:00+00:00",
    }])
    monkeypatch.setattr(AssessmentMarksService, "_assessment_file_path", lambda: str(tmp_path / "assessments.xlsx"))
    monkeypatch.setattr(DataManager, "get", lambda key: assessments if key == "assessments" else None)

    assert AssessmentMarksService.submit_assessment("S1", "FAC1", {"question_Q1": ["1"]})
    saved = DataManager.datasets["assessments"].iloc[0]
    assert saved["Status"] == "Submitted"
    assert saved["MarksObtained"] == 2
    assert json.loads(saved["Evaluation"])["CorrectAnswers"] == 1
