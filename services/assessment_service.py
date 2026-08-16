from models.data_manager import DataManager


class AssessmentService:

    # ---------------------------------------------------------
    # PERFORMANCE CLASSIFICATION
    # ---------------------------------------------------------

    @staticmethod
    def classify_score(percentage):

        if percentage < 35:
            return "Weak"

        elif percentage < 65:
            return "Average"

        elif percentage <= 80:
            return "Above Average"

        else:
            return "Good"


    # ---------------------------------------------------------
    # PERCENTAGE
    # ---------------------------------------------------------

    @staticmethod
    def calculate_percentage(
        marks_obtained,
        max_marks
    ):

        try:

            marks_obtained = float(
                marks_obtained
            )

            max_marks = float(
                max_marks
            )

            if max_marks <= 0:
                return 0

            return round(
                (marks_obtained / max_marks) * 100,
                2
            )

        except (
            ValueError,
            TypeError
        ):

            return 0


    # ---------------------------------------------------------
    # GET QUESTION BANK
    # ---------------------------------------------------------

    @staticmethod
    def get_question_bank():

        question_bank = DataManager.get(
            "question_bank"
        )

        if question_bank is None:
            return None

        return question_bank.copy()


    # ---------------------------------------------------------
    # GET STUDENT MARKS
    # ---------------------------------------------------------

    @staticmethod
    def get_student_marks(
        student_id,
        subject_id=None
    ):

        marks = DataManager.get(
            "marks"
        )

        if marks is None or marks.empty:
            return None

        data = marks[
            marks["StudentID"].astype(str)
            == str(student_id)
        ].copy()

        if subject_id is not None:

            data = data[
                data["SubjectID"].astype(str)
                == str(subject_id)
            ]

        return data


    # ---------------------------------------------------------
    # CO → PO MAPPING
    # ---------------------------------------------------------

    @staticmethod
    def get_co_po_mapping():

        mapping = DataManager.get(
            "co_po"
        )

        if mapping is None or mapping.empty:
            return {}

        result = {}

        for _, row in mapping.iterrows():

            co = str(
                row.get("COID", "")
            ).strip()

            po = str(
                row.get("POID", "")
            ).strip()

            if not co or not po:
                continue

            result.setdefault(
                co,
                []
            ).append(po)

        return result


    # ---------------------------------------------------------
    # QUESTION PERFORMANCE
    # ---------------------------------------------------------

    @classmethod
    def get_question_performance(
        cls,
        student_id,
        subject_id=None
    ):

        marks = cls.get_student_marks(
            student_id,
            subject_id
        )

        question_bank = cls.get_question_bank()

        if (
            marks is None
            or marks.empty
            or question_bank is None
            or question_bank.empty
        ):
            return []


        # Join student marks with question bank
        merged = marks.merge(
            question_bank,
            on="QuestionID",
            how="inner",
            suffixes=(
                "_mark",
                "_question"
            )
        )


        results = []

        for _, row in merged.iterrows():

            marks_obtained = row.get(
                "MarksObtained",
                0
            )

            max_marks = row.get(
                "MaxMarks_question",
                row.get(
                    "MaxMarks",
                    0
                )
            )

            percentage = (
                cls.calculate_percentage(
                    marks_obtained,
                    max_marks
                )
            )

            performance = (
                cls.classify_score(
                    percentage
                )
            )

            co = str(
                row.get(
                    "COID",
                    ""
                )
            ).strip()

            btl = str(
                row.get(
                    "BTL",
                    ""
                )
            ).strip()

            topic = str(
                row.get(
                    "Topic",
                    ""
                )
            ).strip()

            subtopic = str(
                row.get(
                    "Subtopic",
                    ""
                )
            ).strip()

            co_po_mapping = (
                cls.get_co_po_mapping()
            )

            po_list = (
                co_po_mapping.get(
                    co,
                    []
                )
            )

            results.append({

                "QuestionID":
                    row.get(
                        "QuestionID"
                    ),

                "SubjectID":
                    row.get(
                        "SubjectID_question",
                        row.get(
                            "SubjectID"
                        )
                    ),

                "Topic":
                    topic,

                "Subtopic":
                    subtopic,

                "CO":
                    co,

                "PO":
                    po_list,

                "BTL":
                    btl,

                "MarksObtained":
                    marks_obtained,

                "MaxMarks":
                    max_marks,

                "Percentage":
                    percentage,

                "Performance":
                    performance,

                "Question":
                    row.get(
                        "Question",
                        ""
                    ),

                "QuestionType":
                    row.get(
                        "QuestionType",
                        ""
                    ),

                "Difficulty":
                    row.get(
                        "Difficulty",
                        ""
                    )
            })


        return results


    # ---------------------------------------------------------
    # AREA ANALYSIS
    # ---------------------------------------------------------

    @staticmethod
    def analyze_area(
        records,
        field
    ):

        areas = {}

        for record in records:

            value = record.get(
                field
            )

            if isinstance(
                value,
                list
            ):

                values = value

            else:

                values = [value]


            for area in values:

                area = str(
                    area
                ).strip()

                if not area:
                    continue

                if area not in areas:

                    areas[area] = []

                areas[area].append(
                    record["Percentage"]
                )


        result = []

        for area, scores in areas.items():

            average = round(
                sum(scores) / len(scores),
                2
            )

            result.append({

                "Name":
                    area,

                "Average":
                    average,

                "Category":
                    AssessmentService.classify_score(
                        average
                    )
            })


        return result


    # ---------------------------------------------------------
    # COMPLETE SUBJECT ANALYSIS
    # ---------------------------------------------------------

    @classmethod
    def analyze_subject(
        cls,
        student_id,
        subject_id
    ):

        records = cls.get_question_performance(
            student_id,
            subject_id
        )

        if not records:

            return {

                "SubjectID":
                    subject_id,

                "Average":
                    0,

                "Category":
                    "No Data",

                "Topics":
                    [],

                "CO":
                    [],

                "PO":
                    [],

                "BTL":
                    [],

                "WeakTopics":
                    [],

                "StrongTopics":
                    [],

                "WeakCO":
                    [],

                "StrongCO":
                    [],

                "WeakPO":
                    [],

                "StrongPO":
                    [],

                "WeakBTL":
                    [],

                "StrongBTL":
                    [],

                "Questions":
                    []
            }


        overall_average = round(
            sum(
                r["Percentage"]
                for r in records
            )
            /
            len(records),
            2
        )


        topics = cls.analyze_area(
            records,
            "Topic"
        )

        co = cls.analyze_area(
            records,
            "CO"
        )

        po = cls.analyze_area(
            records,
            "PO"
        )

        btl = cls.analyze_area(
            records,
            "BTL"
        )


        def weak(items):

            return [
                item
                for item in items
                if item["Average"] < 65
            ]


        def strong(items):

            return [
                item
                for item in items
                if item["Average"] >= 65
            ]


        return {

            "SubjectID":
                subject_id,

            "Average":
                overall_average,

            "Category":
                cls.classify_score(
                    overall_average
                ),

            "Topics":
                topics,

            "CO":
                co,

            "PO":
                po,

            "BTL":
                btl,

            "WeakTopics":
                weak(topics),

            "StrongTopics":
                strong(topics),

            "WeakCO":
                weak(co),

            "StrongCO":
                strong(co),

            "WeakPO":
                weak(po),

            "StrongPO":
                strong(po),

            "WeakBTL":
                weak(btl),

            "StrongBTL":
                strong(btl),

            "Questions":
                records
        }


    # ---------------------------------------------------------
    # GENERATE AI ASSESSMENT
    # ---------------------------------------------------------

    @classmethod
    def generate_assessment(
        cls,
        student_id,
        subject_id,
        number_of_questions=10
    ):

        analysis = cls.analyze_subject(
            student_id,
            subject_id
        )

        question_bank = (
            cls.get_question_bank()
        )

        if (
            question_bank is None
            or question_bank.empty
        ):
            return []


        # Only active questions
        if "Status" in question_bank.columns:

            question_bank = question_bank[
                question_bank["Status"]
                .astype(str)
                .str.lower()
                == "active"
            ]


        # -----------------------------------------------------
        # WEAK AREAS
        # -----------------------------------------------------

        weak_topics = {
            item["Name"]
            for item in analysis[
                "WeakTopics"
            ]
        }

        weak_co = {
            item["Name"]
            for item in analysis[
                "WeakCO"
            ]
        }

        weak_btl = {
            item["Name"]
            for item in analysis[
                "WeakBTL"
            ]
        }

        weak_po = {
            item["Name"]
            for item in analysis[
                "WeakPO"
            ]
        }


        # -----------------------------------------------------
        # STRONG AREAS
        # -----------------------------------------------------

        strong_topics = {
            item["Name"]
            for item in analysis[
                "StrongTopics"
            ]
        }

        strong_co = {
            item["Name"]
            for item in analysis[
                "StrongCO"
            ]
        }

        strong_btl = {
            item["Name"]
            for item in analysis[
                "StrongBTL"
            ]
        }

        strong_po = {
            item["Name"]
            for item in analysis[
                "StrongPO"
            ]
        }


        weak_questions = []
        strong_questions = []
        other_questions = []


        # -----------------------------------------------------
        # SCORE EACH QUESTION
        # -----------------------------------------------------

        for _, row in question_bank.iterrows():

            if str(
                row.get(
                    "SubjectID",
                    ""
                )
            ) != str(subject_id):

                continue


            question = row.to_dict()

            topic = str(
                row.get(
                    "Topic",
                    ""
                )
            ).strip()

            co = str(
                row.get(
                    "COID",
                    ""
                )
            ).strip()

            btl = str(
                row.get(
                    "BTL",
                    ""
                )
            ).strip()


            co_po_mapping = (
                cls.get_co_po_mapping()
            )

            po_values = set(
                co_po_mapping.get(
                    co,
                    []
                )
            )


            # Weak area score
            weak_score = 0

            if topic in weak_topics:
                weak_score += 3

            if co in weak_co:
                weak_score += 3

            if btl in weak_btl:
                weak_score += 2

            if po_values & weak_po:
                weak_score += 2


            # Strong area score
            strong_score = 0

            if topic in strong_topics:
                strong_score += 3

            if co in strong_co:
                strong_score += 3

            if btl in strong_btl:
                strong_score += 2

            if po_values & strong_po:
                strong_score += 2


            if weak_score > 0:

                question[
                    "_selection_score"
                ] = weak_score

                weak_questions.append(
                    question
                )

            elif strong_score > 0:

                question[
                    "_selection_score"
                ] = strong_score

                strong_questions.append(
                    question
                )

            else:

                question[
                    "_selection_score"
                ] = 0

                other_questions.append(
                    question
                )


        # Highest relevance first
        weak_questions.sort(
            key=lambda x:
                x["_selection_score"],
            reverse=True
        )

        strong_questions.sort(
            key=lambda x:
                x["_selection_score"],
            reverse=True
        )


        # -----------------------------------------------------
        # 80 / 20 DISTRIBUTION
        # -----------------------------------------------------

        weak_count = round(
            number_of_questions * 0.8
        )

        strong_count = (
            number_of_questions
            - weak_count
        )


        selected = []

        selected.extend(
            weak_questions[
                :weak_count
            ]
        )

        selected.extend(
            strong_questions[
                :strong_count
            ]
        )


        # If not enough questions,
        # fill from remaining questions.
        if len(selected) < number_of_questions:

            remaining = (
                weak_questions[weak_count:]
                +
                strong_questions[strong_count:]
                +
                other_questions
            )

            for question in remaining:

                if len(selected) >= number_of_questions:
                    break

                selected.append(
                    question
                )


        # Remove internal scoring field
        for question in selected:

            question.pop(
                "_selection_score",
                None
            )


        return selected[
            :number_of_questions
        ]