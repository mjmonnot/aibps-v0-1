# 🧠 AI Bubble Pressure Score (AIBPS)
A data-driven, multi-pillar early-warning system estimating pressure building inside the modern AI-driven economic cycle.  
Combines market signals, credit conditions, hyperscaler + semiconductor capex, infrastructure build-out, enterprise AI adoption, and sentiment intensity into one 0–100 composite.

AIBPS answers a simple question:

**“How stretched is the AI ecosystem right now compared to its own historical patterns?”**

---

## 🚀 Live Dashboard
👉 **Streamlit App:** https://aibps-v0-1.streamlit.app

Updates automatically via GitHub Actions (daily at ~07:00 UTC).

---

# 📦 Project Structure

```
aibps-v0-1/
├── app/
│   └── streamlit_app.py               # Interactive dashboard
├── src/aibps/
│   ├── compute.py                     # Composite assembly, normalization, weighting
│   ├── normalize.py                   # Rolling Z, percentile, sigmoid transforms
│   ├── fetch_market.py                # Market data (yfinance)
│   ├── fetch_credit.py                # Credit spreads (FRED)
│   ├── fetch_macro_capex.py           # Hyperscaler, semiconductor, fab, infra CAPEX
│   ├── fetch_infra.py                 # Infrastructure build-out (electricity, cooling, grid)
│   ├── fetch_adoption.py              # Enterprise software, digital labor, cloud adoption
│   ├── fetch_sentiment.py             # News/text sentiment (synthetic + API-ready)
│   └── config.yaml                    # Pillar definitions, weights, normalization settings
├── data/
│   ├── raw/                           # Raw pulls from APIs
│   └── processed/                     # Normalized monthly indicators and composite
├── .github/workflows/
│   └── update-data.yml                # Automated daily refresh
├── docs/
│   ├── METHODS.md                     # How each pillar is built
│   ├── OVERVIEW.md                    # Conceptual framing + economic logic
│   ├── ARCHITECTURE.md                # Dataflow + processing pipeline
│   └── REFERENCES.md                  # Literature & citation support
├── requirements.txt
└── README.md
```

---

# ⚙️ How It Works

## 1. **Pillars**
AIBPS is composed of six equally weighted pillars (weights configurable):

| Pillar | What It Measures | Source Examples |
|--------|------------------|------------------|
| **Market** | AI-tilted asset returns & valuations | SOXX, QQQ, NVDA basket |
| **Credit** | Funding stress & corporate risk appetite | FRED HY OAS, IG OAS |
| **Capex** | Hyperscaler + semiconductor + fab investment cycle | FRED PNFI, hyperscaler CSV |
| **Infrastructure** | Power, grid build-out, cooling & data-center density | FRED ELECGEN, IPN313 |
| **Adoption** | Enterprise software, digital labor, productivity | FRED productivity, labor costs |
| **Sentiment** | Media hype, keyword fever, attention cycles | NLP-ready sentiment pipeline |

Each pillar is normalized using either:
- Rolling Z-score  
- Rolling Z-Sigmoid  
- Percentile rank  
- (configurable in `config.yaml`)

All subcomponents → normalized → averaged → pillar score → composite.

---

# 📈 Composite Score (0–100)

AIBPS represents the **relative extremity** of AI-related conditions:

- **0–25** → 🔵 *Cold / Undervalued / Early-cycle*
- **25–50** → 🟢 *Stable / Neutral*
- **50–75** → 🟡 *Elevated / Late-cycle*
- **75–90** → 🟠 *Stretched / Fragile*
- **90–100** → 🔴 *Bubble conditions historically seen before unwinds*

Bands adapt to the selected normalization scheme (default: rolling Z-sigmoid).

---

# 🔄 Automatic Daily Refresh
A GitHub Actions workflow:

- Pulls fresh data (yfinance + FRED + CSV hyperscaler capex)
- Normalizes using rolling windows
- Recomputes composite & pillars
- Commits new artifacts into `/data/processed/`
- Streamlit automatically reloads them

You can inspect the workflow at:
```
.github/workflows/update-data.yml
```

---

# 🧪 Local Development

## Install dependencies
```
pip install -r requirements.txt
```

## Run the composite builder manually
```
python src/aibps/compute.py
```

## Run Streamlit locally
```
streamlit run app/streamlit_app.py
```

---

# 📊 Interpretation Guide

## 📉 What a Rising AIBPS Means
A rising score typically reflects:

- Rapidly accelerating **hyperscaler / semiconductor capex**
- Tightening **credit conditions**
- Surging **market valuations**
- High **media attention or hype intensity**
- Infrastructure bottlenecks (power, cooling, grid)
- Low-friction **AI adoption** in enterprises

## 📈 What a Falling AIBPS Means
- AI cycles cooling off  
- Funding risk improving  
- Capex plateauing / deferred  
- Sentiment moderation  
- Market de-risking  

---

# 📚 Documentation
All full documents stored in `/docs/`:

- **OVERVIEW.md** – economic logic, comparisons to dot-com & housing bubbles  
- **METHODS.md** – detailed pillar construction + normalization math  
- **ARCHITECTURE.md** – ETL/dataflow diagrams  
- **REFERENCES.md** – peer-reviewed citations (APA 7)

---

# 🤝 Contributing

Pull requests welcome!  
Please open an issue before adding new pillars, subcomponents, or APIs.

---

# 📄 License
MIT License — free to fork, modify, and build upon.

---

# 🙋 Contact
Maintainer: **Matt Monnot, PhD**  
Industrial–Organizational Psychologist | People Analytics | Applied Econometrics  
GitHub: https://github.com/mjmonnot
