/* static/main.js
   ──────────────────────────────────────────────────────────────────────────
   StockPlus – UI logic
   Calls /analyze, then renders KPIs, prediction, sentiment donut,
   price chart, and article cards.
*/

let priceChartInstance    = null;
let sentimentChartInstance = null;

/* ── Entry point ─────────────────────────────────────────────── */
async function runAnalysis() {
  const ticker = document.getElementById("tickerInput").value.trim().toUpperCase();
  if (!ticker) { showError("Please enter a ticker symbol (e.g. AAPL)."); return; }

  setLoading(true);
  clearResults();
  hideError();

  try {
    const resp = await fetch("/analyze", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ ticker }),
    });

    const data = await resp.json();

    if (!resp.ok || data.error) {
      showError(data.error || "An unknown error occurred.");
      return;
    }

    renderResults(data);

  } catch (err) {
    showError("Network error – make sure the Flask server is running.");
  } finally {
    setLoading(false);
  }
}

/* Allow pressing Enter in the input */
document.getElementById("tickerInput")
  .addEventListener("keydown", e => { if (e.key === "Enter") runAnalysis(); });

/* ── Render pipeline ─────────────────────────────────────────── */
function renderResults(data) {
  renderKPIs(data);
  renderPrediction(data.prediction, data.model_info);
  renderSentimentDonut(data.sentiment);
  renderPriceChart(data.stock_history, data.ticker);
  renderArticles(data.articles);
  document.getElementById("results").classList.remove("hidden");
}

/* ── KPI strip ───────────────────────────────────────────────── */
function renderKPIs(data) {
  const s  = data.stock  || {};
  const se = data.sentiment || {};

  const change = s.daily_change ?? 0;
  const isUp   = change >= 0;

  const kpis = [
    { label: "Ticker",        value: data.ticker,                              cls: "" },
    { label: "Last Close",    value: s.close ? `$${s.close.toFixed(2)}` : "—", cls: "" },
    { label: "Daily Change",  value: change !== undefined ? `${change >= 0 ? "+" : ""}${change.toFixed(2)}` : "—",
      cls: isUp ? "up" : "down" },
    { label: "Volume",        value: s.volume ? formatVolume(s.volume) : "—",  cls: "" },
    { label: "Avg Sentiment", value: se.avg_score !== undefined ? se.avg_score.toFixed(3) : "—",
      cls: (se.avg_score >= 0.05 ? "up" : se.avg_score <= -0.05 ? "down" : "") },
    { label: "Overall Tone",  value: capitalize(se.overall_label || "—"),      cls: "" },
  ];

  const strip = document.getElementById("kpiStrip");
  strip.innerHTML = kpis.map(k => `
    <div class="kpi">
      <div class="kpi-label">${k.label}</div>
      <div class="kpi-value ${k.cls}">${k.value}</div>
    </div>
  `).join("");
}

/* ── Prediction card ─────────────────────────────────────────── */
function renderPrediction(pred, modelInfo) {
  const badge   = document.getElementById("predBadge");
  const confBar = document.getElementById("confBar");
  const confTxt = document.getElementById("confText");
  const noteEl  = document.getElementById("modelNote");

  const dir  = pred.prediction || "N/A";
  const conf = pred.confidence || 0;
  const isUp = dir === "UP";

  badge.textContent = dir;
  badge.className   = "prediction-badge " + (isUp ? "up" : "down");

  confBar.style.width      = `${conf}%`;
  confBar.style.background = isUp ? "var(--up)" : "var(--down)";
  confTxt.textContent      = `${conf}% confidence`;
  noteEl.textContent       = pred.trained
    ? `Random Forest · ${modelInfo.message}`
    : "Heuristic fallback (train with more data)";
}

/* ── Sentiment donut ─────────────────────────────────────────── */
function renderSentimentDonut(sentiment) {
  const ctx = document.getElementById("sentimentChart").getContext("2d");

  if (sentimentChartInstance) sentimentChartInstance.destroy();

  const pos = sentiment.positive_pct || 0;
  const neu = sentiment.neutral_pct  || 0;
  const neg = sentiment.negative_pct || 0;

  sentimentChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels:   ["Positive", "Neutral", "Negative"],
      datasets: [{
        data:            [pos, neu, neg],
        backgroundColor: ["rgba(34,211,160,.8)", "rgba(240,180,41,.8)", "rgba(248,113,113,.8)"],
        borderColor:     ["#22d3a0", "#f0b429", "#f87171"],
        borderWidth:     1.5,
        hoverOffset:     6,
      }],
    },
    options: {
      cutout: "72%",
      plugins: { legend: { display: false }, tooltip: {
        callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}%` }
      }},
      animation: { animateRotate: true, duration: 800 },
    },
  });

  // Center label
  const center = document.getElementById("donutCenter");
  const label  = sentiment.overall_label || "neutral";
  const score  = (sentiment.avg_score || 0).toFixed(2);
  const colors = { positive: "#22d3a0", neutral: "#f0b429", negative: "#f87171" };
  center.innerHTML = `
    <div class="dc-score" style="color:${colors[label] || "#e8e8f0"}">${score}</div>
    <div class="dc-label">${capitalize(label)}</div>
  `;
}

/* ── Price chart ─────────────────────────────────────────────── */
function renderPriceChart(history, ticker) {
  if (!history || history.length === 0) return;

  const ctx    = document.getElementById("priceChart").getContext("2d");
  const labels = history.map(r => r.date);
  const closes = history.map(r => r.close);

  if (priceChartInstance) priceChartInstance.destroy();

  // Gradient fill
  const gradient = ctx.createLinearGradient(0, 0, 0, 260);
  gradient.addColorStop(0,   "rgba(240,180,41,0.25)");
  gradient.addColorStop(1,   "rgba(240,180,41,0.00)");

  priceChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label:           "Close Price",
        data:            closes,
        borderColor:     "#f0b429",
        borderWidth:     2,
        pointRadius:     3,
        pointBackgroundColor: "#f0b429",
        fill:            true,
        backgroundColor: gradient,
        tension:         0.35,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#0f0f1a",
          borderColor:     "rgba(240,180,41,0.3)",
          borderWidth:     1,
          titleColor:      "#f0b429",
          bodyColor:       "#e8e8f0",
          callbacks: { label: ctx => ` $${ctx.parsed.y.toFixed(2)}` },
        },
      },
      scales: {
        x: { ticks: { color: "#6b6b8a", font: { family: "'DM Mono'" } },
             grid:  { color: "rgba(255,255,255,0.04)" } },
        y: { ticks: { color: "#6b6b8a", font: { family: "'DM Mono'" },
                      callback: v => `$${v}` },
             grid: { color: "rgba(255,255,255,0.04)" } },
      },
    },
  });

  document.getElementById("chartTicker").textContent = ticker;
}

/* ── Articles ────────────────────────────────────────────────── */
function renderArticles(articles) {
  const list = document.getElementById("articlesList");
  if (!articles || articles.length === 0) {
    list.innerHTML = "<p style='color:var(--muted)'>No articles found.</p>";
    return;
  }

  list.innerHTML = articles.map((a, i) => {
    const label = a.sentiment_label || "neutral";
    const score = a.sentiment_score !== undefined ? a.sentiment_score.toFixed(3) : "";
    const delay = (i * 60) + "ms";
    return `
      <div class="article-item" style="animation-delay:${delay}">
        <div>
          <div class="article-title">
            <a href="${a.url}" target="_blank" rel="noopener">${escHtml(a.title)}</a>
          </div>
          <div class="article-summary">${escHtml(a.summary || a.description || "")}</div>
          <div class="article-meta">${escHtml(a.source)} &nbsp;·&nbsp; ${formatDate(a.published_at)}</div>
        </div>
        <div>
          <span class="sentiment-pill pill-${label}">
            ${capitalize(label)} ${score ? `(${score})` : ""}
          </span>
        </div>
      </div>
    `;
  }).join("");
}

/* ── Helpers ─────────────────────────────────────────────────── */
function setLoading(on) {
  document.getElementById("loader").classList.toggle("hidden", !on);
  const btn = document.getElementById("analyzeBtn");
  btn.disabled = on;
  btn.querySelector(".btn-text").textContent = on ? "Analysing…" : "Analyse";
}

function clearResults() {
  document.getElementById("results").classList.add("hidden");
  document.getElementById("kpiStrip").innerHTML   = "";
  document.getElementById("articlesList").innerHTML = "";
}

function showError(msg) {
  const el = document.getElementById("errorBanner");
  el.textContent = "⚠ " + msg;
  el.classList.remove("hidden");
}

function hideError() {
  document.getElementById("errorBanner").classList.add("hidden");
}

function capitalize(str) {
  if (!str) return "";
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function escHtml(str) {
  return (str || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function formatVolume(v) {
  if (v >= 1e9) return (v / 1e9).toFixed(1) + "B";
  if (v >= 1e6) return (v / 1e6).toFixed(1) + "M";
  if (v >= 1e3) return (v / 1e3).toFixed(0) + "K";
  return String(v);
}

function formatDate(iso) {
  if (!iso) return "";
  return iso.slice(0, 10);
}
