#!/usr/bin/env python3
"""
fetch_adoption.py
Builds a multi-component Adoption pillar from real FRED macro series.

Sub-pillars:
    - Adoption_Enterprise_Software
    - Adoption_Cloud_Services
    - Adoption_Digital_Labor
    - Adoption_Connectivity

Output:
    data/processed/adoption_processed.csv
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Allow importing fredapi when running in GitHub Actions
try:
    from fredapi import Fred
except ImportError:
    Fred = None

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

START_DATE = "1980-01-31"
OUT_PATH = "data/processed/adoption_processed.csv"

ENTERPRISE_SERIES = [
    # Enterprise software / IP investment
    ("B985RC1A027NBEA", "Enterprise_Software"),
]

CLOUD_SERIES = [
    # Equipment, hosting, and data-processing proxies
    ("TLHICS",  "Cloud_IT_Comp_Equip"),          # Computers/peripherals investment
    ("AIPDC",   "Cloud_DataProcessing_Equip"),   # Private fixed investment in data-processing
    ("IPB541",  "Cloud_Hosting_Production"),     # Industrial Production: Data Processing & Hosting
]

DIGITAL_LABOR_SERIES = [
    ("PRS85006092",  "Labor_Productivity"),      # Nonfinancial corporate output per hour
    ("ULCBS",        "Unit_Labor_Costs"),        # ULC Business sector
    ("IPN11110",     "Comp_Electronics_Prod"),   # Industrial Prod: Computing & Electronics
]

CONNECTIVITY_SERIES = [
    ("IPN323",         "Comm_Equipment_Prod"),    # Industrial Prod: Communications equipment
    ("IPN2211",        "Electric_Power_Equip"),   # Electric power equipment & distribution
    ("CES1020000001",  "Telecom_Employment"),     # Telecommunications employment
]


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def fetch_series_list(fred, pairs, label):
    """
    Fetch several FRED series and return a DataFrame with columns.
    Each series is one column. Returns empty DataFrame if all fail.
    """
    frames = []

    for sid, colname in pairs:
        try:
            ser = fred.get_series(sid)
            if ser is None or len(ser) == 0:
                print(f"⚠️ Empty or missing series {sid} ({colname}) for {label}")
                continue
            s = pd.Series(ser, name=colname)
            s.index = pd.to_datetime(s.index)
            frames.append(s)
        except Exception as e:
            print(f"⚠️ Failed fetching {sid} ({colname}) for {label}: {e}")

    if not frames:
        print(f"⚠️ No data for block {label}")
        return pd.DataFrame()

    df = pd.concat(frames, axis=1).sort_index()
    print(f"✅ Built block for {label} with columns: {list(df.columns)}")
    return df


def block_to_single_index(df_block, name):
    """
    Build a single composite index per block by taking the row-wise mean
    across all available subseries for that block.
    """
    if df_block.empty:
        return pd.Series(dtype=float)

    ser = df_block.mean(axis=1)
    ser.name = name
    return ser


# ---------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------

def main():
    if Fred is None:
        print("❌ fredapi is not installed. Install it or verify environment.")
        return

    key = os.getenv("FRED_API_KEY")
    if not key:
        print("⚠️ No FRED_API_KEY in environment. Exiting.")
        return

    fred = Fred(api_key=key)

    # --------------------------------------------------------------
    # Sub-blocks
    # --------------------------------------------------------------

    enterprise_block = fetch_series_list(fred, ENTERPRISE_SERIES, "Enterprise_Software")
    cloud_block      = fetch_series_list(fred, CLOUD_SERIES,      "Cloud_Services")
    labor_block      = fetch_series_list(fred, DIGITAL_LABOR_SERIES, "Digital_Labor")
    conn_block       = fetch_series_list(fred, CONNECTIVITY_SERIES,  "Connectivity")

    # Composite indices
    ent_idx   = block_to_single_index(enterprise_block, "Adoption_Enterprise_Software")
    cloud_idx = block_to_single_index(cloud_block,      "Adoption_Cloud_Services")
    labor_idx = block_to_single_index(labor_block,      "Adoption_Digital_Labor")
    conn_idx  = block_to_single_index(conn_block,       "Adoption_Connectivity")

    # --------------------------------------------------------------
    # Combine into a unified DataFrame
    # --------------------------------------------------------------

    df = pd.concat([ent_idx, cloud_idx, labor_idx, conn_idx], axis=1)
    df = df.sort_index()

    # Expand to monthly from 1980 to latest available
    all_months = pd.date_range(START_DATE, df.index.max(), freq="M")
    df = df.reindex(all_months)
    df.index.name = "Date"

    # Forward-fill
    df = df.ffill()

    # Composite Adoption index
    component_cols = [
        c for c in [
            "Adoption_Enterprise_Software",
            "Adoption_Cloud_Services",
            "Adoption_Digital_Labor",
            "Adoption_Connectivity",
        ]
        if c in df.columns
    ]

    if component_cols:
        df["Adoption_Supply"] = df[component_cols].mean(axis=1)
        df["Adoption"]        = df["Adoption_Supply"]
        print(f"✅ Constructed Adoption using components: {component_cols}")
    else:
        df["Adoption"] = float("nan")
        print("⚠️ No Adoption components available — Adoption is empty.")

    # --------------------------------------------------------------
    # Write output
    # --------------------------------------------------------------

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df.to_csv(OUT_PATH, index=True)
    print(f"💾 Wrote {OUT_PATH} with {len(df)} rows and columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
