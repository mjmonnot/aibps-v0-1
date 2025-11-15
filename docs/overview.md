# 🧭 AI Bubble Pressure Score (AIBPS) — Overview
### A high-level guide to what the AIBPS is, how it works, and how to interpret it.

_Last updated: {{ auto-updated by GitHub Actions }}_

---

# 🌐 What Is the AIBPS?

The **AI Bubble Pressure Score (AIBPS)** is a composite index designed to monitor systemic overheating across the artificial intelligence ecosystem.

It answers a single question:

> **How much pressure is building in the AI market, relative to long-term historical conditions?**

A single monthly score (0–100) summarizes six pillars:

1. **Market valuations**
2. **Credit & financing conditions**
3. **Capex / supply investment**
4. **Infrastructure strain**
5. **Technology adoption velocity**
6. **Sentiment / hype intensity**

---

# 🏗 How the AIBPS Works (High Level)

Each pillar is transformed into a comparable **0–100 pressure scale** using a rolling Z-score + sigmoid normalization.  
The pillars are combined using equal weights by default, and the composite is displayed as:

- a long-term line (1980 → present)  
- regime shading bands  
- annotated economic bubbles  
- dynamic decomposition into per-pillar contributions  

The result:  
**A single interpretable number representing current AI overheating pressure.**

---

# 📊 Why Use a Composite Index?

AI markets are influenced by **multiple independent subsystems**:

- equity speculation  
- venture and credit markets  
- datacenter buildout  
- corporate capex  
- cloud/inference demand  
- hype and narrative cycles  

No single metric captures these dynamics alone.  
A composite index:

- reduces noise  
- integrates contradictory signals  
- adapts as new data streams are added  
- provides a historically anchored reference frame  

---

# 🪜 Pillar Overview (Summary Only)

> Full definitions are in `pillars.md`.  
> Full math is in `methods.md`.

### **1. Market**
Captures valuation regime, speculative momentum, and systemic pricing pressure.

### **2. Credit**
Measures ease/tightness of funding, from venture to corporate debt markets.

### **3. Capex / Supply**
Tracks AI-related investment cycles (fabs, cloud capex, GPU supply, robotics).

### **4. Infrastructure**
Measures strain in power, cooling, land, grid capacity, OEM bottlenecks, and rack lead times.

### **5. Adoption**
Captures how rapidly AI products are being integrated into business operations and consumer behavior.

### **6. Sentiment**
Measures hype intensity using narrative frequency and attention-based signals.

---

# 🔦 How to Interpret the AIBPS

### **0–25 (Cool Zone – Blue/Green)**
- Under-heated  
- Capital conditions stable  
- Narrative volume low  
- Historically associated with early cycle positioning opportunities  

### **25–50 (Normal Zone – Yellow)**
- Healthy growth  
- No systemic heat  
- Mixed signals across pillars  

### **50–75 (Warm Zone – Orange)**
- Elevated pressure  
- Some overheating  
- Fundamentals may lag sentiment  

### **75–90 (Hot Zone – Red)**
- High systemic strain  
- Rapid capex acceleration  
- High valuations or tightening credit  
- Historically corresponds to pre-correction environments  

### **90+ (Critical – Deep Red)**
Clear bubble pressure:

- extreme sentiment  
- infrastructure limits  
- vertical capex ramps  
- overinvestment cycles  

Historically aligns with peaks preceding **mean reversion**.

---

# 🕰 Historical Reference Points

The AIBPS dashboard includes markers for:

- **Dot-com peak (Mar 2000)**  
- **Housing bubble peak (2006)**  
- **Lehman failure (Sept 2008)**  
- **COVID tech spike (2020–21)**  
- **Generative AI acceleration (2022–2025)**  

These provide contextual anchors for interpreting current pressure.

---

# 📈 Why Start in 1980?

Beginning the index in **1980** ensures:

- multiple historical bubbles  
- multiple tightening cycles  
- long-horizon volatility regimes  
- baseline compute era → internet era → mobile era → AI era  

This allows robust **multi-decade Z-score normalization**.

---

# ⚙️ Data Sources (High Level)

The system integrates:

- **Equity & ETF prices (Yahoo Finance)**  
- **Corporate bond spreads (FRED)**  
- **AI / cloud / data center capex (FRED + synthetic seed)**  
- **Power & infra bottlenecks (FRED + vendor indices)**  
- **Technology adoption proxies**  
- **Google Trends sentiment metrics**  

Full details: `methods.md`.

---

# 🧩 System Components

This repo contains:

- **fetch scripts** to gather raw data  
- **processing scripts** that transform datasets  
- **normalization & weighting engine**  
- **compute.py** that builds the monthly composite  
- **Streamlit app** for visualization  
- **docs/** folder for explainers  

---

# 🧪 What This Index *Is Not*

- Not investment advice  
- Not a predictor of crashes  
- Not a timing tool for day-trading  
- Not an opinion — it is fully rules-based  

---

# 🧭 What This Index *Is*

A cross-domain **risk thermometer** designed to show the **system-level pressure** inside the AI ecosystem.

It integrates:

- fundamentals  
- capital flows  
- infrastructure limits  
- macro credit  
- narrative sentiment  

into a single interpretable score.

---

# 🔗 Related Documents in This Repo

- **methods.md** → full math + normalization  
- **pillars.md** → individual pillar definitions  
- **architecture.md** → system diagrams, fetch graph  
- **changelog.md** → update history  

---

# 📬 Contact / Attribution

Methodology & design:  
**Matthew J. Monnot, PhD**  
Industrial-Organizational Psychologist, People Analytics & Applied Data Science

Streamlit app & automation:  
GitHub Actions → nightly data refresh  
OpenAI + Streamlit tech stack

---


