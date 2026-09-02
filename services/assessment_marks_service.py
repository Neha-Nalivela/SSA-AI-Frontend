import os
import json
import re

import pandas as pd

from config import ACADEMIC_FOLDER
from models.data_manager import DataManager


class AssessmentMarksService:

    @staticmethod
    def _assessment_file_path():
        return os.path.join(ACADEMIC_FOLDER, "24_AssessmentMarks.xlsx")

    @staticmethod
    def _ensure_assessment_df():
        assessments = DataManager.get("assessments")
        if assessments is None or assessments.empty:
            file_path = AssessmentMarksService._assessment_file_path()
            if os.path.exists(file_path):
                try:
                    assessments = pd.read_excel(file_path)
                except Exception:
                    assessments = pd.DataFrame()
            else:
                assessments = pd.DataFrame()
        return assessments.copy()

    @staticmethod
    def _generate_unique_assessment_id(student_id, subject_id, count):
        return f"AI_{student_id}_{subject_id}_{count}"

    @staticmethod
    def _question_bank_items(subject_id, number_of_questions):
        question_bank = DataManager.get("question_bank")
        if question_bank is None or question_bank.empty or "SubjectID" not in question_bank.columns:
            return []
        data = question_bank.copy()
        subject_key_match = re.search(r"(\d+)", str(subject_id))
        subject_key = subject_key_match.group(1) if subject_key_match else str(subject_id).strip()
        question_subject_keys = data["SubjectID"].astype(str).str.extract(r"(\d+)", expand=False).fillna(
            data["SubjectID"].astype(str).str.strip()
        )
        data = data[question_subject_keys == subject_key]
        if "Status" in data.columns:
            active = data[data["Status"].astype(str).str.strip().str.lower() == "active"]
            if not active.empty:
                data = active
        if "QuestionType" in data.columns:
            types = data["QuestionType"].astype(str).str.strip()
            mcq = types.str.contains("MCQ|Objective|Multiple Choice|Quiz|True|False|Fill", case=False, na=False)
            if mcq.any():
                data = data[mcq]
            else:
                objective_fallback = data[
                    ~types.str.contains("Descriptive|Programming|Case Study|Essay|Long Answer", case=False, na=False)
                ]
                if not objective_fallback.empty:
                    data = objective_fallback
        questions = data.head(number_of_questions).to_dict(orient="records")
        option_columns = ["OptionA", "OptionB", "OptionC", "OptionD"]
        for question in questions:
            options = [
                str(question[column]).strip()
                for column in option_columns
                if column in question and pd.notna(question[column]) and str(question[column]).strip()
            ]
            question["Options"] = options or ["Option A", "Option B", "Option C", "Option D"]
        return questions

    @classmethod
    def prepare_faculty_assessment(cls, faculty_id, student_id, subject_id, number_of_questions=10):
        """Create a pending assessment using only the assigned subject's question bank."""
        from services.assessment_service import AssessmentService

        questions = cls._question_bank_items(subject_id, number_of_questions)
        if not questions:
            return None

        assessments = cls._ensure_assessment_df()
        student_id = str(student_id).strip()
        subject_id = str(subject_id).strip()
        existing = assessments[
            (assessments.get("StudentID", pd.Series(dtype=str)).astype(str).str.strip() == student_id)
            & (assessments.get("SubjectID", pd.Series(dtype=str)).astype(str).str.strip() == subject_id)
        ] if not assessments.empty else pd.DataFrame()
        assessment_no = len(existing) + 1
        assessment_id = f"FAC_{faculty_id}_{student_id}_{subject_id}_{assessment_no}"
        row = {
            "AssessmentID": assessment_id,
            "StudentID": student_id,
            "SubjectID": subject_id,
            "AssessmentNo": assessment_no,
            "MaxMarks": sum(float(item.get("MaxMarks", 0) or 0) for item in questions),
            "MarksObtained": 0,
            "Status": "Pending",
            "PreparedBy": str(faculty_id),
            "AssessmentQuestions": json.dumps(questions, default=str),
            "Source": "faculty_question_bank",
        }
        row["Questions"] = questions
        assessments = pd.concat([assessments, pd.DataFrame([row])], ignore_index=True)
        file_path = cls._assessment_file_path()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        assessments.to_excel(file_path, index=False)
        DataManager.datasets["assessments"] = assessments
        return row

    @classmethod
    def sync_generated_assessments(cls, student_id):
        student_id = str(student_id).strip()
        if not student_id:
            return []

        marks = DataManager.get("marks")
        question_bank = DataManager.get("question_bank")
        if marks is None or marks.empty or question_bank is None or question_bank.empty:
            return []

        if "StudentID" not in marks.columns:
            return []
        if "SubjectID" not in marks.columns or "ExamType" not in marks.columns:
            return []
        if "SubjectID" not in question_bank.columns:
            return []

        mid_marks = marks[
            (marks["StudentID"].astype(str).str.strip() == student_id)
            & (marks["ExamType"].astype(str).str.strip().isin(["Mid-1", "Mid-2"]))
        ].copy()

        if mid_marks.empty:
            return []

        if "MarksObtained" not in mid_marks.columns or "MaxMarks" not in mid_marks.columns:
            return []

        mid_marks["MarksObtained"] = pd.to_numeric(mid_marks["MarksObtained"], errors="coerce").fillna(0)
        mid_marks["MaxMarks"] = pd.to_numeric(mid_marks["MaxMarks"], errors="coerce").fillna(0)

        assessments = cls._ensure_assessment_df()
        if not assessments.empty:
            assessments["StudentID"] = assessments["StudentID"].astype(str).str.strip()
            assessments["SubjectID"] = assessments["SubjectID"].astype(str).str.strip()

        generated_rows = []
        used_subjects = set()

        if not assessments.empty:
            existing_generated = assessments[
                (assessments["StudentID"].astype(str).str.strip() == student_id)
                & (assessments["AssessmentID"].astype(str).str.startswith("AI_"))
            ]
            used_subjects = set(existing_generated["SubjectID"].astype(str).str.strip().tolist())

        for subject_id in sorted(mid_marks["SubjectID"].astype(str).str.strip().unique()):
            if not subject_id or subject_id in used_subjects:
                continue

            subject_marks = mid_marks[mid_marks["SubjectID"].astype(str).str.strip() == subject_id].copy()
            if subject_marks.empty:
                continue

            subject_max = float(subject_marks["MaxMarks"].sum())
            subject_obtained = float(subject_marks["MarksObtained"].sum())
            percentage = round((subject_obtained / subject_max * 100) if subject_max else 0, 2)

            qb = question_bank.copy()
            qb["SubjectID"] = qb["SubjectID"].astype(str).str.strip()
            if "QuestionType" in qb.columns:
                qb["QuestionType"] = qb["QuestionType"].astype(str).str.strip()
            qb = qb[qb["SubjectID"] == subject_id]

            if "Status" in qb.columns:
                qb = qb[qb["Status"].astype(str).str.strip().str.lower() == "active"]

            if "QuestionType" in qb.columns:
                qb = qb[
                    ~qb["QuestionType"].str.contains("Descriptive|Programming|Case Study|Long Answer|Essay", case=False, na=False)
                ]

            if "QuestionType" in qb.columns:
                qb = qb[
                    qb["QuestionType"].str.contains("MCQ|Objective|Multiple Choice|Quiz|Fill in the Blanks|True|False|Short Answer", case=False, na=False)
                    | (~qb["QuestionType"].fillna("").astype(str).str.contains("Descriptive|Programming|Case Study|Long Answer|Essay", case=False, na=False))
                ]

            if qb.empty:
                qb = question_bank.copy()
                qb["SubjectID"] = qb["SubjectID"].astype(str).str.strip()
                if "QuestionType" in qb.columns:
                    qb["QuestionType"] = qb["QuestionType"].astype(str).str.strip()
                qb = qb[qb["SubjectID"] == subject_id]

            if qb.empty:
                continue

            if "MaxMarks" not in qb.columns:
                continue

            selected = qb.head(10).copy()
            if selected.empty:
                continue

            max_marks = float(selected["MaxMarks"].fillna(0).astype(float).sum())
            generated_marks = round((percentage / 100) * max_marks, 2) if max_marks else 0.0

            generated_rows.append({
                "AssessmentID": cls._generate_unique_assessment_id(student_id, subject_id, len(generated_rows) + 1),
                "StudentID": student_id,
                "SubjectID": subject_id,
                "AssessmentNo": f"AI-{subject_id}-Mid",
                "MaxMarks": round(max_marks, 2),
                "MarksObtained": round(generated_marks, 2),
                "QuestionCount": len(selected),
                "Source": "question_bank_mid",
            })

        if not generated_rows:
            return []

        if assessments.empty:
            assessments = pd.DataFrame(generated_rows)
        else:
            assessments = pd.concat([assessments, pd.DataFrame(generated_rows)], ignore_index=True)

        assessments = assessments.drop_duplicates(subset=["AssessmentID"], keep="last")
        file_path = cls._assessment_file_path()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        assessments.to_excel(file_path, index=False)
        DataManager.datasets["assessments"] = assessments
        return generated_rows

    @classmethod
    def generate_next_assessment(cls, student_id, subject_id=None, number_of_questions=10):
        completed = cls.get_completed_assessments(student_id)
        if subject_id is None and completed:
            subject_id = min(
                completed,
                key=lambda item: float(item.get("Percentage", 0))
            )["SubjectID"]

        if subject_id is None:
            marks = DataManager.get("marks")
            if marks is None or marks.empty:
                return None
            mid_marks = marks[
                (marks["StudentID"].astype(str).str.strip() == str(student_id).strip())
                & marks["ExamType"].astype(str).str.strip().isin(["Mid-1", "Mid-2"])
            ]
            if mid_marks.empty:
                return None
            subject_scores = mid_marks.groupby("SubjectID").agg(
                obtained=("MarksObtained", "sum"),
                maximum=("MaxMarks", "sum")
            )
            subject_id = str((subject_scores["obtained"] / subject_scores["maximum"]).idxmin())

        questions = cls._question_bank_items(subject_id, number_of_questions)
        if not questions:
            return None

        next_number = len([item for item in completed if str(item["SubjectID"]) == str(subject_id)]) + 1
        return {
            "SubjectID": str(subject_id),
            "AssessmentNo": next_number,
            "Questions": questions,
            "BasedOnAssessments": len(completed),
        }

    @classmethod
    def get_performance_summary(cls, student_id):

        assessments = cls.get_student_assessments(student_id)

        if not assessments:
            return {
                "assessments": [],
                "average": 0,
                "category": "No Data"
            }

        percentages = [
            float(item["Percentage"])
            for item in assessments
        ]

        average = round(
            sum(percentages) / len(percentages),
            2
        )

        category = cls.category(average)

        return {
            "assessments": assessments,
            "average": average,
            "category": category
        }

    @staticmethod
    def percentage(obtained, maximum):

        try:
            obtained = float(obtained)
            maximum = float(maximum)

            if maximum <= 0:
                return 0

            return round(
                (obtained / maximum) * 100,
                2
            )

        except (ValueError, TypeError):
            return 0


    @staticmethod
    def category(score):

        if score < 35:
            return "Weak"

        elif score < 65:
            return "Average"

        elif score <= 80:
            return "Above Average"

        return "Good"


    @classmethod
    def get_student_assessments(
        cls,
        student_id,
        subject_id=None
    ):

        df = DataManager.get(
            "assessments"
        )
        print("================================")
        print("ASSESSMENT DEBUG")
        print("Student ID:", student_id)
        print("Assessment Data:")
        print(df)
        print("================================")

        if df is None or df.empty:
            return []

        data = df[
            df["StudentID"].astype(str)
            == str(student_id)
        ].copy()

        if subject_id is not None:

            data = data[
                data["SubjectID"].astype(str)
                == str(subject_id)
            ]

        results = []

        for _, row in data.iterrows():

            percentage = cls.percentage(
                row["MarksObtained"],
                row["MaxMarks"]
            )

            results.append({

                "AssessmentID":
                    row["AssessmentID"],

                "StudentID":
                    row["StudentID"],

                "SubjectID":
                    row["SubjectID"],

                "AssessmentNo":
                    row["AssessmentNo"],

                "MaxMarks":
                    row["MaxMarks"],

                "MarksObtained":
                    row["MarksObtained"],

                "Percentage":
                    percentage,

                "Category":
                    cls.category(percentage)

                ,"Status": row.get("Status", "Completed")

                ,"Questions": cls._decode_questions(row.get("AssessmentQuestions", ""))

            })

        return results

    @staticmethod
    def _decode_questions(value):
        if not value or not isinstance(value, str):
            return []
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return []

    @classmethod
    def get_completed_assessments(cls, student_id):
        return [
            item for item in cls.get_student_assessments(student_id)
            if str(item.get("Status", "Completed")).strip().lower() == "completed"
        ]

    @classmethod
    def get_pending_assessments(cls, student_id):
        return [
            item for item in cls.get_student_assessments(student_id)
            if str(item.get("Status", "Completed")).strip().lower() in {"pending", "submitted"}
        ]

    @classmethod
    def submit_assessment(cls, student_id, assessment_id, selected_answers):
        assessments = cls._ensure_assessment_df()
        if assessments.empty or "AssessmentID" not in assessments.columns:
            return False
        match = (
            assessments["AssessmentID"].astype(str).str.strip() == str(assessment_id).strip()
        ) & (
            assessments["StudentID"].astype(str).str.strip() == str(student_id).strip()
        )
        if not match.any():
            return False
        index = assessments.index[match][0]
        assessments.loc[index, "SelectedAnswers"] = json.dumps(selected_answers)
        assessments.loc[index, "Status"] = "Submitted"
        file_path = cls._assessment_file_path()
        assessments.to_excel(file_path, index=False)
        DataManager.datasets["assessments"] = assessments
        return True


    @classmethod
    def get_subject_summary(
        cls,
        student_id
    ):

        assessments = cls.get_student_assessments(
            student_id
        )

        if not assessments:
            return []

        subjects = {}

        for assessment in assessments:

            subject = str(
                assessment["SubjectID"]
            )

            if subject not in subjects:

                subjects[subject] = {
                    "total_obtained": 0,
                    "total_max": 0,
                    "count": 0
                }

            subjects[subject][
                "total_obtained"
            ] += float(
                assessment["MarksObtained"]
            )

            subjects[subject][
                "total_max"
            ] += float(
                assessment["MaxMarks"]
            )

            subjects[subject][
                "count"
            ] += 1

        results = []

        for subject, values in subjects.items():

            percentage = cls.percentage(
                values["total_obtained"],
                values["total_max"]
            )

            results.append({

                "SubjectID":
                    subject,

                "AssessmentCount":
                    values["count"],

                "MarksObtained":
         
                    values["total_obtained"],

                "MaxMarks":
                    values["total_max"],

                "Percentage":
                    percentage,

                "Category":
                    cls.category(percentage)

            })
