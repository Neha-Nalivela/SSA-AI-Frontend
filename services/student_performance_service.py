import pandas as pd

from models.data_manager import DataManager
from services.assessment_service import AssessmentService

def get_student(reference_id):

    students = DataManager.get("students")

    if students is None or students.empty:
        return None

    if "StudentID" not in students.columns:
        return None

    student_rows = students[
        students["StudentID"].astype(str)
        == str(reference_id)
    ]

    if student_rows.empty:
        return None

    return student_rows.iloc[0]

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
    student = get_student(reference_id)
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

        # Student information
        "student": student,

        # Marks
        "marks": marks,

        # Overall statistics
        "average": average,

        "highest": highest,

        "lowest": lowest

    }

def get_analytics(reference_id):

    marks = get_student_marks(reference_id)

    subject_summary = []
    assessment_analysis = []

    if not marks.empty:

        if (
            "SubjectID" in marks.columns
            and "MarksObtained" in marks.columns
        ):

            grouped = marks.groupby(
                "SubjectID"
            )["MarksObtained"].mean()

            for subject_id, value in grouped.items():

                average_marks = round(
                    float(value),
                    2
                )

                # ---------------------------------------------
                # CONVERT AVERAGE MARKS TO PERCENTAGE
                # Assuming marks are out of 10
                # ---------------------------------------------

                percentage = round(
                    (average_marks / 10) * 100,
                    2
                )

                # ---------------------------------------------
                # PERFORMANCE CATEGORY
                # ---------------------------------------------

                if percentage < 35:

                    category = "Weak"

                elif percentage < 65:

                    category = "Average"

                elif percentage <= 80:

                    category = "Above Average"

                else:

                    category = "Good"


                # ---------------------------------------------
                # QUESTION-LEVEL ANALYSIS
                # ---------------------------------------------

                analysis = AssessmentService.analyze_subject(
                    reference_id,
                    subject_id
                )


                # ---------------------------------------------
                # WEAK AREAS
                # ---------------------------------------------

                weak_topics = [
                    item["Name"]
                    for item in analysis.get(
                        "WeakTopics",
                        []
                    )
                ]

                weak_co = [
                    item["Name"]
                    for item in analysis.get(
                        "WeakCO",
                        []
                    )
                ]

                weak_po = [
                    item["Name"]
                    for item in analysis.get(
                        "WeakPO",
                        []
                    )
                ]

                weak_btl = [
                    item["Name"]
                    for item in analysis.get(
                        "WeakBTL",
                        []
                    )
                ]


                # ---------------------------------------------
                # STRONG AREAS
                # ---------------------------------------------

                strong_topics = [
                    item["Name"]
                    for item in analysis.get(
                        "StrongTopics",
                        []
                    )
                ]

                strong_co = [
                    item["Name"]
                    for item in analysis.get(
                        "StrongCO",
                        []
                    )
                ]

                strong_po = [
                    item["Name"]
                    for item in analysis.get(
                        "StrongPO",
                        []
                    )
                ]

                strong_btl = [
                    item["Name"]
                    for item in analysis.get(
                        "StrongBTL",
                        []
                    )
                ]


                # ---------------------------------------------
                # SUBJECT SUMMARY
                # ---------------------------------------------

                subject_summary.append({

                    "SubjectID":
                        subject_id,

                    "Average":
                        average_marks,

                    "Percentage":
                        percentage,

                    "Category":
                        category,

                    "weak_topics":
                        weak_topics,

                    "strong_topics":
                        strong_topics,

                    "weak_co":
                        weak_co,

                    "strong_co":
                        strong_co,

                    "weak_po":
                        weak_po,

                    "strong_po":
                        strong_po,

                    "weak_btl":
                        weak_btl,

                    "strong_btl":
                        strong_btl
                })


                # ---------------------------------------------
                # COMPLETE ASSESSMENT ANALYSIS
                # ---------------------------------------------

                assessment_analysis.append({

                    "SubjectID":
                        subject_id,

                    "Average":
                        average_marks,

                    "Percentage":
                        percentage,

                    "Category":
                        category,

                    "Topics":
                        analysis.get(
                            "Topics",
                            []
                        ),

                    "CO":
                        analysis.get(
                            "CO",
                            []
                        ),

                    "PO":
                        analysis.get(
                            "PO",
                            []
                        ),

                    "BTL":
                        analysis.get(
                            "BTL",
                            []
                        ),

                    "WeakTopics":
                        analysis.get(
                            "WeakTopics",
                            []
                        ),

                    "StrongTopics":
                        analysis.get(
                            "StrongTopics",
                            []
                        ),

                    "WeakCO":
                        analysis.get(
                            "WeakCO",
                            []
                        ),

                    "StrongCO":
                        analysis.get(
                            "StrongCO",
                            []
                        ),

                    "WeakPO":
                        analysis.get(
                            "WeakPO",
                            []
                        ),

                    "StrongPO":
                        analysis.get(
                            "StrongPO",
                            []
                        ),

                    "WeakBTL":
                        analysis.get(
                            "WeakBTL",
                            []
                        ),

                    "StrongBTL":
                        analysis.get(
                            "StrongBTL",
                            []
                        )
                })


    return {

        "marks":
            marks,

        "subject_summary":
            subject_summary,

        "assessment_analysis":
            assessment_analysis
    }