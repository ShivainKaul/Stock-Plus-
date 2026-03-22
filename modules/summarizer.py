"""
modules/summarizer.py
---------------------
Extractive text summarizer using a simple frequency-based sentence scoring
approach (lightweight alternative to TextRank – no heavy dependencies needed).

The algorithm:
  1. Tokenise the text into sentences.
  2. Count word frequencies (stop-words excluded).
  3. Score each sentence by the sum of its word frequencies.
  4. Return the top-N highest-scoring sentences in original order.
"""

import re
import heapq


# Common English stop-words to ignore when scoring
_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "this", "that",
    "these", "those", "it", "its", "as", "up", "out", "about", "than",
    "into", "through", "over", "after", "before", "also", "not", "no",
    "so", "if", "then", "i", "we", "you", "he", "she", "they", "their",
    "our", "your", "his", "her", "said", "according",
}


def summarize(text: str, num_sentences: int = 2) -> str:
    """
    Return an extractive summary of `text` using `num_sentences` sentences.

    Parameters
    ----------
    text : str
        The article body or description to summarise.
    num_sentences : int
        How many sentences to include in the summary (default 2).

    Returns
    -------
    str
        The summary string, or the original text if it is already short.
    """

    if not text or not text.strip():
        return ""

    # ── 1. Split into sentences ───────────────────────────────────────────────
    # Simple heuristic: split on ". ", "! ", "? "
    sentence_pattern = r"(?<=[.!?])\s+"
    sentences = re.split(sentence_pattern, text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    # Nothing worth summarising
    if len(sentences) <= num_sentences:
        return text.strip()

    # ── 2. Build word-frequency table ─────────────────────────────────────────
    word_freq: dict[str, int] = {}
    for sentence in sentences:
        for word in re.findall(r"\b[a-z]+\b", sentence.lower()):
            if word not in _STOP_WORDS:
                word_freq[word] = word_freq.get(word, 0) + 1

    if not word_freq:
        return sentences[0]

    # Normalise frequencies to 0-1
    max_freq = max(word_freq.values())
    word_freq = {w: f / max_freq for w, f in word_freq.items()}

    # ── 3. Score sentences ────────────────────────────────────────────────────
    scores: dict[int, float] = {}
    for idx, sentence in enumerate(sentences):
        for word in re.findall(r"\b[a-z]+\b", sentence.lower()):
            if word in word_freq:
                scores[idx] = scores.get(idx, 0.0) + word_freq[word]

    # ── 4. Pick the top-N sentences and return them in original order ─────────
    top_indices = heapq.nlargest(num_sentences, scores, key=lambda i: scores[i])
    top_indices.sort()  # preserve original reading order

    summary = " ".join(sentences[i] for i in top_indices)
    return summary


def summarize_articles(articles: list[dict]) -> list[dict]:
    """
    Add a 'summary' key to each article dict in-place and return the list.

    Parameters
    ----------
    articles : list[dict]
        Articles as returned by news_fetcher.fetch_news().

    Returns
    -------
    list[dict]
        Same list with 'summary' added to every item.
    """
    for article in articles:
        # Combine title + description for richer summarisation input
        combined = f"{article.get('title', '')}. {article.get('description', '')}"
        article["summary"] = summarize(combined, num_sentences=2)
    return articles
