# 🧭 How to Interpret the AI Bubble Pressure Score (AIBPS)

_Last updated: {{DATE}}_  
Version: v0.1

AIBPS measures **systemwide bubble pressure** across AI-related markets, credit, infrastructure, sentiment, and adoption.  
This guide explains how to read the score, interpret pillar signals, and understand divergences and historical parallels.

---

# 1. What the AIBPS Measures

AIBPS summarizes conditions across six domains:

- **Market Valuation Pressure**  
- **Credit & Liquidity Regime**
- **Capex & Supply Investment Cycles**
- **Infrastructure (power/datacenter) Constraints**
- **Adoption Momentum**
- **Public Attention & Narrative Heat (Sentiment)**

The index answers one question:

> **To what degree do current conditions resemble the buildup to previous speculative bubbles?**

It does *not* predict prices — it quantifies *pressure*, not direction.

---

# 2. The 0–100 Bubble Pressure Scale

The score is normalized so each reading fits into a regime:

| Score | Interpretation |
|-------|----------------|
| **0–20 → Low** | Underheated, fundamentals strong vs. narratives |
| **20–40 → Normal** | Stable expansion, no major excesses |
| **40–60 → Elevated** | Momentum forming, risk appetite rising |
| **60–80 → Overheated** | High valuations, liquidity thinning, hype accelerating |
| **80–100 → Extreme** | Historically similar to bubble peaks (Dot Com, 2020 SPAC mania, Crypto 2021, etc.) |

A reading of **90+** does *not* predict an immediate correction, but indicates rare historical stress conditions.

---

# 3. Interpreting the Regime Color Bands

The main chart displays background shading:

- **Green (0–40):** Healthy expansion  
- **Yellow (40–60):** Frothy  
- **Orange (60–80):** Overheated  
- **Red (80–100):** Historically extreme pressure  

If the line sits in **Red**, it suggests conditions comparable to known bubble peaks when measured across many indicators simultaneously.

---

# 4. Interpreting Pillar Trajectories

Each pillar is displayed below the main AIBPS chart.

## ✔ Market
High = speculative valuations exceed fundamentals  
Low = markets cooling or consolidating  

Look for:
- Sharp upward slope → narrative chasing  
- Long plateaus → persistent over-optimism  

## ✔ Credit
High = funding conditions strained  
Low = easy liquidity supporting growth  

Credit often **tightens before markets crack**.

## ✔ Capex Supply  
High = heavy investment → potential overbuild  
Low = underinvestment → possible scarcity  

Useful for identifying supply gluts or bottlenecks.

## ✔ Infrastructure  
High = power/datacenter constraints intensifying  
Low = infrastructure expanding comfortably  

AI demand can outpace energy/thermal capacity.

## ✔ Adoption  
High = businesses adopting rapidly (or reporting they are)  
Low = experimental phase / early cycle  

## ✔ Sentiment  
High = hype, media intensity, unrealistic expectations  
Low = low public attention or narrative fatigue  

Sentiment typically peaks *before* fundamentals do.

---

# 5. Reading Divergences (Important)

Divergences between pillars reveal hidden dynamics:

### **A. Market ↑ while Credit ↓**  
Speculation rising despite tightening liquidity.  
Seen in **late 1999** and **late 2021**.

### **B. Sentiment ↑ while Adoption ↓**  
Hype far ahead of real deployment.  
Classic bubble signature.

### **C. Capex ↑ while Market ↓**  
Buildout continues even as prices soften.  
Often precedes **post-bubble supply gluts**.

### **D. Infra ↑ while Adoption ↑ but Credit ↑**  
Rapid growth straining both physical and financial systems.  
Seen in **2024–2025 GPU/power crunch**.

These divergences make AIBPS more informative than any single indicator.

---

# 6. Interpreting Historical Callouts (Dot Com, Housing, AI 2023–25)

The chart includes vertical markers identifying major economic bubbles.

### Dot Com (1999–2000)
- Market pillar extreme  
- Sentiment off the charts  
- Credit tightening quietly underneath  

### Housing Bubble (2005–2007)
- Credit pillar signals strongly  
- Market less extreme  
- Adoption outside tech still rising  

### AI 2023–2025 run-up
- Sentiment & Market surge  
- Infrastructure pillar under growing strain  
- Capex catching up with notable lag  

Historical regimes help contextualize current readings:  
**“Are we in the same zone?”** does not mean *“will it crash?”*  
but **“are conditions comparable?”**

---

# 7. Technical Sidebar (for Analysts)

### **AIBPS uses:**
- Rolling **Z-score normalization** per pillar  
- Z-clipping to avoid outlier domination  
- **Sigmoid transforms** to produce a bounded 0–100 pressure scale  
- Pillar weighting (equal by default; adjustable)  
- A rolling-adjusted composite (AIBPS_RA) to smooth high-frequency noise  

### Why rolling normalization?
- Ensures comparability across long histories  
- Avoids distortions from structural breaks (e.g., tech dominance post-2010)  
- Makes the score sensitive to relative intensity, not raw magnitude  

### Why sigmoid?
- Converts z-scores into intuitive “pressure” space  
- Prevents pillar extremes from blowing up composite scores  
- Places non-linear emphasis on the tails (where bubbles form)

---

# 8. Common Misinterpretations

| Misread | Clarification |
|--------|---------------|
| “A high AIBPS = imminent crash.” | No — it means stress resembles past bubble peaks, not that reversal is predicted. |
| “Sentiment is 100 so the bubble must be bursting.” | Sentiment peaks *before* declines; it is a leading indicator, not a trigger. |
| “If one pillar is low, the system is safe.” | Bubble pressure emerges from **synchronization**, not individual spikes. |
| “Composite is flat, so nothing is happening.” | Flat composites often mask internal **pillar divergences**, which matter greatly. |

---

# 9. Practical Interpretation Guide

### **If AIBPS is rising:**
Systemwide pressure is increasing.  
Signals may be diverging but pointing toward overheating.

### **If AIBPS is falling:**
Either:
- A real cooling-off is happening  
- Or pressure is shifting between pillars (e.g., sentiment down, infra up)

### **If AIBPS is stable but elevated (60–80):**
This historically corresponds to “slow burn bubbles,”  
not immediate collapse, but vulnerability.

### **If AIBPS enters the red zone (80–100):**
Historically rare.  
Suggests systemwide stretch across **multiple independent domains**.

---

# 10. Summary

AIBPS is best read as:

- A **composite systemic pressure signal**  
- A **framework for comparing cycles**  
- A **diagnostic tool**, not a prediction engine  

When multiple pillars synchronize at high levels, history shows elevated risk of unsustainable conditions.

Use AIBPS as a **lens**, not a prophecy.

---

_End of Document_  
Save as: `docs/how_to_interpret_aibps.md`
