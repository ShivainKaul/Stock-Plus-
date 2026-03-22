"""
modules/predictor.py
--------------------
Trains a Random Forest classifier on the feature DataFrame and
predicts whether the stock will move UP or DOWN.

Because we're using only a few days of data for a college project,
the model is intentionally simple and the prediction should be treated
as a *demonstration*, not real financial advice.
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from config import MODEL_PATH, MIN_TRAINING_ROWS


# Column names expected by the model
FEATURE_COLS = ["sentiment_score", "prev_close", "log_volume",
                "daily_change", "price_change_pct"]
LABEL_MAP = {1: "UP", 0: "DOWN"}


def train_model(feature_df: pd.DataFrame) -> dict:
    """
    Train a Random Forest on the supplied feature DataFrame and persist it.

    Parameters
    ----------
    feature_df : pd.DataFrame
        Output of preprocessing.build_feature_dataframe() – must contain
        FEATURE_COLS and the 'movement' column.

    Returns
    -------
    dict with keys:
        success  (bool)
        message  (str)
        accuracy (float | None)
    """
    if feature_df.empty or len(feature_df) < MIN_TRAINING_ROWS:
        return {
            "success": False,
            "message": f"Need at least {MIN_TRAINING_ROWS} rows to train. "
                       f"Got {len(feature_df)}.",
            "accuracy": None,
        }

    missing = [c for c in FEATURE_COLS if c not in feature_df.columns]
    if missing:
        return {"success": False, "message": f"Missing columns: {missing}", "accuracy": None}

    X = feature_df[FEATURE_COLS].values
    y = feature_df["movement"].values

    # Simple pipeline: scale → Random Forest
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=100,
            max_depth=4,          # keep shallow to prevent overfitting on tiny data
            random_state=42,
        )),
    ])

    pipeline.fit(X, y)

    # Training accuracy (on the same data – only indicative for small sets)
    train_acc = round(pipeline.score(X, y) * 100, 1)

    # Persist
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    return {
        "success":  True,
        "message":  f"Model trained on {len(X)} samples.",
        "accuracy": train_acc,
    }


def predict(feature_row: pd.DataFrame) -> dict:
    """
    Load the saved model and return a prediction for a single feature row.

    Parameters
    ----------
    feature_row : pd.DataFrame
        One-row DataFrame with FEATURE_COLS (from preprocessing.get_latest_feature_row).

    Returns
    -------
    dict with keys:
        prediction  – "UP" or "DOWN"
        confidence  – probability of the predicted class (0–100 %)
        trained     – whether a saved model was found
    """
    if not os.path.exists(MODEL_PATH):
        # No trained model yet – fall back to rule-based heuristic
        return _heuristic_predict(feature_row)

    try:
        with open(MODEL_PATH, "rb") as f:
            pipeline = pickle.load(f)

        X = feature_row[FEATURE_COLS].values
        pred_int = int(pipeline.predict(X)[0])
        proba    = pipeline.predict_proba(X)[0]
        confidence = round(float(np.max(proba)) * 100, 1)

        return {
            "prediction": LABEL_MAP[pred_int],
            "confidence": confidence,
            "trained": True,
        }

    except Exception as e:
        print(f"[predictor] Prediction error: {e}")
        return _heuristic_predict(feature_row)


def _heuristic_predict(feature_row: pd.DataFrame) -> dict:
    """
    Simple rule-based fallback when no trained model is available.

    Logic: if sentiment_score > 0 AND recent daily_change > 0 → UP, else DOWN.
    """
    if feature_row.empty:
        return {"prediction": "N/A", "confidence": 0.0, "trained": False}

    row = feature_row.iloc[0]
    sentiment = float(row.get("sentiment_score", 0))
    change    = float(row.get("daily_change", 0))

    if sentiment > 0.05 and change > 0:
        prediction, confidence = "UP", 62.0
    elif sentiment < -0.05 or change < 0:
        prediction, confidence = "DOWN", 60.0
    else:
        prediction, confidence = "UP", 51.0   # coin-flip territory

    return {"prediction": prediction, "confidence": confidence, "trained": False}
