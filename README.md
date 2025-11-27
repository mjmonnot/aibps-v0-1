# ============================================
# README.md
# ============================================

# 🤖 AI Bubble Pressure Score (AIBPS)

The **AI Bubble Pressure Score (AIBPS)** is a research-grade, transparent index that tracks how overheated or subdued the AI economy is relative to its own history and to past macro bubble regimes (dot-com, housing/GFC, COVID).

AIBPS integrates **six major economic pillars**:
- 📈 **Market**
- 💳 **Credit**
- 🏭 **Capex / Supply**
- 🖥️ **Infrastructure**
- 🧩 **Adoption**
- 🧠 **Sentiment**

Each is normalized to **0–100** and combined into a single composite updated monthly.

---

## 📊 Live Dashboard

**👉 Streamlit App:**  
https://aibps-v0-1.streamlit.app

Features:
- Full AIBPS history (~1980–present)
- Dynamic bubble-regime shading (green → yellow → orange → red)
- Major macro event callouts (Dot-Com, Lehman, COVID, etc.)
- Pillar trajectories
- Sub-pillar debug charts
- Live adjustable pillar weights
- Pillar contribution breakdown

---

## 🧱 Project Structure

aibps-v0-1/
├── app/
│ └── streamlit_app.py
├── src/
│ └── aibps/
│ ├── compute.py
│ ├── normalize.py
│ ├── fetch_market.py
│ ├── fetch_credit.py
│ ├── fetch_macro_capex.py
│ ├── fetch_infra.py
│ ├── fetch_adoption.py
│ ├── fetch_sentiment.py
│ └── config.yaml
├── data/
│ ├── raw/
│ └── processed/
├── docs/
│ ├── METHODOLOGY.md
│ ├── ARCHITECTURE.md
│ └── INTERPRET_AIBPS.md
└── .github/workflows/update-data.yml


---

## ⚙️ How the System Works

### **1. Fetch raw data**
Automated scripts in `src/aibps/` pull:
- Market data (yfinance)
- Credit spreads (FRED)
- Capex (macro capex, hyperscaler AI capex CSV)
- Infrastructure proxies (FRED + curated CSVs)
- Adoption indicators (enterprise software, digital labor, etc.)
- Sentiment measures (consumer sentiment, uncertainty, VIX)

Raw → processed → monthly-aligned outputs written to  
`data/processed/*.csv`

---

### **2. Normalize & unify**
`compute.py`:
- Aligns all pillars on a **common monthly index** (≈1980+)
- Applies normalization (rolling-z-sigmoid, percentiles, z-score)
- Produces:
  - Normalized pillar scores (0–100)
  - Sub-pillar columns
  - Composite AIBPS
  - Smoothed AIBPS_RA (rolling average)

Outputs to:  
`data/processed/aibps_monthly.csv`

---

### **3. Visualize**
The Streamlit dashboard shows:
- 📈 AIBPS main line (0–100)
- 🟥/🟧/🟨/🟩 bubble regime shading
- 🏛️ historical macro events
- 🔧 pillar debug panels
- 🎛️ adjustable weights
- 🌡️ normalized pillar contributions

---

## ▶️ Run Locally



git clone https://github.com/mjmonnot/aibps-v0-1.git

cd aibps-v0-1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FRED_API_KEY="YOUR_KEY"

python src/aibps/fetch_market.py
python src/aibps/fetch_credit.py
python src/aibps/fetch_macro_capex.py
python src/aibps/fetch_infra.py
python src/aibps/fetch_adoption.py
python src/aibps/fetch_sentiment.py
python src/aibps/compute.py

streamlit run app/streamlit_app.py

---

## 🤖 GitHub Actions (Auto Update)

`.github/workflows/update-data.yml` refreshes:
- raw data  
- processed pillars  
- composite AIBPS  
- dashboard-ready CSV  

Runs on schedule using your secret `FRED_API_KEY`.

---

## 📚 Documentation

See the `docs/` folder for:
- `METHODOLOGY.md` – scientific underpinnings  
- `ARCHITECTURE.md` – compute + dataflow diagrams  
- `INTERPRET_AIBPS.md` – how to read the index  

---

# ============================================
# METHODOLOGY.md
# ============================================

# 📘 AIBPS Methodology

This document details the conceptual scaffolding, data selection, normalization logic, and composite construction behind the **AI Bubble Pressure Score (AIBPS)**.

---

## 🎯 1. Purpose & Philosophy

AIBPS answers:

> **“Relative to its own historical behavior, how stretched are AI-related economic conditions today?”**

The index is:
- **Comparative** (vs. history)
- **Cross-disciplinary** (markets, macro, adoption, psychology)
- **Non-predictive** (not a trading signal)
- **Transparent** (open methodology)

---

## 🧊 2. Pillars & Sub-Pillars

AIBPS uses **six pillars**, each scaled to **0–100**:

### **📈 Market**
Tracks AI-exposed asset valuations & momentum.  
Inputs:
- Nasdaq-100  
- SOXX / SMH  
- NVDA, AMD, AVGO, MSFT (optionally)  
Processing:
- Monthly close
- Composite index

---

### **💳 Credit**
Measures financial conditions & macro stress.  
Inputs (FRED):
- High-Yield OAS  
- IG OAS  
Processing:
- Inversion & standardization (high spreads → stress → lower score)

---

### **🏭 Capex / Supply**
Tracks capital formation into AI compute.

Sub-pillars:
- **Capex_Macro_Comp** (macro capex series)
- **Capex_Hyperscaler** (Meta, AWS, GCP, MSFT AI capex)
- **Capex_Supply** (composite)

---

### **🖥️ Infrastructure**
Physical capacity & constraints affecting AI scale-up.

Sub-pillars:
- **Infra_DC_Construction** (data center buildout)
- **Infra_Power_Capacity** (electrical generation)
- **Infra_Grid_Stress** (optional)
- Composite: **Infra**

---

### **🧩 Adoption**
Tracks real-world AI, digital, and cloud utilization.

Sub-pillars (active):
- **Adoption_Enterprise_Software**  
- **Adoption_Digital_Labor** (productivity + unit labor costs)

Scaffolded (requires future data):
- **Adoption_Cloud_Services**  
- **Adoption_Connectivity**

---

### **🧠 Sentiment**
Macro psychological temperature.

Inputs:
- UM Consumer Sentiment (UMCSENT)  
- Economic Policy Uncertainty (EPU)  
- VIX (monthly)

Composite: **Sentiment**

---

## 🧮 3. Normalization (0–100)

Applied via `normalize.py`:

### **Default method: Rolling-Z-Sigmoid**
- Computes rolling z-score (e.g., 36–60 months)
- Clips extreme outliers
- Passes through logistic sigmoid → stable 0–100 scale

### Alternatives
- Percentile rank  
- Standard z-score (for debugging)

---

## 🧠 Why Rolling-Z-Sigmoid?

- Adjusts for **regime drift** (AI economy structurally changing over decades)  
- Ensures **bounded scale** (0–100)  
- Offers **interpretable tail conditions**  
- Used in macro risk systems, climate metrics, and credit analytics  

---

## 🎛️ 4. Composite Score Formula

Let each pillar _p_ be normalized to 0–100.

**AIBPS(t) = Σ [ weight_p * pillar_p(t) ]**

Defaults: **equal weights (1/6 each)**  
Changeable in `config.yaml` or Streamlit UI.

The system also computes:

- **AIBPS_RA** → rolling 6-month smoothing  
- **z-intensity metrics** (internal)

---

## 📉 5. Interpretation Guide

| AIBPS Range | Interpretation |
|-------------|----------------|
| **0–20**    | Deep stress, washout, capitulation |
| **20–40**   | Below-trend conditions |
| **40–60**   | Normal / typical | 
| **60–80**   | Elevated, overheating |
| **80–100**  | Bubble-like conditions |

**Important:**  
AIBPS ≠ prediction.  
It shows **relative pressure**, not future performance.

---

## 🧱 6. Limitations

- AI-capex data is partly manual until APIs exist  
- Cloud/connectivity adoption proxies still incomplete  
- Sentiment is macro, not AI-specific  
- Normalization window selection affects sensitivity  
- Equal weighting may not reflect actual economic influence  

---

## 🔧 7. How to Extend

To add new sub-pillars:
1. Create new `fetch_*.py` script  
2. Add new processed CSV  
3. Update normalization mapping in `config.yaml`  
4. Include in `compute.py`  
5. Add visuals in Streamlit dashboard  

To adjust weights:
- Modify `config.yaml`  
- Or adjust sliders in Streamlit  

---

# ============================================
# END OF DOCUMENT
# ============================================
