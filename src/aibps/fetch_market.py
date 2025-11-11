# src/aibps/fetch_market.py
# MARKER: fetch_market.py SAFE v4 — monthly resample, 12m change, rolling 10y percentiles
import os, sys, time
import numpy as np
import pandas as pd

RAW_DIR = os.path.join("data","raw")
PRO_DIR = os.path.join("data","processed")
os.makedirs(RAW_DIR, exist_ok=True); os.makedirs(PRO_DIR, exist_ok=True)

START   = "1980-01-01"
TICKERS = ["SOXX","QQQ"]

def rolling_pct_rank(series: pd.Series, window: int = 120) -> pd.Series:
    """Percentile rank of the last value within a trailing window on MONTHLY data."""
    def _rank_last(x):
        s = pd.Series(x)
        return float(s.rank(pct=True).iloc[-1] * 100.0)
    return series.rolling(window, min_periods=max(24, window//4)).apply(_rank_last, raw=False)

def download_live():
    try:
        import yfinance as yf
        frames = []
        for t in TICKERS:
            df = yf.download(t, start=START, auto_adjust=True, progress=False)
            if df is None or df.empty or "Close" not in df:
                print(f"⚠️ yfinance empty for {t}; skipping"); continue
            s = df["Close"]
            s.index = pd.to_datetime(s.index); s.index.name = "Date"
            frames.append(s.to_frame(name=t))              # SAFE: no .rename(...)
        if not frames:
            return None
        daily = pd.concat(frames, axis=1).sort_index()
        daily.index.name = "Date"
        return daily
    except Exception as e:
        print(f"⚠️ yfinance failed: {e}")
        return None

def load_sample_or_generate():
    sample = os.path.join("data","sample","market_prices_sample.csv")
    if os.path.exists(sample):
        print(f"ℹ️ Using sample market file: {sample}")
        return pd.read_csv(sample, index_col=0, parse_dates=True).sort_index()
    idx = pd.date_range("2015-01-31","2025-12-31",freq="M")
    soxx = np.linspace(100,400,len(idx)) + np.random.normal(0,10,len(idx))
    qqq  = np.linspace( 90,380,len(idx)) + np.random.normal(0,10,len(idx))
    return pd.DataFrame({"SOXX":soxx,"QQQ":qqq}, index=idx)

def main():
    print("MARKER fetch_market.py v4 — pandas", pd.__version__)
    t0 = time.time()

    # 1) raw daily → save
    daily = download_live() or load_sample_or_generate()
    daily = daily.sort_index()
    raw_path = os.path.join(RAW_DIR,"market_prices.csv")
    daily.to_csv(raw_path)
    print(f"💾 raw → {raw_path}  rows={len(daily)}")

    # 2) resample to month-end closes, then 12-month change
    monthly = daily.resample("M").last()
    mon_12m = monthly.pct_change(12) * 100.0   # <-- monthly base, robust at tail

    # 3) rolling 10y percentiles (120 months)
    out = pd.DataFrame(index=mon_12m.index)
    if "SOXX" in mon_12m:
        out["MKT_SOXX_1y_pct"] = rolling_pct_rank(mon_12m["SOXX"], 120)
    if "QQQ" in mon_12m:
        out["MKT_QQQ_1y_pct"]  = rolling_pct_rank(mon_12m["QQQ"], 120)

    out = out.dropna(how="all")
    pro_path = os.path.join(PRO_DIR,"market_processed.csv")
    out.to_csv(pro_path)
    print(f"💾 processed → {pro_path}  rows={len(out)}  cols={list(out.columns)}")
    print(f"⏱  Done in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ fetch_market.py: {e}"); sys.exit(1)
