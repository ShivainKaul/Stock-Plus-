# StockPlus 📈

> AI-Powered Stock Sentiment Analysis Platform  
> *B.Tech Computer Science College Project*

---

## What it does

StockPlus combines **financial news**, **NLP sentiment analysis**, and
**machine learning** to predict short-term stock price movement:

1. Fetches recent news articles for any stock ticker via **NewsAPI**
2. Summarises each article using extractive summarisation
3. Scores sentiment with **VADER** (compound score –1 to +1)
4. Pulls historical price data with **yfinance**
5. Trains a **Random Forest** on combined features
6. Predicts **UP / DOWN** for the next trading day
7. Displays everything in a sleek dark-mode web UI

---

## Project Structure

```
StockPlus/
├── app.py                  ← Flask entry point & routes
├── config.py               ← API keys & settings
├── requirements.txt
│
├── modules/
│   ├── news_fetcher.py     ← NewsAPI integration
│   ├── summarizer.py       ← Extractive summarisation
│   ├── sentiment.py        ← VADER sentiment analysis
│   ├── stock_data.py       ← yfinance stock data
│   └── predictor.py        ← Random Forest model
│
├── utils/
│   └── preprocessing.py   ← Feature engineering
│
├── templates/
│   └── index.html          ← Single-page UI
│
├── static/
│   ├── style.css
│   └── main.js
│
├── models/                 ← Auto-created; stores trained model
└── data/                   ← Available for CSV exports (optional)
```

---

## Setup Instructions

### 1 · Clone / download the project

```bash
cd StockPlus
```

### 2 · Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3 · Install dependencies

```bash
pip install -r requirements.txt
```

### 4 · Get a free NewsAPI key

1. Visit https://newsapi.org/register
2. Register for a **free** account
3. Copy your API key

### 5 · Add your API key

Open `config.py` and replace the placeholder:

```python
NEWS_API_KEY = "paste_your_key_here"
```

Or set it as an environment variable:

```bash
# Linux / macOS
export NEWS_API_KEY="your_key"

# Windows PowerShell
$env:NEWS_API_KEY="your_key"
```

> **No key yet?** The app still runs with built-in demo articles so you
> can test the UI immediately.

### 6 · Run the app

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## How to use

1. Type a ticker symbol in the search box (e.g. `AAPL`, `TSLA`, `NVDA`)
2. Press **Analyse** or hit Enter
3. View:
   - Latest price KPIs
   - ML prediction (UP / DOWN) with confidence
   - Sentiment breakdown donut chart
   - 30-day price history chart
   - Individual article sentiment scores

---

## Technology Stack

| Layer              | Library / Tool       |
|--------------------|----------------------|
| Web framework      | Flask                |
| News data          | NewsAPI              |
| Stock data         | yfinance             |
| Summarisation      | Custom extractive    |
| Sentiment analysis | VADER                |
| ML model           | scikit-learn (RF)    |
| Frontend charts    | Chart.js             |
| Fonts              | Syne + DM Mono       |

---

## Disclaimer

> This project is for **academic / educational demonstration only**.
> It is **not** financial advice and should **never** be used for real
> investment decisions.  Stock prices are influenced by thousands of
> factors; this simple model captures only a fraction of them.

---

*Made with Python, Flask & ☕ by a CS student who loves building things.*
