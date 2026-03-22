"""
modules/news_fetcher.py
-----------------------
Fetches recent news articles related to a stock ticker / company
using the NewsAPI (https://newsapi.org).

Each returned article is a plain dict with keys:
    title, description, source, published_at, url
"""

import datetime
import requests
from config import NEWS_API_KEY, NEWS_PAGE_SIZE, NEWS_LOOKBACK_DAYS


def fetch_news(query: str) -> list[dict]:
    """
    Query NewsAPI for articles matching `query`.

    Parameters
    ----------
    query : str
        Company name or stock ticker, e.g. "Apple" or "AAPL".

    Returns
    -------
    list[dict]
        A list of article dicts.  Returns an empty list on any error.
    """

    if NEWS_API_KEY == "your_newsapi_key_here":
        # Return sample data so the UI still works during development
        return _sample_articles(query)

    # Calculate the earliest date we care about
    from_date = (
        datetime.date.today() - datetime.timedelta(days=NEWS_LOOKBACK_DAYS)
    ).isoformat()

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "sortBy": "publishedAt",
        "pageSize": NEWS_PAGE_SIZE,
        "language": "en",
        "apiKey": NEWS_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = []
        for item in data.get("articles", []):
            articles.append({
                "title":        item.get("title", ""),
                "description":  item.get("description", "") or "",
                "source":       item.get("source", {}).get("name", "Unknown"),
                "published_at": item.get("publishedAt", ""),
                "url":          item.get("url", ""),
            })
        return articles

    except Exception as e:
        print(f"[news_fetcher] Error fetching news: {e}")
        return []


# ── Demo data (used when no API key is configured) ────────────────────────────

def _sample_articles(query: str) -> list[dict]:
    """Return a handful of plausible-looking demo articles."""
    today = datetime.date.today().isoformat()
    return [
        {
            "title": f"{query} Reports Strong Quarterly Earnings, Stock Surges",
            "description": f"{query} beat analyst expectations with record revenue, sending shares higher in after-hours trading.",
            "source": "Financial Times",
            "published_at": today,
            "url": "https://example.com/article1",
        },
        {
            "title": f"Analysts Upgrade {query} to Buy on Growth Outlook",
            "description": f"Several Wall Street firms raised their price targets for {query} citing robust demand and margin expansion.",
            "source": "Bloomberg",
            "published_at": today,
            "url": "https://example.com/article2",
        },
        {
            "title": f"{query} Faces Regulatory Scrutiny Over Data Practices",
            "description": f"Regulators opened a preliminary inquiry into {query}'s data-handling policies, adding uncertainty to the outlook.",
            "source": "Reuters",
            "published_at": today,
            "url": "https://example.com/article3",
        },
        {
            "title": f"{query} Announces New Product Line to Expand Market Share",
            "description": f"{query} unveiled its next-generation product lineup aimed at capturing a larger slice of the market.",
            "source": "TechCrunch",
            "published_at": today,
            "url": "https://example.com/article4",
        },
        {
            "title": f"Market Volatility Weighs on {query} as Macro Concerns Rise",
            "description": f"Broader market selloff dragged {query} shares down despite no company-specific negative news.",
            "source": "CNBC",
            "published_at": today,
            "url": "https://example.com/article5",
        },
    ]
