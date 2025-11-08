# src/aibps/fetch_capex.py
# Capex_Supply pillar with flexible percentile for short histories.
# Works even if you only have a few quarterly rows.

import os, sys, time
import pandas as pd
import numpy as np

RAW = os.path.join("data","raw","capex_manual.csv")
OUT = os.path.join("data","processed","capex_processed.csv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def _expanding_pct(series: pd.Series) -> pd.Series:
    # Expanding percentile of the LAST value in the window
    out = []
    vals = series.values
    for i in range(len(vals)):
        s = pd.Series(vals[: i+1])
        out.append(float(s.rank(pct=True).iloc[-1] * 100.0))
    return pd.Series(out, index=series.index)

def rolling_pct_rank_flexible(series: pd.Series, window: int = 120) -> pd.Series:
    """
    If history is short, use expanding percentile (needs >=3 pts to be meaningful).
    Once we have >= min_periods, switch to rolling window.
    """
    series = series.dropna()
    n = len(series)
    if n == 0:
        return series
    # For sparse series, ensure we emit something instead of all-NaN:
    if n < 24:
        return _expanding_pct(series)
    # Normal path: rolling 10y percentile with reasonable min_periods
    def _rank_last(x):
        s = pd.Series(x)
        return float(s.rank(pct=True).iloc[-1] * 100.0)
    minp = max(24, window // 4)
    return series.rolling(window, min_periods=minp).apply(_rank_last, raw=False)

def main():
    t0 = time.time()
    if not os.path.exists(RAW):
        print(f"ℹ️ {RAW} not found. Writing placeholder header so pipeline stays green.")
        pd.DataFrame(columns=["Capex_Supply"]).to_csv(OUT)
        return

    df = pd.read_csv(RAW)
    # Expect columns: date,company,metric,value,unit,notes  (extra cols allowed)
    if "date" not in df.columns or "value" not in df.columns:
        raise ValueError("capex_manual.csv must include at least 'date' and 'value' columns.")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[~df["date"].isna()].copy()
    df["date"] = df["date"].dt.to_period("M").dt.to_timestamp("M")

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df[~df["value"].isna()].copy()

    # Monthly aggregate across companies/metrics
    monthly = df.groupby("date")["value"].sum().sort_index()

    # Flexible percentile (emits values even with sparse quarterly data)
    capex_pct = rolling_pct_rank_flexible(monthly, window=120)

    out = pd.DataFrame({"Capex_Supply": capex_pct}).dropna(how="all")
    out.to_csv(OUT)
    print(f"💾 Wrote {OUT} ({len(out)} rows)")
    print("Tail:")
    print(out.tail(6))
    print(f"⏱  Done in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ fetch_capex.py: {e}")
        sys.exit(1)
