import pandas as pd

from services.student_performance_service import build_subject_performance_summary


def test_build_subject_performance_summary_includes_exam_breakdown_and_cgpa():
    marks = pd.DataFrame([
        {"SubjectID": "S001", "ExamType": "Mid-1", "MarksObtained": 15, "MaxMarks": 20},
        {"SubjectID": "S001", "ExamType": "Mid-1", "MarksObtained": 10, "MaxMarks": 20},
        {"SubjectID": "S001", "ExamType": "Mid-2", "MarksObtained": 12, "MaxMarks": 20},
        {"SubjectID": "S001", "ExamType": "End Semester", "MarksObtained": 50, "MaxMarks": 100},
        {"SubjectID": "S002", "ExamType": "Mid-1", "MarksObtained": 16, "MaxMarks": 20},
        {"SubjectID": "S002", "ExamType": "End Semester", "MarksObtained": 75, "MaxMarks": 100},
    ])

    summary = build_subject_performance_summary(marks)

    s1 = next(item for item in summary if item["SubjectID"] == "S001")
    s2 = next(item for item in summary if item["SubjectID"] == "S002")

    assert s1["Mid-1"] == 62.5
    assert s1["Mid-2"] == 60.0
    assert s1["End Semester"] == 50.0
    assert s1["OverallPercent"] == 54.38
    assert s1["CGPA"] == 5.44

    assert s2["Mid-1"] == 80.0
    assert s2["End Semester"] == 75.0
    assert s2["OverallPercent"] == 75.83
    assert s2["CGPA"] == 7.58
