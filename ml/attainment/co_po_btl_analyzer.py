import pandas as pd

from models.data_manager import DataManager


# ============================================================
# CONFIGURATION
# ============================================================

WEAK_PERCENTAGE_THRESHOLD = 50.0
WARNING_PERCENTAGE_THRESHOLD = 60.0


# ============================================================
# UTILITY
# ============================================================

def _numeric(series):
    """Safely convert a pandas Series to numeric."""
    return pd.to_numeric(series, errors="coerce")


def _get_status(percentage):
    """Convert percentage into performance status."""

    if percentage < WEAK_PERCENTAGE_THRESHOLD:
        return "Weak"

    elif percentage < WARNING_PERCENTAGE_THRESHOLD:
        return "Needs Improvement"

    return "Good"


# ============================================================
# GET STUDENT QUESTION PERFORMANCE
# ============================================================

def get_student_question_performance(student_id):
    """
    Combine student marks with question-bank information.

    Returns one record for every question attempted by the student.
    """

    student_id = str(student_id).strip()

    marks = DataManager.get("marks")
    question_bank = DataManager.get("question_bank")

    if marks is None or marks.empty:
        return pd.DataFrame()

    if question_bank is None or question_bank.empty:
        return pd.DataFrame()

    required_marks = [
        "StudentID",
        "SubjectID",
        "QuestionID",
        "MarksObtained",
        "MaxMarks"
    ]

    required_questions = [
        "QuestionID",
        "SubjectID",
        "COID",
        "BTL"
    ]

    if not all(column in marks.columns for column in required_marks):
        return pd.DataFrame()

    if not all(column in question_bank.columns for column in required_questions):
        return pd.DataFrame()

    # --------------------------------------------------
    # Clean identifiers before merging
    # --------------------------------------------------

    marks = marks.copy()
    question_bank = question_bank.copy()

    marks["StudentID"] = (
        marks["StudentID"]
        .astype(str)
        .str.strip()
    )

    marks["SubjectID"] = (
        marks["SubjectID"]
        .astype(str)
        .str.strip()
    )

    marks["QuestionID"] = (
        marks["QuestionID"]
        .astype(str)
        .str.strip()
    )

    question_bank["SubjectID"] = (
        question_bank["SubjectID"]
        .astype(str)
        .str.strip()
    )

    question_bank["QuestionID"] = (
        question_bank["QuestionID"]
        .astype(str)
        .str.strip()
    )

    # Clean CO and BTL too
    question_bank["COID"] = (
        question_bank["COID"]
        .astype(str)
        .str.strip()
    )

    question_bank["BTL"] = (
        question_bank["BTL"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------
    # Select student's marks
    # --------------------------------------------------

    student_marks = marks[
        marks["StudentID"] == student_id
    ].copy()

    if student_marks.empty:
        return pd.DataFrame()

    # --------------------------------------------------
    # Question-bank columns
    # --------------------------------------------------

    question_columns = [
        "QuestionID",
        "SubjectID",
        "Subject",
        "Topic",
        "Subtopic",
        "COID",
        "BTL",
        "Difficulty"
    ]

    question_columns = [
        column
        for column in question_columns
        if column in question_bank.columns
    ]

    questions = question_bank[
        question_columns
    ].copy()

    # --------------------------------------------------
    # Remove duplicate question definitions
    # --------------------------------------------------

    questions = questions.drop_duplicates(
        subset=["QuestionID", "SubjectID"]
    )

    # --------------------------------------------------
    # Merge
    # --------------------------------------------------

    merged = student_marks.merge(
        questions,
        on=["QuestionID", "SubjectID"],
        how="left",
        suffixes=("_mark", "_question")
    )

    # --------------------------------------------------
    # Convert marks to numeric
    # --------------------------------------------------

    merged["MarksObtained"] = pd.to_numeric(
        merged["MarksObtained"],
        errors="coerce"
    )

    merged["MaxMarks"] = pd.to_numeric(
        merged["MaxMarks"],
        errors="coerce"
    )

    # --------------------------------------------------
    # Remove invalid marks
    # --------------------------------------------------

    merged = merged.dropna(
        subset=[
            "MarksObtained",
            "MaxMarks"
        ]
    )

    return merged


# --------------------------------------------------
# CO Analysis
# --------------------------------------------------

def analyze_co_performance(student_id):
    """
    Calculate Course Outcome performance for a student,
    separately for each SubjectID + COID.
    """

    data = get_student_question_performance(student_id)

    if data.empty:
        return []

    required = ["SubjectID", "COID", "MarksObtained", "MaxMarks", "QuestionID"]

    if not all(column in data.columns for column in required):
        return []

    data = data.dropna(subset=["SubjectID", "COID"])

    if data.empty:
        return []

    grouped = data.groupby(
        ["SubjectID", "COID"]
    ).agg(
        ObtainedMarks=("MarksObtained", "sum"),
        MaximumMarks=("MaxMarks", "sum"),
        Questions=("QuestionID", "count")
    ).reset_index()

    results = []

    for _, row in grouped.iterrows():

        maximum = float(row["MaximumMarks"])

        if maximum <= 0:
            continue

        obtained = float(row["ObtainedMarks"])

        percentage = round(
            (obtained / maximum) * 100,
            2
        )

        if percentage < WEAK_PERCENTAGE_THRESHOLD:
            status = "Weak"

        elif percentage < WARNING_PERCENTAGE_THRESHOLD:
            status = "Needs Improvement"

        else:
            status = "Good"

        results.append({
            "SubjectID": str(row["SubjectID"]),
            "COID": str(row["COID"]),
            "ObtainedMarks": round(obtained, 2),
            "MaximumMarks": round(maximum, 2),
            "Percentage": percentage,
            "Questions": int(row["Questions"]),
            "Status": status
        })

    results.sort(
        key=lambda x: x["Percentage"]
    )

    return results


# --------------------------------------------------
# BTL Analysis
# --------------------------------------------------

def analyze_btl_performance(student_id):
    """
    Calculate BTL-level performance for a student,
    separately for each SubjectID + BTL.
    """

    data = get_student_question_performance(student_id)

    if data.empty:
        return []

    required = [
        "SubjectID",
        "BTL",
        "MarksObtained",
        "MaxMarks",
        "QuestionID"
    ]

    if not all(column in data.columns for column in required):
        return []

    data = data.dropna(
        subset=["SubjectID", "BTL"]
    )

    if data.empty:
        return []

    grouped = data.groupby(
        ["SubjectID", "BTL"]
    ).agg(
        ObtainedMarks=("MarksObtained", "sum"),
        MaximumMarks=("MaxMarks", "sum"),
        Questions=("QuestionID", "count")
    ).reset_index()

    results = []

    for _, row in grouped.iterrows():

        maximum = float(row["MaximumMarks"])

        if maximum <= 0:
            continue

        obtained = float(row["ObtainedMarks"])

        percentage = round(
            (obtained / maximum) * 100,
            2
        )

        if percentage < WEAK_PERCENTAGE_THRESHOLD:
            status = "Weak"

        elif percentage < WARNING_PERCENTAGE_THRESHOLD:
            status = "Needs Improvement"

        else:
            status = "Good"

        results.append({
            "SubjectID": str(row["SubjectID"]),
            "BTL": str(row["BTL"]),
            "ObtainedMarks": round(obtained, 2),
            "MaximumMarks": round(maximum, 2),
            "Percentage": percentage,
            "Questions": int(row["Questions"]),
            "Status": status
        })

    results.sort(
        key=lambda x: x["Percentage"]
    )

    return results

# ============================================================
# TOPIC ANALYSIS
# ============================================================

def analyze_topic_performance(student_id):
    """
    Calculate topic-level performance for a student.
    """

    data = get_student_question_performance(
        student_id
    )

    if data.empty or "Topic" not in data.columns:
        return []

    data = data.dropna(
        subset=["Topic"]
    )

    if data.empty:
        return []

    grouped = data.groupby(
        ["SubjectID", "Topic"]
    ).agg(
        ObtainedMarks=("MarksObtained", "sum"),
        MaximumMarks=("MaxMarks", "sum"),
        Questions=("QuestionID", "count")
    ).reset_index()

    results = []

    for _, row in grouped.iterrows():

        maximum = float(
            row["MaximumMarks"]
        )

        if maximum <= 0:
            continue

        obtained = float(
            row["ObtainedMarks"]
        )

        percentage = round(
            (obtained / maximum) * 100,
            2
        )

        if percentage < WEAK_PERCENTAGE_THRESHOLD:
            status = "Weak"

        elif percentage < WARNING_PERCENTAGE_THRESHOLD:
            status = "Needs Improvement"

        else:
            status = "Good"

        results.append({

            "SubjectID":
                str(row["SubjectID"]),

            "Topic":
                str(row["Topic"]),

            "ObtainedMarks":
                round(obtained, 2),

            "MaximumMarks":
                round(maximum, 2),

            "Percentage":
                percentage,

            "Questions":
                int(row["Questions"]),

            "Status":
                status
        })

    results.sort(
        key=lambda x: x["Percentage"]
    )

    return results


# ============================================================
# COMPLETE CO + BTL ANALYSIS
# ============================================================

def analyze_student_obe(student_id):
    """
    Perform complete OBE analysis for a student.

    Includes:
        - Question performance
        - CO performance
        - BTL performance
        - Topic performance
    """

    return {

        "StudentID":
            str(student_id),

        "question_performance":
            get_student_question_performance(
                student_id
            ).to_dict("records"),

        "co_performance":
            analyze_co_performance(
                student_id
            ),

        "btl_performance":
            analyze_btl_performance(
                student_id
            ),

        "topic_performance":
            analyze_topic_performance(
                student_id
            )
    }


# ============================================================
# WEAK COs
# ============================================================

def get_weak_cos(student_id):
    """
    Return only weak Course Outcomes.
    """

    return [
        co
        for co in analyze_co_performance(
            student_id
        )
        if co["Status"] == "Weak"
    ]


# ============================================================
# WEAK BTLs
# ============================================================

def get_weak_btls(student_id):
    """
    Return only weak Bloom's Taxonomy levels.
    """

    return [
        btl
        for btl in analyze_btl_performance(
            student_id
        )
        if btl["Status"] == "Weak"
    ]


# ============================================================
# WEAK TOPICS
# ============================================================

def get_weak_topics(student_id):
    """
    Return only weak topics.
    """

    return [
        topic
        for topic in analyze_topic_performance(
            student_id
        )
        if topic["Status"] == "Weak"
    ]