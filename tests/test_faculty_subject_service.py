import pandas as pd

from services.faculty_subject_service import _build_student_summary


def test_build_student_summary_aggregates_mid_exam_marks_and_average():
    subject = {"SubjectID": "S001"}
    marks = pd.DataFrame(
        [
            {"StudentID": "S1", "ExamType": "Mid-1", "MarksObtained": 8, "MaxMarks": 10},
            {"StudentID": "S1", "ExamType": "Mid-1", "MarksObtained": 6, "MaxMarks": 10},
            {"StudentID": "S1", "ExamType": "Mid-2", "MarksObtained": 7, "MaxMarks": 10},
            {"StudentID": "S2", "ExamType": "Mid-2", "MarksObtained": 5, "MaxMarks": 10},
        ]
    )

    _, summary = _build_student_summary(subject, marks, ["Mid-1", "Mid-2"])

    assert summary.loc[summary["StudentID"] == "S1", "Mid-1"].iloc[0] == 14
    assert summary.loc[summary["StudentID"] == "S1", "Mid-2"].iloc[0] == 7
    assert summary.loc[summary["StudentID"] == "S1", "Average"].iloc[0] == 10.5
    assert summary.loc[summary["StudentID"] == "S2", "Mid-1"].iloc[0] == 0
    assert summary.loc[summary["StudentID"] == "S2", "Mid-2"].iloc[0] == 5
