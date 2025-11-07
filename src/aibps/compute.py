# src/aibps/compute.py
# Robust compute: coercion to numeric, strict month-end alignment, defensive pillar build, no stubs
import os, sys, time
import pandas as pd
import numpy as np

PRO = os.path.join("data", "processed")
OUT = os.path.join(PRO, "aibps_monthly.csv")
os.makedirs(PRO, exist_ok=True)

def read_proc_csv(filename: str) -> pd.DataFrame | None:
    path = os.path.join(PRO, filename)
    if not os.path.exists(path):
        print(f"ℹ️ Missing: {path}")
        return None
    try:
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        # Normalize index -> month-end timestamp
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, errors="coerce")
        df = df[~df.index.isna()].copy()
        df.index = df.index.to_period("M").to_timestamp("M")
        # Coerce all columns to numeric (non-numeric -> NaN), drop all-NaN columns
        for c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna(axis=1, how="all").sort_index()
        return df
    except Exception as e:
        print(f"⚠️ Failed to read {path}: {e}")
        return None

def build_market(market_df: pd.DataFrame | None) -> pd.DataFrame | None:
    if market_df is None or market_df.empty:
        return None
    # Prefer engineered columns beginning with MKT_
    mcols = [c for c in market_df.columns if c.startswith("MKT_")]
    if not mcols:
        # fallback: use any numeric columns available
        mcols = [c for c in market_df.columns if pd.api.types.is_numeric_dtype(market_df[c])]
    if not mcols:
        return None
    ser = market_df[mcols].mean(axis=1, skipna=True)
    return ser.to_frame("Market")

def build_credit(credit_df: pd.DataFrame | None) -> pd.DataFrame | None:
    if credit_df is None or credit_df.empty:
        return None
    ccols = [c for c in credit_df.columns if c.endswith("_pct")]
    if not ccols:
        ccols = [c for c in credit_df.columns if pd.api.types.is_numeric_dtype(credit_df[c])]
    if not ccols:
        return None
    ser = credit_df[ccols].mean(axis=1, skipna=True)
    return ser.to_frame("Credit")

def keep_col(df: pd.DataFrame | None, name: str) -> pd.DataFrame | None:
    if df is None or df.empty:
        return None
    return df[[name]] if name in df.columns else None

def main():
    t0 = time.time()

    market = read_proc_csv("market_processed.csv")
    credit = read_proc_csv("credit_fred_processed.csv")
    capex  = read_proc_csv("capex_processed.csv")
    infra  = read_proc_csv("infra_processed.csv")
    adopt  = read_proc_csv("adoption_processed.csv")

    pillars = []

    mk = build_market(market)
    if mk is not None:
        pillars.append(mk)

    cr = build_credit(credit)
    if cr is not None:
        pillars.append(cr)

    cx = keep_col(capex, "Capex_Supply")
    if cx is not None: pillars.append(cx)

    inf = keep_col(infra, "Infra")
    if inf is not None: pillars.append(inf)

    adp = keep_col(adopt, "Adoption")
    if adp is not None: pillars.append(adp)

    if not pillars:
        raise RuntimeError("No pillar inputs found in data/processed/. Ensure market/credit processed CSVs exist.")

    # Outer-join across all month-ends, ensure monthly frequency
    df = pd.concat(pillars, axis=1, join="outer").sort_index()
    df = df[~df.index.duplicated(keep="last")].asfreq("M")  # keep month-end grid

    # Default weights (app will recalc interactively; this is just reference)
    desired  = ["Market","Capex_Supply","Infra","Adoption","Credit"]
    present  = [p for p in desired if p in df.columns]
    defaults = {"Market":0.25,"Capex_Supply":0.25,"Infra":0.20,"Adoption":0.15,"Credit":0.15}
    w = np.array([defaults[p] for p in present], dtype=float)
    w = w / w.sum() if w.sum() else np.ones(len(present))/len(present)

    df["AIBPS"] = (df[present] * w).sum(axis=1, skipna=True)
    df["AIBPS_RA"] = df["AIBPS"].rolling(3, min_periods=1).mean()

    # Print quick sanity before writing
    print("---- Sanity (tails) ----")
    for col in ["Market","Credit","Capex_Supply","Infra","Adoption","AIBPS","AIBPS_RA"]:
        if col in df.columns:
            print(col, "tail:")
            print(df[col].tail(3))

    df.to_csv(OUT)
    print(f"💾 Wrote {OUT} with pillars: {present} (rows={len(df)})")
    print(f"⏱  Done in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ compute.py: {e}")
        sys.exit(1)
