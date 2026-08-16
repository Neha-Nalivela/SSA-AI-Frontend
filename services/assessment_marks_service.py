from models.data_manager import DataManager


class AssessmentMarksService:

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
            "assessment_marks"
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

            })

        return results


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

        return results