#!/usr/bin/env python3
"""
fetch_sentiment.py

Builds a multi-component Sentiment pillar for AIBPS from real FRED series:

Sub-pillars:
    - Sentiment_Consumer : UMCSENT
        * University of Michigan: Consumer Sentiment Index

    - Sentiment_EPU      : USEPUINDXM
        * Economic Policy Uncertainty Index for United States (news-based)

    - Sentiment_VIX      : VIXCLS
        * CBOE Volatility Index (VIX) – daily; resampled to month-end

We:
    * Fetch raw series from FRED
    * Resample all to month-end, forward-fill
    * Trim to START_DATE
    * Standardize each sub-pillar via z-score
    * Build Sentiment = mean of available standardized sub-pillars

Output:
    data/processed/sentiment_processed.csv with columns:
        - Sentiment_Consumer
        - Sentiment_EPU
        - Sentiment_VIX
        - Sentiment   (composite, based on z-mean)
"""

import os
import sys
import pandas as pd

try:
    from fredapi import Fred
except ImportError:
    Fred = None

START_DATE = "1980-01-31"
OUT_PATH = "data/processed/sentiment_processed.csv"

# FRED IDs
CONSUMER_ID = "UMCSENT"
EPU_ID      = "USEPUINDXM"
VIX_ID      = "VIXCLS"


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def get_fred_client():
    """Instantiate a Fred client from FRED_API_KEY, or return None if unavailable."""
    if Fred is None:
        print("❌ fredapi is not installed. Install it in your environment.")
        return None

    key = os.getenv("FRED_API_KEY")
    if not key:
        print("⚠️ FRED_API_KEY not set; cannot fetch Sentiment data from FRED.")
        return None

    try:
        return Fred(api_key=key)
    except Exception as e:
        print(f"❌ Failed to initialize Fred client: {e}")
        return None


def fetch_series(fred, sid, colname, label):
    """
    Fetch a single FRED series and return as a one-column DataFrame with Date index.
    """
    try:
        ser = fred.get_series(sid)
        if ser is None or len(ser) == 0:
            print(f"⚠️ {label}: empty or missing series {sid}; skipping.")
            return pd.DataFrame()

        s = pd.Series(ser, name=colname)
        s.index = pd.to_datetime(s.index)
        s = s.sort_index()
        print(
            f"✅ {label}: fetched {sid} → {colname} "
            f"({s.index.min().date()} → {s.index.max().date()}, n={len(s)})"
        )
        return s.to_frame()
    except Exception as e:
        print(f"⚠️ {label}: failed fetching {sid}: {e}")
        return pd.DataFrame()


def reindex_monthly(df, start_date):
    """
    Resample to month-end ("ME"), forward-fill, and trim to dates >= start_date.
    Ensures DatetimeIndex before resampling.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()].sort_index()
    if df.empty:
        return pd.DataFrame()

    monthly = df.resample("ME").last().ffill()

    start_ts = pd.to_datetime(start_date)
    monthly = monthly[monthly.index >= start_ts]
    monthly.index.name = "Date"
    return monthly


def z_standardize(series: pd.Series) -> pd.Series:
    """
    Simple z-score standardization: (x - mean) / std.
    Returns NaNs if std == 0 or series empty.
    """
    if series is None or series.empty:
        return series

    m = series.mean()
    s = series.std()
    if s == 0 or pd.isna(s):
        return pd.Series(index=series.index, data=float("nan"), name=series.name)

    z = (series - m) / s
    z.name = series.name
    return z


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():
    fred = get_fred_client()
    if fred is None:
        # Write an empty shell file so downstream steps don't blow up.
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        empty_cols = ["Sentiment_Consumer", "Sentiment_EPU", "Sentiment_VIX", "Sentiment"]
        pd.DataFrame(columns=empty_cols).to_csv(OUT_PATH, index_label="Date")
        print(f"💾 Wrote empty {OUT_PATH} (no FRED client).")
        return 0

    # --- Fetch individual series ---
    cons_df = fetch_series(fred, CONSUMER_ID, "Sentiment_Consumer", "ConsumerSentiment")
    epu_df  = fetch_series(fred, EPU_ID,      "Sentiment_EPU",      "EconomicPolicyUncertainty")
    vix_df  = fetch_series(fred, VIX_ID,      "Sentiment_VIX",      "VIX")

    # Combine and resample
    combined = pd.concat([cons_df, epu_df, vix_df], axis=1).sort_index()

    if combined.empty:
        print("⚠️ All Sentiment sub-series empty; writing empty sentiment_processed.csv.")
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        empty_cols = ["Sentiment_Consumer", "Sentiment_EPU", "Sentiment_VIX", "Sentiment"]
        pd.DataFrame(columns=empty_cols).to_csv(OUT_PATH, index_label="Date")
        print(f"💾 Wrote empty {OUT_PATH}")
        return 0

    monthly = reindex_monthly(combined, START_DATE)

    # Z-standardize each component before building composite
    z_cols = {}
    for cname in ["Sentiment_Consumer", "Sentiment_EPU", "Sentiment_VIX"]:
        if cname in monthly.columns:
            z_cols[cname] = z_standardize(monthly[cname])

    if z_cols:
        z_df = pd.concat(z_cols.values(), axis=1)
        # Composite = mean of available z-scores
        monthly["Sentiment"] = z_df.mean(axis=1)
        print(f"✅ Sentiment composite constructed from z-scored components: {list(z_cols.keys())}")
    else:
        monthly["Sentiment"] = float("nan")
        print("⚠️ No Sentiment components available; Sentiment is NaN.")

    # Tail debug
    print("---- Tail of sentiment_processed.csv ----")
    print(monthly.tail(12))

    # Write output
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    monthly.to_csv(OUT_PATH, index_label="Date")
    print(
        f"💾 Wrote {OUT_PATH} with {len(monthly)} rows and columns: "
        f"{list(monthly.columns)}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
