import pandas as pd

from services.assessment_marks_service import AssessmentMarksService


def test_sync_generated_assessments_uses_mid_marks_only(monkeypatch, tmp_path):
    marks = pd.DataFrame([
        {"StudentID": "S1", "SubjectID": "SUB1", "ExamType": "Mid-1", "MarksObtained": 10, "MaxMarks": 20},
        {"StudentID": "S1", "SubjectID": "SUB1", "ExamType": "Mid-2", "MarksObtained": 12, "MaxMarks": 20},
        {"StudentID": "S1", "SubjectID": "SUB1", "ExamType": "End Semester", "MarksObtained": 90, "MaxMarks": 100},
        {"StudentID": "S1", "SubjectID": "SUB2", "ExamType": "Mid-1", "MarksObtained": 15, "MaxMarks": 20},
    ])

    question_bank = pd.DataFrame([
        {"QuestionID": "Q1", "SubjectID": "SUB1", "QuestionType": "MCQ", "MaxMarks": 10},
        {"QuestionID": "Q2", "SubjectID": "SUB1", "QuestionType": "Objective", "MaxMarks": 10},
        {"QuestionID": "Q3", "SubjectID": "SUB1", "QuestionType": "Descriptive", "MaxMarks": 20},
        {"QuestionID": "Q4", "SubjectID": "SUB2", "QuestionType": "MCQ", "MaxMarks": 20},
    ])

    monkeypatch.setattr(
        AssessmentMarksService,
        "_assessment_file_path",
        lambda: str(tmp_path / "24_AssessmentMarks.xlsx"),
    )
    monkeypatch.setattr(
        "services.assessment_marks_service.DataManager.get",
        lambda key: {"marks": marks, "question_bank": question_bank, "assessments": pd.DataFrame()}.get(key),
    )

    rows = AssessmentMarksService.sync_generated_assessments("S1")

    assert rows
    assert all(row["SubjectID"] in {"SUB1", "SUB2"} for row in rows)
    assert all(row["MarksObtained"] <= row["MaxMarks"] for row in rows)
    assert all(row["AssessmentID"].startswith("AI_") for row in rows)

    sub1 = next(row for row in rows if row["SubjectID"] == "SUB1")
    assert sub1["MaxMarks"] > 0
    assert sub1["MarksObtained"] == 11.0
