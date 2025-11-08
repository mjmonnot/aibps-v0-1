# src/aibps/fetch_macro_capex.py
# Macro Capex (FRED PNRESCAPQUSQ) -> monthly line -> percentile (0–100)
# Writes: data/processed/macro_capex_processed.csv with column Capex_Supply_Macro
import os, sys, time
import pandas as pd
import numpy as np

OUT = os.path.join("data", "processed", "macro_capex_processed.csv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def _expanding_pct(series: pd.Series) -> pd.Series:
    out = []
    vals = series.values
    for i in range(len(vals)):
        s = pd.Series(vals[:i+1])
        out.append(float(s.rank(pct=True).iloc[-1] * 100.0))
    return pd.Series(out, index=series.index)

def rolling_pct_rank_flexible(series: pd.Series, window: int = 120) -> pd.Series:
    """Expanding percentile for short histories; rolling for longer."""
    series = series.dropna()
    n = len(series)
    if n == 0:
        return series
    if n < 24:
        return _expanding_pct(series)
    def _rank_last(x):
        s = pd.Series(x)
        return float(s.rank(pct=True).iloc[-1] * 100.0)
    minp = max(24, window // 4)
    return series.rolling(window, min_periods=minp).apply(_rank_last, raw=False)

def main():
    t0 = time.time()
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print("❌ FRED_API_KEY not found in environment; set GitHub Secret FRED_API_KEY.")
        # Write empty header so pipeline stays green but signal caller
        pd.DataFrame(columns=["Capex_Supply_Macro"]).to_csv(OUT)
        sys.exit(1)

    try:
        from fredapi import Fred
    except Exception as e:
        print(f"❌ fredapi not installed: {e}")
        pd.DataFrame(columns=["Capex_Supply_Macro"]).to_csv(OUT)
        sys.exit(1)

    fred = Fred(api_key=api_key)

    # 1) Fetch BEA/FRED quarterly series (Billions SAAR), from 2010 for depth
    series_id = "PNRESCAPQUSQ"
    q = fred.get_series(series_id, observation_start="2010-01-01")
    if q is None or len(q) == 0:
        print("❌ FRED returned empty series.")
        pd.DataFrame(columns=["Capex_Supply_Macro"]).to_csv(OUT)
        sys.exit(1)

    q.index = pd.to_datetime(q.index)  # quarter end
    q = q.sort_index()

    # 2) Convert to monthly: linear interpolation between quarter-ends
    start = q.index.min().to_period("M").to_timestamp("M")
    end   = pd.Timestamp.today().to_period("M").to_timestamp("M")
    idx_m = pd.period_range(start, end, freq="M").to_timestamp("M")
    m = q.reindex(idx_m).interpolate(method="linear")  # monthly SAAR proxy

    # Optional normalization (e.g., per GDP) can go here if desired

    # 3) Percentile scaling (0–100) using 10y window with flexible fallback
    capex_pct = rolling_pct_rank_flexible(m, window=120)
    capex_pct.index.name = "date"

    out = pd.DataFrame({"Capex_Supply_Macro": capex_pct}).dropna(how="all")
    out.to_csv(OUT)
    print(f"💾 Wrote {OUT} ({len(out)} rows)")
    print("Tail:")
    print(out.tail(6))
    print(f"⏱  Done in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    main()
