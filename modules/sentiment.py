"""
modules/sentiment.py
--------------------
Sentiment analysis for news headlines / summaries.

Uses VADER (Valence Aware Dictionary and sEntiment Reasoner) from the
`vaderSentiment` package – a rule-based model tuned for short social-media
and news-headline text.  No GPU or heavy model download needed.

Output per article:
    sentiment_score  – compound score in [-1.0, +1.0]
    sentiment_label  – "positive" | "neutral" | "negative"
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Reuse a single analyser instance for efficiency
_analyser = SentimentIntensityAnalyzer()

# VADER compound-score thresholds (standard recommendation)
POSITIVE_THRESHOLD =  0.05
NEGATIVE_THRESHOLD = -0.05


def analyse_sentiment(text: str) -> dict:
    """
    Return sentiment score and label for a piece of text.

    Parameters
    ----------
    text : str
        A news headline, summary, or short paragraph.

    Returns
    -------
    dict with keys:
        sentiment_score  (float)
        sentiment_label  (str)
    """
    if not text or not text.strip():
        return {"sentiment_score": 0.0, "sentiment_label": "neutral"}

    scores = _analyser.polarity_scores(text)
    compound = round(scores["compound"], 4)

    if compound >= POSITIVE_THRESHOLD:
        label = "positive"
    elif compound <= NEGATIVE_THRESHOLD:
        label = "negative"
    else:
        label = "neutral"

    return {"sentiment_score": compound, "sentiment_label": label}


def analyse_articles(articles: list[dict]) -> list[dict]:
    """
    Adds sentiment_score and sentiment_label to each article dict.

    The analyser uses the 'summary' field when available, otherwise falls
    back to 'title'.

    Parameters
    ----------
    articles : list[dict]
        Articles as enriched by summarizer.summarize_articles().

    Returns
    -------
    list[dict]
        Same list with sentiment fields added to every item.
    """
    for article in articles:
        text = article.get("summary") or article.get("title", "")
        result = analyse_sentiment(text)
        article["sentiment_score"] = result["sentiment_score"]
        article["sentiment_label"] = result["sentiment_label"]
    return articles


def aggregate_sentiment(articles: list[dict]) -> dict:
    """
    Compute an overall sentiment signal across all articles.

    Returns
    -------
    dict with keys:
        avg_score     – mean compound score
        overall_label – dominant label
        positive_pct  – % of articles that are positive
        negative_pct  – % of articles that are negative
        neutral_pct   – % of articles that are neutral
    """
    if not articles:
        return {
            "avg_score": 0.0,
            "overall_label": "neutral",
            "positive_pct": 0,
            "negative_pct": 0,
            "neutral_pct": 100,
        }

    scores = [a["sentiment_score"] for a in articles if "sentiment_score" in a]
    avg = round(sum(scores) / len(scores), 4) if scores else 0.0

    labels = [a["sentiment_label"] for a in articles if "sentiment_label" in a]
    n = len(labels)
    pos = labels.count("positive")
    neg = labels.count("negative")
    neu = labels.count("neutral")

    if avg >= POSITIVE_THRESHOLD:
        overall = "positive"
    elif avg <= NEGATIVE_THRESHOLD:
        overall = "negative"
    else:
        overall = "neutral"

    return {
        "avg_score":     avg,
        "overall_label": overall,
        "positive_pct":  round(pos / n * 100) if n else 0,
        "negative_pct":  round(neg / n * 100) if n else 0,
        "neutral_pct":   round(neu / n * 100) if n else 0,
    }
