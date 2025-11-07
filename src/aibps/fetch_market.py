# src/aibps/fetch_market.py
"""
Fetches market proxies via yfinance with safe naming (no .rename(...)).
Writes:
  - data/raw/market_prices.csv
  - data/processed/market_processed.csv (monthly 1y-return percentiles)
"""
import os, sys, time
import pandas as pd
import numpy as np

RAW_DIR = os.path.join("data", "raw")
PRO_DIR = os.path.join("data", "processed")
SAMPLE_FILE = os.path.join("data", "sample", "market_prices_sample.csv")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PRO_DIR, exist_ok=True)

START = "2015-01-01"
TICKERS = ["SOXX", "QQQ"]

def download_live(start=START):
    try:
        import yfinance as yf
        frames = []
        for t in TICKERS:
            df = yf.download(t, start=start, auto_adjust=True, progress=False)
            if df is None or df.empty or "Close" not in df:
                print(f"⚠️ yfinance returned empty for {t}; skipping.")
                continue
            # SAFE naming: never use .rename(<str>) on Series/DataFrame
            s = df["Close"]
            s.index = pd.to_datetime(s.index)
            s.index.name = "Date"
            frames.append(s.to_frame(name=t))  # <- this is the safe way
        if not frames:
            return None
        out = pd.concat(frames, axis=1)
        out.index.name = "Date"
        return out
    except Exception as e:
        print(f"⚠️ yfinance fetch failed: {e}")
        return None

def load_sample_or_generate():
    if os.path.exists(SAMPLE_FILE):
        print(f"ℹ️ Using sample market file: {SAMPLE_FILE}")
        return pd.read_csv(SAMPLE_FILE, index_col=0, parse_dates=True)
    print("ℹ️ No sample file. Generating synthetic series.")
    idx = pd.date_range("2015-01-31", "2025-12-31", freq="M")
    soxx = np.linspace(100, 400, len(idx)) + np.random.normal(0, 10, len(idx))
    qqq  = np.linspace( 90, 380, len(idx)) + np.random.normal(0, 10, len(idx))
    df = pd.DataFrame({"SOXX": soxx, "QQQ": qqq}, index=idx)
    df.index.name = "Date"
    return df

def pct_rank(s, invert=False):
    r = s.rank(pct=True) * 100
    return 100 - r if invert else r

def main():
    print("fetch_market.py loaded — safe naming (no .rename). pandas:", pd.__version__)
    t0 = time.time()

    market_df = download_live()
    if market_df is None or market_df.empty:
        market_df = load_sample_or_generate()

    raw_path = os.path.join(RAW_DIR, "market_prices.csv")
    market_df.to_csv(raw_path)
    print(f"💾 Saved raw market data → {raw_path}")

    # Compute 1Y returns on daily data, then resample to month-end for stability
    daily = market_df.copy()
    one_year = daily.pct_change(252) * 100
    ret_m = one_year.resample("M").last()

    out = pd.DataFrame({
        "MKT_SOXX_1y_pct": pct_rank(ret_m["SOXX"]),
        "MKT_QQQ_1y_pct":  pct_rank(ret_m["QQQ"]),
    }).dropna()

    pro_path = os.path.join(PRO_DIR, "market_processed.csv")
    out.to_csv(pro_path)
    print(f"💾 Saved processed market data → {pro_path}")
    print(f"⏱ Done in {time.time()-t0:.1f}s")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ fetch_market.py failed: {e}")
        sys.exit(1)
