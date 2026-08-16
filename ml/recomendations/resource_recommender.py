from models.data_manager import DataManager

from ml.subjects.weak_subject_detector import (
    detect_weak_subjects
)

from ml.attainment.co_po_btl_analyzer import (
    analyze_co_performance,
    analyze_btl_performance,
    analyze_topic_performance
)


# ============================================================
# FALLBACK RESOURCE DATABASE
# ============================================================

RESOURCE_DATABASE = {

    "Mathematics I": {

        "Concepts": [
            {
                "type": "Video",
                "title": "Mathematics I - Fundamental Concepts",
                "source": "YouTube",
                "url": "https://www.youtube.com/results?search_query=engineering+mathematics+fundamental+concepts"
            },
            {
                "type": "Book",
                "title": "Higher Engineering Mathematics",
                "source": "B.S. Grewal",
                "url": ""
            }
        ],

        "Applications": [
            {
                "type": "Video",
                "title": "Engineering Mathematics Applications",
                "source": "YouTube",
                "url": "https://www.youtube.com/results?search_query=engineering+mathematics+applications"
            }
        ]
    },


    "Mathematics II": {

        "Concepts": [
            {
                "type": "Video",
                "title": "Engineering Mathematics II - Basic Concepts",
                "source": "YouTube",
                "url": "https://www.youtube.com/results?search_query=engineering+mathematics+2+basic+concepts"
            },
            {
                "type": "Book",
                "title": "Higher Engineering Mathematics",
                "source": "B.S. Grewal",
                "url": ""
            }
        ],

        "Applications": [
            {
                "type": "Video",
                "title": "Engineering Mathematics II - Applications",
                "source": "YouTube",
                "url": "https://www.youtube.com/results?search_query=engineering+mathematics+2+applications"
            }
        ]
    },


    "Physics": {

        "Concepts": [
            {
                "type": "Video",
                "title": "Engineering Physics - Core Concepts",
                "source": "YouTube",
                "url": "https://www.youtube.com/results?search_query=engineering+physics+basic+concepts"
            },
            {
                "type": "Book",
                "title": "Engineering Physics",
                "source": "S. Mani Naidu",
                "url": ""
            }
        ]
    },


    "Chemistry": {

        "Concepts": [
            {
                "type": "Video",
                "title": "Engineering Chemistry - Basic Concepts",
                "source": "YouTube",
                "url": "https://www.youtube.com/results?search_query=engineering+chemistry+basic+concepts"
            },
            {
                "type": "Book",
                "title": "Engineering Chemistry",
                "source": "Jain & Jain",
                "url": ""
            }
        ]
    },


    "Programming for Problem Solving": {

        "Concepts": [
            {
                "type": "Video",
                "title": "C Programming Fundamentals",
                "source": "YouTube",
                "url": "https://www.youtube.com/results?search_query=C+programming+fundamentals"
            }
        ],

        "Applications": [
            {
                "type": "Video",
                "title": "C Programming Problem Solving",
                "source": "YouTube",
                "url": "https://www.youtube.com/results?search_query=C+programming+problem+solving"
            }
        ]
    },


    "Data Structures": {

        "Concepts": [
            {
                "type": "Video",
                "title": "Data Structures Fundamentals",
                "source": "YouTube",
                "url": "https://www.youtube.com/results?search_query=data+structures+fundamentals"
            }
        ],

        "Applications": [
            {
                "type": "Video",
                "title": "Data Structures Problem Solving",
                "source": "YouTube",
                "url": "https://www.youtube.com/results?search_query=data+structures+problem+solving"
            }
        ]
    }
}


# ============================================================
# STATUS → PRIORITY
# ============================================================

def _priority(status):

    if status == "Weak":
        return "High"

    if status == "Needs Improvement":
        return "Medium"

    return "Low"


# ============================================================
# GENERIC RESOURCE
# ============================================================

def _generic_resource(subject, topic):

    query = f"{subject} {topic} tutorial"

    return {
        "type": "Video",
        "title": f"{subject} - {topic} Tutorial",
        "source": "YouTube",
        "url": (
            "https://www.youtube.com/results?search_query="
            + query.replace(" ", "+")
        )
    }


# ============================================================
# GET RESOURCES FROM EXCEL DATASET
# ============================================================

def _get_dataset_resources(subject_id, co_id=None, topic=None):

    try:
        resources_df = DataManager.get("resources")

    except Exception:
        return []


    if resources_df is None or resources_df.empty:
        return []


    data = resources_df.copy()


    # --------------------------------------------------------
    # Filter by SubjectID
    # --------------------------------------------------------

    if subject_id is not None and "SubjectID" in data.columns:

        data = data[
            data["SubjectID"].astype(str).str.strip()
            == str(subject_id).strip()
        ]


    # --------------------------------------------------------
    # Prefer matching CO
    # --------------------------------------------------------

    if (
        co_id is not None
        and "COID" in data.columns
        and not data.empty
    ):

        co_data = data[
            data["COID"].astype(str).str.strip()
            == str(co_id).strip()
        ]

        if not co_data.empty:
            data = co_data


    # --------------------------------------------------------
    # Prefer matching Topic
    # --------------------------------------------------------

    if (
        topic is not None
        and "Topic" in data.columns
        and not data.empty
    ):

        topic_data = data[
            data["Topic"].astype(str).str.strip().str.lower()
            == str(topic).strip().lower()
        ]

        if not topic_data.empty:
            data = topic_data


    resources = []


    for _, row in data.iterrows():

        resources.append({

            "type": str(
                row.get("ResourceType", "Video")
            ),

            "title": str(
                row.get("Title", "Learning Resource")
            ),

            "source": str(
                row.get("ResourceType", "Resource")
            ),

            "url": str(
                row.get("Link", "")
            )
        })


    return resources


# ============================================================
# GET RESOURCES
# ============================================================

def get_resources(
    subject,
    topic,
    subject_id=None,
    co_id=None
):

    # --------------------------------------------------------
    # First use the Excel resource dataset
    # --------------------------------------------------------

    dataset_resources = _get_dataset_resources(
        subject_id,
        co_id,
        topic
    )

    if dataset_resources:
        return dataset_resources


    # --------------------------------------------------------
    # Fallback to local resource database
    # --------------------------------------------------------

    subject_resources = RESOURCE_DATABASE.get(
        subject,
        {}
    )

    resources = subject_resources.get(
        topic,
        []
    )

    if resources:
        return resources


    # --------------------------------------------------------
    # Generic YouTube resource
    # --------------------------------------------------------

    return [
        _generic_resource(
            subject,
            topic
        )
    ]


# ============================================================
# GET SUBJECT NAME FROM SUBJECT ID
# ============================================================

def _get_subject_name(subject_id):

    try:

        subjects = DataManager.get("subjects")

        if subjects is None or subjects.empty:
            return None

        result = subjects[
            subjects["SubjectID"].astype(str).str.strip()
            == str(subject_id).strip()
        ]

        if result.empty:
            return None

        return str(
            result.iloc[0]["SubjectName"]
        )

    except Exception:
        return None


# ============================================================
# FIND SUBJECT-SPECIFIC CO
# ============================================================

def _get_subject_weakest_co(
    co_data,
    subject_id
):

    if not co_data:
        return {
            "CO": None,
            "Percentage": None
        }


    try:

        co_df = DataManager.get("co")

        if co_df is None or co_df.empty:
            return {
                "CO": None,
                "Percentage": None
            }


        # ----------------------------------------------------
        # Find CO IDs belonging to this subject
        # ----------------------------------------------------

        subject_cos = co_df[
            co_df["SubjectID"].astype(str).str.strip()
            == str(subject_id).strip()
        ]


        valid_co_ids = set(
            subject_cos["COID"]
            .astype(str)
            .str.strip()
        )


        # ----------------------------------------------------
        # Filter analyzer results
        # ----------------------------------------------------

        filtered = [

            item

            for item in co_data

            if str(
                item.get("COID", "")
            ).strip() in valid_co_ids

        ]


        if not filtered:
            return {
                "CO": None,
                "Percentage": None
            }


        # ----------------------------------------------------
        # Find lowest percentage
        # ----------------------------------------------------

        weakest = min(

            filtered,

            key=lambda x: float(
                x.get("Percentage", 100)
                if x.get("Percentage") is not None
                else 100
            )

        )


        return {

            "CO":
                weakest.get("COID"),

            "Percentage":
                weakest.get("Percentage")

        }


    except Exception:

        return {
            "CO": None,
            "Percentage": None
        }


# ============================================================
# FIND SUBJECT-SPECIFIC BTL
# ============================================================

def _get_subject_weakest_btl(
    btl_data,
    subject_id
):

    if not btl_data:
        return {
            "BTL": None,
            "Percentage": None
        }


    try:

        question_bank = DataManager.get(
            "question_bank"
        )

        if (
            question_bank is None
            or question_bank.empty
        ):
            return {
                "BTL": None,
                "Percentage": None
            }


        # ----------------------------------------------------
        # Get BTLs used by this subject
        # ----------------------------------------------------

        subject_questions = question_bank[

            question_bank["SubjectID"]
            .astype(str)
            .str.strip()

            == str(subject_id).strip()

        ]


        valid_btls = set(

            subject_questions["BTL"]
            .astype(str)
            .str.strip()

        )


        # ----------------------------------------------------
        # Filter analyzer BTL results
        # ----------------------------------------------------

        filtered = [

            item

            for item in btl_data

            if str(
                item.get("BTL", "")
            ).strip() in valid_btls

        ]


        if not filtered:
            return {
                "BTL": None,
                "Percentage": None
            }


        # ----------------------------------------------------
        # Find lowest BTL
        # ----------------------------------------------------

        weakest = min(

            filtered,

            key=lambda x: float(
                x.get("Percentage", 100)
                if x.get("Percentage") is not None
                else 100
            )

        )


        return {

            "BTL":
                weakest.get("BTL"),

            "Percentage":
                weakest.get("Percentage")

        }


    except Exception:

        return {
            "BTL": None,
            "Percentage": None
        }


# ============================================================
# FIND REMEDIAL CLASSES
# ============================================================

def _get_remedial_classes(
    subject_id,
    co_id=None,
    topic=None
):

    try:

        remedial = DataManager.get(
            "remedial"
        )

        if remedial is None or remedial.empty:
            return []


        data = remedial.copy()


        # ----------------------------------------------------
        # Subject
        # ----------------------------------------------------

        if "SubjectID" in data.columns:

            data = data[
                data["SubjectID"].astype(str).str.strip()
                == str(subject_id).strip()
            ]


        # ----------------------------------------------------
        # CO
        # ----------------------------------------------------

        if (
            co_id is not None
            and "COID" in data.columns
            and not data.empty
        ):

            co_data = data[

                data["COID"].astype(str).str.strip()
                == str(co_id).strip()

            ]

            if not co_data.empty:
                data = co_data


        # ----------------------------------------------------
        # Topic
        # ----------------------------------------------------

        if (
            topic is not None
            and "Topic" in data.columns
            and not data.empty
        ):

            topic_data = data[

                data["Topic"]
                .astype(str)
                .str.strip()
                .str.lower()

                == str(topic)
                .strip()
                .lower()

            ]

            if not topic_data.empty:
                data = topic_data


        remedial_classes = []


        for _, row in data.iterrows():

            remedial_classes.append({

                "RemedialID":
                    row.get("RemedialID"),

                "SubjectID":
                    row.get("SubjectID"),

                "COID":
                    row.get("COID"),

                "Topic":
                    row.get("Topic"),

                "FacultyID":
                    row.get("FacultyID"),

                "Day":
                    row.get("Day"),

                "Time":
                    row.get("Time"),

                "Room":
                    row.get("Room")

            })


        return remedial_classes


    except Exception:

        return []


# ============================================================
# RESOURCE RECOMMENDATION
# ============================================================

def recommend_resources(student_id):

    student_id = str(student_id)


    # --------------------------------------------------------
    # ANALYZE STUDENT
    # --------------------------------------------------------

    weak_data = detect_weak_subjects(
        student_id
    )

    co_data = analyze_co_performance(
        student_id
    )

    btl_data = analyze_btl_performance(
        student_id
    )

    topic_data = analyze_topic_performance(
        student_id
    )


    recommendations = []


    # --------------------------------------------------------
    # SUBJECTS REQUIRING ATTENTION
    # --------------------------------------------------------

    weak_subjects = weak_data.get(
        "weak_subjects",
        []
    )

    needs_improvement = weak_data.get(
        "needs_improvement",
        []
    )


    target_subjects = (
        weak_subjects
        + needs_improvement
    )


    # --------------------------------------------------------
    # PROCESS EACH SUBJECT
    # --------------------------------------------------------

    for subject_info in target_subjects:


        subject = subject_info.get(
            "Subject"
        )

        subject_id = subject_info.get(
            "SubjectID"
        )

        subject_status = subject_info.get(
            "Status"
        )

        subject_percentage = subject_info.get(
            "Percentage",
            0
        )


        # ----------------------------------------------------
        # SUBJECT-SPECIFIC CO
        # ----------------------------------------------------

        weakest_co = _get_subject_weakest_co(
            co_data,
            subject_id
        )


        weak_co = weakest_co.get(
            "CO"
        )

        co_percentage = weakest_co.get(
            "Percentage"
        )


        # ----------------------------------------------------
        # SUBJECT-SPECIFIC BTL
        # ----------------------------------------------------

        weakest_btl = _get_subject_weakest_btl(
            btl_data,
            subject_id
        )


        weak_btl = weakest_btl.get(
            "BTL"
        )

        btl_percentage = weakest_btl.get(
            "Percentage"
        )


        # ----------------------------------------------------
        # FIND TOPICS
        # ----------------------------------------------------

        subject_topics = [

            topic

            for topic in topic_data

            if topic.get("SubjectID")
            == subject_id

        ]


        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if not subject_topics:

            subject_topics = [

                {
                    "Topic": "General",

                    "Percentage":
                        subject_percentage,

                    "Status":
                        subject_status
                }

            ]


        # ----------------------------------------------------
        # ONLY WEAK / NEEDS IMPROVEMENT
        # ----------------------------------------------------

        subject_topics = [

            topic

            for topic in subject_topics

            if topic.get("Status")

            in [
                "Weak",
                "Needs Improvement"
            ]

        ]


        # ----------------------------------------------------
        # SORT WEAKEST FIRST
        # ----------------------------------------------------

        subject_topics = sorted(

            subject_topics,

            key=lambda x: float(
                x.get(
                    "Percentage",
                    100
                )
                if x.get("Percentage") is not None
                else 100
            )

        )


        # ----------------------------------------------------
        # TOP 3 TOPICS
        # ----------------------------------------------------

        for topic_info in subject_topics[:3]:


            topic = topic_info.get(
                "Topic",
                "General"
            )


            topic_percentage = topic_info.get(
                "Percentage",
                0
            )


            topic_status = topic_info.get(
                "Status",
                "Needs Improvement"
            )


            # ------------------------------------------------
            # RESOURCES
            # ------------------------------------------------

            resources = get_resources(

                subject,

                topic,

                subject_id,

                weak_co

            )


            # ------------------------------------------------
            # REMEDIAL CLASSES
            # ------------------------------------------------

            remedial_classes = _get_remedial_classes(

                subject_id,

                weak_co,

                topic

            )


            # ------------------------------------------------
            # CREATE RECOMMENDATIONS
            # ------------------------------------------------

            for resource in resources:


                recommendations.append({

                    "StudentID":
                        student_id,

                    "Subject":
                        subject,

                    "SubjectID":
                        subject_id,

                    "Topic":
                        topic,

                    "SubjectPercentage":
                        subject_percentage,

                    "TopicPercentage":
                        topic_percentage,

                    "Status":
                        topic_status,

                    "Priority":
                        _priority(
                            topic_status
                        ),

                    "Reason":
                        (
                            f"Low performance in "
                            f"{subject} - {topic}"
                        ),

                    "WeakestCO":
                        weak_co,

                    "COPercentage":
                        co_percentage,

                    "WeakestBTL":
                        weak_btl,

                    "BTLPercentage":
                        btl_percentage,

                    "ResourceType":
                        resource["type"],

                    "ResourceTitle":
                        resource["title"],

                    "Source":
                        resource["source"],

                    "URL":
                        resource["url"],

                    "RemedialClasses":
                        remedial_classes

                })


    # ========================================================
    # SORT BY PRIORITY
    # ========================================================

    priority_order = {

        "High": 0,

        "Medium": 1,

        "Low": 2

    }


    recommendations.sort(

        key=lambda x:
        priority_order.get(
            x["Priority"],
            3
        )

    )


    return recommendations


# ============================================================
# SUMMARY
# ============================================================

def get_recommendation_summary(student_id):

    student_id = str(student_id)


    recommendations = recommend_resources(
        student_id
    )


    high = sum(

        1

        for item in recommendations

        if item["Priority"] == "High"

    )


    medium = sum(

        1

        for item in recommendations

        if item["Priority"] == "Medium"

    )


    low = sum(

        1

        for item in recommendations

        if item["Priority"] == "Low"

    )


    # --------------------------------------------------------
    # ANALYSIS COUNTS
    # --------------------------------------------------------

    weak_data = detect_weak_subjects(
        student_id
    )

    co_data = analyze_co_performance(
        student_id
    )

    btl_data = analyze_btl_performance(
        student_id
    )

    topic_data = analyze_topic_performance(
        student_id
    )


    weak_subject_count = len(

        weak_data.get(
            "weak_subjects",
            []
        )

    )


    weak_co_count = sum(

        1

        for item in co_data

        if item.get("Status") == "Weak"

    )


    weak_btl_count = sum(

        1

        for item in btl_data

        if item.get("Status") == "Weak"

    )


    weak_topic_count = sum(

        1

        for item in topic_data

        if item.get("Status") == "Weak"

    )


    return {

        "StudentID":
            student_id,

        "total_recommendations":
            len(recommendations),

        "high_priority":
            high,

        "medium_priority":
            medium,

        "low_priority":
            low,

        "weak_subject_count":
            weak_subject_count,

        "weak_co_count":
            weak_co_count,

        "weak_btl_count":
            weak_btl_count,

        "weak_topic_count":
            weak_topic_count,

        "recommendations":
            recommendations

    }
