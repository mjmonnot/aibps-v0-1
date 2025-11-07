# src/aibps/compute.py
# Robust compute: build Market/Credit pillars from processed inputs, align monthly, no stubs
import os, sys, time
import pandas as pd
import numpy as np

PRO = os.path.join("data","processed")
OUT = os.path.join(PRO, "aibps_monthly.csv")
os.makedirs(PRO, exist_ok=True)

def read_proc(name):
    path = os.path.join(PRO, name)
    if not os.path.exists(path):
        return None
    try:
        return pd.read_csv(path, index_col=0, parse_dates=True).sort_index()
    except Exception as e:
        print(f"⚠️ Failed to read {path}: {e}")
        return None

def to_month_end(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    # Ensure DateTimeIndex & month-end alignment
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()]
    return df.resample("M").last()

def main():
    t0 = time.time()

    market = read_proc("market_processed.csv")
    credit = read_proc("credit_fred_processed.csv")
    capex  = read_proc("capex_processed.csv")       # optional
    infra  = read_proc("infra_processed.csv")       # optional
    adopt  = read_proc("adoption_processed.csv")    # optional

    market = to_month_end(market)
    credit = to_month_end(credit)
    capex  = to_month_end(capex)
    infra  = to_month_end(infra)
    adopt  = to_month_end(adopt)

    pillars = []

    # ---- Market pillar: average of all MKT_* columns (0–100) ----
    if market is not None and not market.empty:
        mcols = [c for c in market.columns if c.startswith("MKT_")]
        if mcols:
            mk = market[mcols].mean(axis=1, skipna=True).to_frame("Market")
            pillars.append(mk)

    # ---- Credit pillar: average of *_pct columns (0–100) ----
    if credit is not None and not credit.empty:
        ccols = [c for c in credit.columns if c.endswith("_pct")]
        if ccols:
            cr = credit[ccols].mean(axis=1, skipna=True).to_frame("Credit")
            pillars.append(cr)

    # ---- Optional pillars (already 0–100) ----
    if capex is not None and "Capex_Supply" in capex.columns:
        pillars.append(capex[["Capex_Supply"]])
    if infra is not None and "Infra" in infra.columns:
        pillars.append(infra[["Infra"]])
    if adopt is not None and "Adoption" in adopt.columns:
        pillars.append(adopt[["Adoption"]])

    if not pillars:
        raise RuntimeError("No pillar inputs found in data/processed/. Ensure market/credit processed CSVs exist.")

    # Outer-join all pillars on month-end index (keep data even if others missing)
    df = pd.concat(pillars, axis=1, join="outer").sort_index()

    # Default weights; app will reweight interactively
    desired  = ["Market","Capex_Supply","Infra","Adoption","Credit"]
    present  = [p for p in desired if p in df.columns]
    defaults = {"Market":0.25,"Capex_Supply":0.25,"Infra":0.20,"Adoption":0.15,"Credit":0.15}
    w = np.array([defaults[p] for p in present], dtype=float)
    w = w / w.sum()

    # Static composite (for reference); app recomputes with user weights
    df["AIBPS"] = (df[present] * w).sum(axis=1, skipna=True)
    df["AIBPS_RA"] = df["AIBPS"].rolling(3, min_periods=1).mean()

    df.to_csv(OUT)
    print(f"💾 Wrote {OUT} with pillars: {present} (rows={len(df)})")
    print(f"⏱  Done in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ compute.py: {e}")
        sys.exit(1)
