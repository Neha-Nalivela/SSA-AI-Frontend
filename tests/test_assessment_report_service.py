from datetime import datetime, timedelta, timezone

import pandas as pd

from services.assessment_report_service import AssessmentReportService
from models.data_manager import DataManager


def test_weekly_report_groups_recent_assessments(monkeypatch, tmp_path):
    now = datetime.now(timezone.utc)
    assessments = pd.DataFrame([
        {"AssessmentID": "A1", "StudentID": "S1", "SubjectID": "SUB1", "MarksObtained": 8, "MaxMarks": 10, "Status": "Completed", "CreatedAt": now.isoformat()},
        {"AssessmentID": "A2", "StudentID": "S1", "SubjectID": "SUB1", "MarksObtained": 6, "MaxMarks": 10, "Status": "Pending", "CreatedAt": (now - timedelta(days=2)).isoformat()},
        {"AssessmentID": "A3", "StudentID": "S1", "SubjectID": "SUB1", "MarksObtained": 10, "MaxMarks": 10, "Status": "Completed", "CreatedAt": (now - timedelta(days=8)).isoformat()},
    ])
    monkeypatch.setattr(DataManager, "get", lambda key: assessments if key == "assessments" else None)
    monkeypatch.setattr(AssessmentReportService, "_report_file_path", lambda: str(tmp_path / "weekly.xlsx"))

    reports = AssessmentReportService.generate_weekly_reports(as_of=now)

    assert len(reports) == 1
    assert reports[0]["AssessmentCount"] == 2
    assert reports[0]["CompletedCount"] == 1
    assert reports[0]["AveragePercentage"] == 80.0
