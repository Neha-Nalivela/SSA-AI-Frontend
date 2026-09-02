import os
from datetime import datetime, timedelta, timezone

import pandas as pd

from config import ACADEMIC_FOLDER
from models.data_manager import DataManager


class AssessmentReportService:
    @staticmethod
    def _report_file_path():
        return os.path.join(ACADEMIC_FOLDER, "25_WeeklyAssessmentReports.xlsx")

    @staticmethod
    def _parse_date(value):
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        parsed = pd.to_datetime(value, errors="coerce", utc=True)
        return None if pd.isna(parsed) else parsed.to_pydatetime()

    @classmethod
    def generate_weekly_reports(cls, as_of=None):
        assessments = DataManager.get("assessments")
        if assessments is None or assessments.empty:
            return []

        required = {"StudentID", "SubjectID", "MarksObtained", "MaxMarks"}
        if not required.issubset(assessments.columns):
            return []

        end = as_of or datetime.now(timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        start = end - timedelta(days=7)
        data = assessments.copy()
        date_column = "CreatedAt"
        if date_column not in data.columns:
            return []
        dates = pd.to_datetime(data[date_column], errors="coerce", utc=True)
        data = data[(dates >= start) & (dates <= end)].copy()
        if data.empty:
            return []

        data["MarksObtained"] = pd.to_numeric(data["MarksObtained"], errors="coerce").fillna(0)
        data["MaxMarks"] = pd.to_numeric(data["MaxMarks"], errors="coerce").fillna(0)
        data["StudentID"] = data["StudentID"].astype(str).str.strip()
        data["SubjectID"] = data["SubjectID"].astype(str).str.strip()
        if "Status" in data.columns:
            data["Status"] = data["Status"].fillna("Completed").astype(str)
        else:
            data["Status"] = "Completed"

        rows = []
        period_start = start.date().isoformat()
        period_end = end.date().isoformat()
        for (student_id, subject_id), group in data.groupby(["StudentID", "SubjectID"]):
            completed = group[group["Status"].str.lower().isin(["completed", "submitted"])]
            total_max = float(completed["MaxMarks"].sum())
            total_obtained = float(completed["MarksObtained"].sum())
            percentage = round(total_obtained / total_max * 100, 2) if total_max else 0
            rows.append({
                "ReportID": f"WR_{student_id}_{subject_id}_{period_end}",
                "StudentID": student_id,
                "SubjectID": subject_id,
                "PeriodStart": period_start,
                "PeriodEnd": period_end,
                "AssessmentCount": len(group),
                "CompletedCount": len(completed),
                "TotalMarks": round(total_obtained, 2),
                "TotalMaxMarks": round(total_max, 2),
                "AveragePercentage": percentage,
                "GeneratedAt": end.isoformat(),
            })

        report_df = pd.DataFrame(rows)
        report_df.to_excel(cls._report_file_path(), index=False)
        DataManager.datasets["weekly_reports"] = report_df
        return rows

    @classmethod
    def get_student_weekly_reports(cls, student_id, as_of=None):
        rows = cls.generate_weekly_reports(as_of=as_of)
        student_id = str(student_id).strip()
        return [row for row in rows if str(row["StudentID"]).strip() == student_id]
