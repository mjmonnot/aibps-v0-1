# src/aibps/fetch_macro_capex.py
# Macro Capex (FRED) -> monthly line -> percentile (0–100)
# Robust: searches FRED for the correct PNFI series if a hard-coded id fails.

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

def pick_series(fred):
    """
    Pick a good PNFI series from FRED.
    Priority:
      1) Real Private Nonresidential Fixed Investment (quarterly)
      2) Private Nonresidential Fixed Investment (current dollars, quarterly)
    """
    # Try common IDs first (fast path)
    candidates = [
        ("PNFI", "Real Private Nonresidential Fixed Investment (chained $)"),
        ("PNFIC1", "Real Private Nonresidential Fixed Investment (SAAR, chained $)"),
        ("PNFIC96", "Chain-type quantity index (real)"),
        ("PNFIC", "Private Nonresidential Fixed Investment (current $)"),
    ]
    for sid, why in candidates:
        try:
            s = fred.get_series(sid, observation_start="2010-01-01")
            if s is not None and len(s) > 0:
                print(f"✔ Using FRED series {sid}: {why}")
                return sid, s
        except Exception as e:
            print(f"… {sid} failed: {e}")

    # Slow path: search FRED
    try:
        df = fred.search("Private Nonresidential Fixed Investment")
        if df is not None and not df.empty:
            # Filter to quarterly
            if "frequency_short" in df.columns:
                df = df[df["frequency_short"].str.upper() == "Q"]
            # Prefer 'Real' in title
            if "title" in df.columns:
                df = df.sort_values(
                    by=["title"], key=lambda c: c.str.contains("Real", case=False, na=False), ascending=False
                )
            # Pick the first viable id
            sid = df.iloc[0]["id"]
            s = fred.get_series(sid, observation_start="2010-01-01")
            if s is not None and len(s) > 0:
                print(f"✔ Using FRED series from search: {sid} — {df.iloc[0].get('title','')}")
                return sid, s
    except Exception as e:
        print(f"FRED search failed: {e}")

    raise RuntimeError("Could not find a valid PNFI series on FRED.")

def main():
    t0 = time.time()
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print("❌ FRED_API_KEY not found. Set GitHub Secret FRED_API_KEY.")
        pd.DataFrame(columns=["Capex_Supply_Macro"]).to_csv(OUT)
        sys.exit(1)

    try:
        from fredapi import Fred
    except Exception as e:
        print(f"❌ fredapi not installed: {e}")
        pd.DataFrame(columns=["Capex_Supply_Macro"]).to_csv(OUT)
        sys.exit(1)

    fred = Fred(api_key=api_key)

    # Select a working PNFI series
    sid, q = pick_series(fred)

    # Ensure datetime index (quarter-ends) and sort
    q.index = pd.to_datetime(q.index, errors="coerce")
    q = q[~q.index.isna()].sort_index()

    # Convert quarterly to monthly via linear interpolation on a month-end grid
    start = q.index.min().to_period("M").to_timestamp("M")
    end   = pd.Timestamp.today().to_period("M").to_timestamp("M")
    idx_m = pd.period_range(start, end, freq="M").to_timestamp("M")
    m = q.reindex(idx_m).interpolate(method="linear")
    m.index.name = "date"

    # Percentile scaling (0–100) with flexible fallback
    capex_pct = rolling_pct_rank_flexible(m, window=120)

    out = pd.DataFrame({"Capex_Supply_Macro": capex_pct}).dropna(how="all")
    out.to_csv(OUT)

    print(f"💾 Wrote {OUT} ({len(out)} rows) • FRED series used: {sid}")
    print("Tail:")
    print(out.tail(6))
    print(f"⏱  Done in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ fetch_macro_capex.py: {e}")
        sys.exit(1)
