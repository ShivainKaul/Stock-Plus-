"""
modules/stock_data.py
---------------------
Fetches historical OHLCV (Open/High/Low/Close/Volume) stock data
using the yfinance library.

Also computes a simple 'daily_price_change' feature used later in
the feature-engineering step.
"""

import datetime
import yfinance as yf
import pandas as pd
from config import STOCK_HISTORY_DAYS


def fetch_stock_data(ticker: str) -> pd.DataFrame:
    """
    Download recent daily stock data for the given ticker.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol, e.g. "AAPL", "TSLA", "MSFT".

    Returns
    -------
    pd.DataFrame
        Columns: date, open, high, low, close, volume, daily_change
        Returns an empty DataFrame on error.
    """
    end   = datetime.date.today()
    start = end - datetime.timedelta(days=STOCK_HISTORY_DAYS)

    try:
        raw = yf.download(
            ticker,
            start=start.isoformat(),
            end=end.isoformat(),
            progress=False,
            auto_adjust=True,   # adjusts for splits & dividends automatically
        )

        if raw.empty:
            print(f"[stock_data] No data returned for ticker '{ticker}'.")
            return pd.DataFrame()

        # Flatten MultiIndex columns that yfinance sometimes returns
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.columns = ["open", "high", "low", "close", "volume"]
        df.index.name = "date"
        df = df.reset_index()

        # daily_change: today's close minus yesterday's close
        df["daily_change"] = df["close"].diff().fillna(0.0)

        # Round floats for cleaner display
        for col in ["open", "high", "low", "close", "daily_change"]:
            df[col] = df[col].round(4)

        return df

    except Exception as e:
        print(f"[stock_data] Error fetching data for '{ticker}': {e}")
        return pd.DataFrame()


def get_latest_price_info(df: pd.DataFrame) -> dict:
    """
    Extract the most recent row's key figures for quick display.

    Parameters
    ----------
    df : pd.DataFrame
        As returned by fetch_stock_data().

    Returns
    -------
    dict with keys: date, close, open, high, low, volume, daily_change
    """
    if df.empty:
        return {}

    row = df.iloc[-1]
    return {
        "date":         str(row["date"])[:10],
        "close":        float(row["close"]),
        "open":         float(row["open"]),
        "high":         float(row["high"]),
        "low":          float(row["low"]),
        "volume":       int(row["volume"]),
        "daily_change": float(row["daily_change"]),
    }


def stock_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to a list of plain dicts for JSON serialisation."""
    if df.empty:
        return []
    records = df.copy()
    records["date"] = records["date"].astype(str).str[:10]
    return records.to_dict(orient="records")
