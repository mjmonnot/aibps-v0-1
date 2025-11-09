# src/aibps/fetch_sentiment.py
# Sentiment / Valuation pillar (manual / curated):
# - Reads data/raw/sentiment_manual.csv
# - Aggregates to monthly
# - Computes rolling/expanding percentile (0–100)
# - Writes data/processed/sentiment_processed.csv with column "Sentiment"

import os, sys, time
import pandas as pd
import numpy as np

RAW = os.path.join("data", "raw", "sentiment_manual.csv")
OUT = os.path.join("data", "processed", "sentiment_processed.csv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)


def _expanding_pct(series: pd.Series) -> pd.Series:
    out = []
    vals = series.values
    for i in range(len(vals)):
        s = pd.Series(vals[: i + 1])
        out.append(float(s.rank(pct=True).iloc[-1] * 100.0))
    return pd.Series(out, index=series.index)


def rolling_pct_rank_flexible(series: pd.Series, window: int = 120) -> pd.Series:
    """
    For shorter histories: expanding percentile.
    For longer histories: rolling window percentile.
    """
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
    if not os.path.exists(RAW):
        print(f"ℹ️ {RAW} not found. Writing header only.")
        pd.DataFrame(columns=["Sentiment"]).to_csv(OUT)
        return

    try:
        # python engine is tolerant of commas in notes
        df = pd.read_csv(RAW, engine="python")
    except Exception as e:
        print(f"❌ Failed to read {RAW}: {e}")
        pd.DataFrame(columns=["Sentiment"]).to_csv(OUT)
        sys.exit(1)

    # Expect at least date + value
    if "date" not in df.columns or "value" not in df.columns:
        raise ValueError("sentiment_manual.csv must include 'date' and 'value' columns.")

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[~df["date"].isna()].copy()
    # Snap to month-end
    df["date"] = df["date"].dt.to_period("M").dt.to_timestamp("M")

    # Numeric value
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df[~df["value"].isna()].copy()

    if df.empty:
        print("ℹ️ sentiment_manual.csv produced no valid rows after cleaning.")
        pd.DataFrame(columns=["Sentiment"]).to_csv(OUT)
        return

    # Monthly aggregate (if you later split segments/metrics, they’ll sum here)
    monthly = df.groupby("date")["value"].sum().sort_index()

    # Percentile transform
    sent_pct = rolling_pct_rank_flexible(monthly, window=120)
    sent_pct.index.name = "date"

    out = pd.DataFrame({"Sentiment": sent_pct}).dropna(how="all")
    out.to_csv(OUT)

    print(f"💾 Wrote {OUT} ({len(out)} rows)")
    print("Tail:")
    print(out.tail(6))
    print(f"⏱  Done in {time.time() - t0:.2f}s")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ fetch_sentiment.py: {e}")
        sys.exit(1)
