
from flask import Flask, render_template, request, jsonify

from modules.news_fetcher  import fetch_news
from modules.summarizer    import summarize_articles
from modules.sentiment     import analyse_articles, aggregate_sentiment
from modules.stock_data    import fetch_stock_data, get_latest_price_info, stock_to_records
from modules.predictor     import train_model, predict
from utils.preprocessing   import build_feature_dataframe, get_latest_feature_row
from config                import FLASK_HOST, FLASK_PORT, FLASK_DEBUG

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main single-page UI."""
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Full analysis pipeline triggered by the user entering a ticker.

    Expected JSON body:  { "ticker": "AAPL" }

    Response JSON structure:
    {
        "ticker":       str,
        "articles":     [ { title, description, source, published_at,
                            url, summary, sentiment_score, sentiment_label } ],
        "sentiment":    { avg_score, overall_label, positive_pct, negative_pct, neutral_pct },
        "stock":        { date, close, open, high, low, volume, daily_change },
        "stock_history": [ ... ],          # last N days for chart
        "prediction":   { prediction, confidence, trained },
        "model_info":   { success, message, accuracy },
        "error":        str | null
    }
    """
    data   = request.get_json(force=True) or {}
    ticker = data.get("ticker", "").strip().upper()

    if not ticker:
        return jsonify({"error": "Please provide a ticker symbol."}), 400

    # ── 1. Fetch & enrich news ────────────────────────────────────────────────
    articles = fetch_news(ticker)
    if not articles:
        return jsonify({"error": f"No news found for '{ticker}'. Check your NewsAPI key or try another ticker."}), 404

    articles = summarize_articles(articles)
    articles = analyse_articles(articles)
    sentiment = aggregate_sentiment(articles)

    # ── 2. Fetch stock data ───────────────────────────────────────────────────
    stock_df    = fetch_stock_data(ticker)
    latest_price = get_latest_price_info(stock_df)
    history      = stock_to_records(stock_df)

    if stock_df.empty:
        return jsonify({
            "error": f"Could not fetch stock data for '{ticker}'. "
                     "Make sure it is a valid ticker on Yahoo Finance."
        }), 404

    # ── 3. Feature engineering ────────────────────────────────────────────────
    feature_df = build_feature_dataframe(stock_df, sentiment["avg_score"])

    # ── 4. Train model (on available history) and predict ────────────────────
    model_info   = train_model(feature_df)
    feature_row  = get_latest_feature_row(feature_df)
    prediction   = predict(feature_row)

    # ── 5. Return full result ─────────────────────────────────────────────────
    return jsonify({
        "ticker":        ticker,
        "articles":      articles,
        "sentiment":     sentiment,
        "stock":         latest_price,
        "stock_history": history,
        "prediction":    prediction,
        "model_info":    model_info,
        "error":         None,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5002)
