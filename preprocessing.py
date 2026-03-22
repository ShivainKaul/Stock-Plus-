"""
utils/preprocessing.py
-----------------------
Helper functions to build a feature matrix from news sentiment
and stock-price data, suitable for training / inference with
scikit-learn models.
"""

import pandas as pd
import numpy as np


def build_feature_dataframe(
    stock_df: pd.DataFrame,
    sentiment_score: float,
) -> pd.DataFrame:
    """
    Create a feature DataFrame by combining stock history with the
    current aggregate sentiment score.

    Features per row (trading day):
        sentiment_score     – same value repeated for every row (current batch)
        prev_close          – previous day's closing price
        volume              – trading volume (log-scaled for better range)
        daily_change        – close − previous close
        price_change_pct    – daily_change / prev_close × 100

    Target variable (to be added by the caller or trainer):
        movement  →  1 = price went UP, 0 = price went DOWN or flat

    Parameters
    ----------
    stock_df : pd.DataFrame
        Output of stock_data.fetch_stock_data().
    sentiment_score : float
        Aggregate sentiment score from sentiment.aggregate_sentiment().

    Returns
    -------
    pd.DataFrame  (may be empty if stock_df has fewer than 2 rows)
    """
    if stock_df.empty or len(stock_df) < 2:
        return pd.DataFrame()

    df = stock_df[["date", "close", "volume", "daily_change"]].copy()
    df = df.rename(columns={"close": "current_close"})

    # Shift close by 1 to get the *previous* day's close as a feature
    df["prev_close"] = df["current_close"].shift(1)
    df = df.dropna(subset=["prev_close"])

    # Percentage change
    df["price_change_pct"] = (df["daily_change"] / df["prev_close"] * 100).round(4)

    # Log-scale volume (avoids huge numeric range swamping the model)
    df["log_volume"] = np.log1p(df["volume"]).round(4)

    # Attach sentiment (constant for this news batch)
    df["sentiment_score"] = round(float(sentiment_score), 4)

    # Binary movement label: 1 if price went UP, 0 if flat/down
    df["movement"] = (df["daily_change"] > 0).astype(int)

    feature_cols = ["sentiment_score", "prev_close", "log_volume",
                    "daily_change", "price_change_pct"]
    return df[["date"] + feature_cols + ["movement"]].reset_index(drop=True)


def get_latest_feature_row(feature_df: pd.DataFrame) -> pd.DataFrame:
    """
    Return just the last row of feature_df (used for live prediction).
    Drops the 'movement' column since that's what we're predicting.
    """
    if feature_df.empty:
        return pd.DataFrame()

    row = feature_df.tail(1).copy()
    feature_cols = ["sentiment_score", "prev_close", "log_volume",
                    "daily_change", "price_change_pct"]
    return row[feature_cols]
