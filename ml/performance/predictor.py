import os
import joblib
import pandas as pd

from ml.data.feature_builder import build_student_features
from ml.data.preprocessing import get_performance_features


# --------------------------------------------------
# Project root
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


# --------------------------------------------------
# Saved ML files
# --------------------------------------------------

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "saved_models",
    "performance_model.joblib"
)

PREPROCESSOR_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "saved_models",
    "performance_preprocessor.joblib"
)


# --------------------------------------------------
# Load model
# --------------------------------------------------

def load_model():

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Performance model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


# --------------------------------------------------
# Load preprocessor
# --------------------------------------------------

def load_preprocessor():

    if not os.path.exists(PREPROCESSOR_PATH):
        raise FileNotFoundError(
            f"Performance preprocessor not found: "
            f"{PREPROCESSOR_PATH}"
        )

    return joblib.load(PREPROCESSOR_PATH)


# --------------------------------------------------
# Predict student performance
# --------------------------------------------------

def predict_student_performance(student_id):

    # ----------------------------------------------
    # Build ALL student features
    # ----------------------------------------------

    features = build_student_features(student_id)

    if not features:

        return {
            "StudentID": student_id,
            "predicted_percentage": None,
            "error": "Student not found"
        }


    # ----------------------------------------------
    # Convert dictionary to DataFrame
    # ----------------------------------------------

    df = pd.DataFrame([features])


    # ----------------------------------------------
    # Select the SAME features used during training
    # ----------------------------------------------

    X = get_performance_features(df)


    # ----------------------------------------------
    # Check required columns
    # ----------------------------------------------

    required_columns = [
        "AverageMarks",
        "AveragePercentage",
        "HighestMarks",
        "LowestMarks",
        "TotalAssessments",
        "AverageAttendance",
        "Python",
        "Java",
        "C",
        "SQL",
        "ML",
        "Web",
        "Networking",
        "Communication",
        "Year",
        "Semester",
        "Department",
        "Section"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in X.columns
    ]

    if missing_columns:

        return {
            "StudentID": student_id,
            "predicted_percentage": None,
            "error": (
                "Missing prediction features: "
                + ", ".join(missing_columns)
            )
        }


    # ----------------------------------------------
    # Load trained objects
    # ----------------------------------------------

    model = load_model()

    preprocessor = load_preprocessor()


    # ----------------------------------------------
    # Transform features
    # ----------------------------------------------

    X_processed = preprocessor.transform(X)


    # ----------------------------------------------
    # Generate prediction
    # ----------------------------------------------

    prediction = model.predict(X_processed)[0]


    # ----------------------------------------------
    # Return result
    # ----------------------------------------------

    return {
        "StudentID": student_id,
        "predicted_percentage": round(
            float(prediction),
            2
        )
    }