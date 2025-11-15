# 📘 AIBPS Methods
### Full computational methodology for the AI Bubble Pressure Score  
_Last updated: {{ auto-updated }}_

---

## 🧩 1. Purpose

This document explains *how* the AI Bubble Pressure Score (AIBPS) is computed:

- What data is ingested  
- How signals are normalized  
- How pillars are constructed  
- How the composite score is formed  
- How regimes are classified  

It is the technical companion to `overview.md` and `pillars.md`.

---

## 📥 2. Data Ingestion & Monthly Index

AIBPS ingests six categories of signals:

| Pillar          | Example Sources (high level)                |
|-----------------|---------------------------------------------|
| Market          | QQQ, SOXX, AI mega-cap basket               |
| Credit          | FRED HY OAS, IG OAS                         |
| Capex / Supply  | PNFI, UNXANO, hyperscaler capex             |
| Infrastructure  | Power / cooling / construction proxies      |
| Adoption        | Usage & adoption proxies                    |
| Sentiment       | Google Trends (AI, ChatGPT, OpenAI, etc.)   |

Each fetch script writes CSVs into:

- `data/raw/`
- `data/processed/`

All series are aligned to a **monthly, month-end (ME)** index:

- Date range: from 1980-01-31 to the latest available month  
- Frequency: monthly (end-of-month)  

The master index is created (conceptually):

- `1980-01-31, 1980-02-29, ..., 2025-11-30, ...`

Each pillar series is reindexed onto this monthly grid.

---

## 🧮 3. Normalization to 0–100

To combine heterogeneous signals, each pillar is put onto a **0–100 “pressure” scale**.

### 3.1 Rolling Z-Score

For a time series \( x_t \), we compute a rolling z-score:

\[
z_t = \frac{x_t - \mu_{(t-w,t)}}{\sigma_{(t-w,t)}}
\]

- \( w \) = rolling window length (in months), pillar-specific  
- \( \mu_{(t-w,t)} \) = rolling mean over the last \( w \) months  
- \( \sigma_{(t-w,t)} \) = rolling standard deviation over the last \( w \) months  

Typical windows (configured in `config.yaml`):

| Pillar         | Window (months) |
|----------------|-----------------|
| Market         | 60              |
| Credit         | 60              |
| Capex / Supply | 24              |
| Infrastructure | 36              |
| Adoption       | 24              |
| Sentiment      | 24              |

The z-scores are **clipped** to avoid blow-ups:

\[
z_t \leftarrow \max(-4, \min(z_t, 4))
\]

### 3.2 Sigmoid Transformation

To map z-scores into a smooth, bounded scale:

\[
s_t = \frac{1}{1 + e^{-k z_t}}
\]

- Default \( k \approx 1.2 \) (steepness parameter)

This function ensures:

- \( z_t = 0 \Rightarrow s_t = 0.5 \)  
- Large positive \( z_t \Rightarrow s_t \to 1 \)  
- Large negative \( z_t \Rightarrow s_t \to 0 \)

### 3.3 Scale to 0–100

Finally:

\[
p_t = 100 \cdot s_t
\]

So each pillar’s monthly series becomes a **pressure score** \( p_t \in [0, 100] \), where:

- ~0   → extremely low pressure (below historical norm)  
- ~50  → near historical norm  
- ~100 → extremely high pressure (far above historical norm)  

---

## 🧱 4. Pillar Construction

Each of the six pillars is constructed as follows:

1. Load raw time series relevant to that pillar  
2. Resample to month-end if needed  
3. Compute rolling z-score with pillar-specific window  
4. Apply clipping + sigmoid transform  
5. Optionally apply a light smoothing step (e.g., exponential moving average)  
6. Output a monthly 0–100 score  

For example, for the Market pillar:

- Raw: log-returns, valuations, or index levels for QQQ/SOXX/AI basket  
- Transform: rolling z-score (60-month window)  
- Map: sigmoid → 0–100  

The same pattern applies to Credit, Capex, Infra, Adoption, and Sentiment with different windows and raw metrics, but identical mathematical transformation.

(Details of **what** each pillar measures live in `pillars.md`.)

---

## ⚖️ 5. Composite Score (AIBPS)

Let \( P_i(t) \) be the normalized 0–100 pressure score for pillar \( i \) at time \( t \).

The **AIBPS composite** is:

\[
AIBPS(t) = \sum_{i=1}^{N} w_i \, P_i(t)
\]

Where:

- \( N = 6 \) (Market, Credit, Capex / Supply, Infra, Adoption, Sentiment)  
- \( w_i \) = weight of pillar \( i \), configured in `config.yaml`  

By default, weights are **equal**:

\[
w_i = \frac{1}{6} \quad \text{for all } i
\]

If the user provides custom weights, they are renormalized so that:

\[
\sum_{i=1}^{N} w_i = 1
\]

### Missing Data Handling in Composite

If, at a given \( t \), some pillars are missing (NaN) due to lack of data:

- Those pillars are **dropped** from the sum  
- The remaining weights are renormalized over the available pillars only  

Conceptually:

- Let \( A \) be the set of pillars with non-missing \( P_i(t) \)  
- Then:

\[
AIBPS(t) =
\frac{\sum_{i \in A} w_i \, P_i(t)}
{\sum_{i \in A} w_i}
\]

This allows the index to function even in earlier periods where not all pillars are available.

---

## 🛡️ 6. Robustness & Edge-Case Handling

### 6.1 Outliers

- Extreme raw values may occur (e.g., sudden spread spikes, market crashes).  
- The rolling z-score is **clipped** before applying the sigmoid, preventing single-month anomalies from exploding the scale.

### 6.2 Missing Raw Data

- When upstream data is missing for a month but is *known* to be continuous (e.g., FRED series or ETFs):  
  - A conservative forward-fill within that series may be used, depending on the fetch script.  
- No pillar ever borrows from another pillar (no cross-pillar imputation).

### 6.3 Synthetic or Placeholder Data

- Some early-history segments (e.g., sentiment pre-2000) may use synthetic or seeded data.  
- These segments are clearly logged in the pipeline.  
- The intent is to replace these with real historical series as they become available.

---

## 🌡️ 7. Regime Classification

For interpretability, the AIBPS value is bucketed into four regimes:

| AIBPS Range | Regime Name | Interpretation                          |
|-------------|-------------|------------------------------------------|
| 0–30        | Depressed   | Below-trend demand and activity          |
| 30–60       | Neutral     | Normal regime                            |
| 60–80       | Elevated    | Over-extension risk rising               |
| 80–100      | Bubble      | Historically unstable / bubble-like zone |

These regimes feed the **color bands** in the Streamlit chart (Green → Yellow → Orange → Red).

---

## 📂 8. Implementation: File Structure

Implementation is organized roughly as:

    src/aibps/
        fetch_market.py
        fetch_credit.py
        fetch_capex.py
        fetch_macro_capex.py
        fetch_infra.py
        fetch_adoption.py
        fetch_sentiment.py
        normalize.py
        compute.py

    data/
        raw/
        processed/
            market_processed.csv
            credit_fred_processed.csv
            macro_capex_processed.csv
            infra_processed.csv
            adoption_processed.csv
            sentiment_processed.csv
            aibps_monthly.csv

- `normalize.py` implements the rolling z-score + sigmoid logic.  
- `compute.py` merges all processed pillar files, applies weights, and writes `aibps_monthly.csv`.

---

## 🧾 9. Versioning & Change Control

Methodology changes are tracked in:

- `docs/changelog.md`

We follow a loose semantic convention:

- **MAJOR** – changes to normalization, pillar structure, or composite definition  
- **MINOR** – new pillars, new data sources, or additional debug views  
- **PATCH** – bug fixes, parameter tuning, visualization improvements  

---

## 📚 10. References (Selected)

Kindleberger, C. P., & Aliber, R. Z. (2011). *Manias, Panics, and Crashes*. Palgrave Macmillan.  
Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press.  
Taleb, N. N. (2012). *Antifragile*. Random House.  

---

_End of methods.md_
