import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from models.data_manager import DataManager

from ml.data.feature_builder import build_student_feature_dataframe
from ml.data.preprocessing import (
    get_performance_features,
    create_performance_preprocessor
)

from ml.performance.model import create_performance_model


MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "saved_models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "performance_model.joblib"
)

PREPROCESSOR_PATH = os.path.join(
    MODEL_DIR,
    "performance_preprocessor.joblib"
)


def train_performance_model():

    print("Loading student data...")

    DataManager.load_all()

    df = build_student_feature_dataframe()

    if df.empty:
        raise ValueError(
            "No student feature data available."
        )

    print(f"Students available: {len(df)}")

    # -------------------------------------------------
    # Features
    # -------------------------------------------------

    X = get_performance_features(df)

    # -------------------------------------------------
    # Target
    # -------------------------------------------------
    #
    # We use AveragePercentage as the target.
    #
    # IMPORTANT:
    # For a real prediction system, the target should
    # ideally represent future performance rather than
    # the same data used to construct the features.
    #
    # For our first working model, we use it to establish
    # the ML pipeline.
    # -------------------------------------------------

    if "AveragePercentage" not in df.columns:
        raise ValueError(
            "AveragePercentage column not found."
        )

    y = df["AveragePercentage"]

    # -------------------------------------------------
    # Train/Test Split
    # -------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    print(
        f"Training samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    # -------------------------------------------------
    # Preprocessing
    # -------------------------------------------------

    preprocessor = create_performance_preprocessor(
        X_train
    )

    X_train_processed = preprocessor.fit_transform(
        X_train
    )

    X_test_processed = preprocessor.transform(
        X_test
    )

    print(
        f"Processed training shape: "
        f"{X_train_processed.shape}"
    )

    # -------------------------------------------------
    # Model
    # -------------------------------------------------

    model = create_performance_model()

    model.fit(
        X_train_processed,
        y_train
    )

    # -------------------------------------------------
    # Prediction
    # -------------------------------------------------

    predictions = model.predict(
        X_test_processed
    )

    # -------------------------------------------------
    # Evaluation
    # -------------------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    mse = mean_squared_error(
        y_test,
        predictions
    )

    rmse = mse ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    print("\nModel Evaluation")
    print("----------------------")

    print(
        f"MAE  : {mae:.2f}"
    )

    print(
        f"RMSE : {rmse:.2f}"
    )

    print(
        f"R²   : {r2:.2f}"
    )

    # -------------------------------------------------
    # Save model
    # -------------------------------------------------

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    joblib.dump(
        preprocessor,
        PREPROCESSOR_PATH
    )

    print("\nModel saved:")
    print(MODEL_PATH)

    print("\nPreprocessor saved:")
    print(PREPROCESSOR_PATH)

    return {
        "model": model,
        "preprocessor": preprocessor,
        "mae": mae,
        "rmse": rmse,
        "r2": r2
    }


if __name__ == "__main__":
    train_performance_model()