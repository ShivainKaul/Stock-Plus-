import os

# ─────────────────────────────────────────────
#  StockPlus – Configuration
#  Replace the placeholder values below with
#  your actual API keys before running the app.
# ─────────────────────────────────────────────

# NewsAPI key  →  https://newsapi.org/register
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "6773b6b4b42e4a3bbf1ae52dca4635cb")

# Number of news articles to fetch per query
NEWS_PAGE_SIZE = 10

# How many days of news to look back
NEWS_LOOKBACK_DAYS = 7

# yfinance: how many calendar days of stock history to pull
STOCK_HISTORY_DAYS = 30

# Flask server settings
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Path where the trained model is persisted
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "stock_model.pkl")

# Minimum number of data-points required to attempt training
MIN_TRAINING_ROWS = 5
