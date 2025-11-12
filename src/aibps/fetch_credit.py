# MARKER: fetch_credit.py SAFE v3 — FRED w/ fallback, invert spreads, rolling 10y percentiles
import os, sys, time
import pandas as pd, numpy as np

RAW_DIR = os.path.join("data","raw")
PRO_DIR = os.path.join("data","processed")
os.makedirs(RAW_DIR, exist_ok=True); os.makedirs(PRO_DIR, exist_ok=True)

HY_SERIES = "BAMLH0A0HYM2"   # HY OAS
IG_SERIES = "BAMLCC0A0CM"    # IG OAS

def rolling_pct_rank(series: pd.Series, window: int = 120, invert: bool=False) -> pd.Series:
    """Percentile rank of last value within trailing window; invert=True ranks tighter spreads higher."""
    def _rank_last(x):
        s = pd.Series(x)
        if invert: s = -s
        return (s.rank(pct=True).iloc[-1] * 100)
    return series.rolling(window, min_periods=max(24, window//4)).apply(_rank_last, raw=False)

def fetch_fred():
    key = os.getenv("FRED_API_KEY")
    if not key:
        print("⚠️ No FRED_API_KEY — will use sample/synthetic.")
        return None
    try:
        from fredapi import Fred
        fred = Fred(api_key=key)

        # explicitly pull as much history as possible
        start_date = "1980-01-01"

        hy = fred.get_series(HY_SERIES, observation_start=start_date)
        ig = fred.get_series(IG_SERIES, observation_start=start_date)

        df = pd.concat(
            [
                pd.Series(hy, name="HY_OAS"),
                pd.Series(ig, name="IG_OAS")
            ],
            axis=1
        )

        df.index = pd.to_datetime(df.index)
        df.index.name = "Date"
        print(f"✅ Fetched FRED data from {df.index.min().date()} to {df.index.max().date()}")
        return df.sort_index()

    except Exception as e:
        print(f"⚠️ FRED fetch failed: {e}")
        return None


def load_sample_or_generate():
    sample = os.path.join("data","sample","credit_fred_sample.csv")
    if os.path.exists(sample):
        print(f"ℹ️ Using sample credit file: {sample}")
        return pd.read_csv(sample, index_col=0, parse_dates=True)
    # synthetic fallback
    idx = pd.date_range("2015-01-31","2025-12-31",freq="M")
    hy = np.linspace(6.5,4.5,len(idx)) + np.random.normal(0,0.2,len(idx))
    ig = np.linspace(2.2,1.6,len(idx)) + np.random.normal(0,0.1,len(idx))
    df = pd.DataFrame({"HY_OAS":hy,"IG_OAS":ig}, index=idx); df.index.name="Date"
    return df

def main():
    print("MARKER fetch_credit.py v3 — pandas", pd.__version__)
    t0 = time.time()

    raw = fetch_fred() or load_sample_or_generate()
    raw_path = os.path.join(RAW_DIR,"credit_fred.csv")
    raw.to_csv(raw_path)
    print(f"💾 raw → {raw_path}  rows={len(raw)}")

    # monthly (ensure monthly index)
    monthly = raw.resample("M").last()

    # rolling 10y percentiles; invert spreads so tighter (risk-on) = higher %
    hy_pct = rolling_pct_rank(monthly["HY_OAS"], window=120, invert=True)
    ig_pct = rolling_pct_rank(monthly["IG_OAS"], window=120, invert=True)

    out = monthly.copy()
    out["HY_OAS_pct"] = hy_pct
    out["IG_OAS_pct"] = ig_pct
    out = out.dropna(subset=["HY_OAS_pct","IG_OAS_pct"])

    pro_path = os.path.join(PRO_DIR,"credit_fred_processed.csv")
    out.to_csv(pro_path)
    print(f"💾 processed → {pro_path}  rows={len(out)}  cols={list(out.columns)}")
    print(f"⏱  Done in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    try: main()
    except Exception as e:
        print(f"❌ fetch_credit.py: {e}"); sys.exit(1)
