import os
import yaml
import pandas as pd
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
RAW = os.path.join(ROOT, "data", "raw")
PRO = os.path.join(ROOT, "data", "processed")
SAMPLE = os.path.join(ROOT, "data", "sample")

os.makedirs(PRO, exist_ok=True)

def percentile(series):
    return series.rank(pct=True) * 100

def inverted_percentile(series):
    return (1 - series.rank(pct=True)) * 100

def pct_yoy_percentile(series):
    yoy = series.pct_change(252) * 100
    return percentile(yoy)

def main():
    cfg = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "config.yaml")))
    weights = cfg["weights"]

    # Load market proxies if available; else sample
    if os.path.exists(os.path.join(RAW, "market_prices.csv")):
        mkt = pd.read_csv(os.path.join(RAW, "market_prices.csv"), index_col=0, parse_dates=True)
    else:
        mkt = pd.read_csv(os.path.join(SAMPLE, "market_prices_sample.csv"), index_col=0, parse_dates=True)

    # Compute percentiles for proxies
    ai_beta = pct_yoy_percentile(mkt["SOXX"].dropna())
    ev_sales_proxy = percentile(mkt["QQQ"].pct_change(252).dropna())

    # Credit (from FRED) or sample
    if os.path.exists(os.path.join(RAW, "credit_fred.csv")):
        cred = pd.read_csv(os.path.join(RAW, "credit_fred.csv"), index_col=0, parse_dates=True)
    else:
        cred = pd.read_csv(os.path.join(SAMPLE, "credit_fred_sample.csv"), index_col=0, parse_dates=True)

    hy = inverted_percentile(cred["HY_OAS"].dropna())
    ig = inverted_percentile(cred["IG_OAS"].dropna())

    # Assemble pillars (monthly)
    df = pd.concat([ai_beta, ev_sales_proxy, hy, ig], axis=1).dropna()
    df.columns = ["AI_Beta_Index", "EV_Sales_Proxy", "HY_OAS", "IG_OAS"]

    # Map indicators to pillars
    pillar_map = {
        "AI_Beta_Index": "Market",
        "EV_Sales_Proxy": "Market",
        "HY_OAS": "Credit",
        "IG_OAS": "Credit"
    }

    # Aggregate to pillar percentiles (mean)
    pillars = {}
    for col in df.columns:
        pillars.setdefault(pillar_map[col], []).append(df[col])
    pillar_df = pd.concat({k: pd.concat(v, axis=1).mean(axis=1) for k, v in pillars.items()}, axis=1)

    # Compute composite with weights
    w = pd.Series(weights)
    composite = (pillar_df * w).sum(axis=1)
    out = pillar_df.copy()
    out["AIBPS"] = composite

    out.to_csv(os.path.join(PRO, "aibps_monthly.csv"))
    print(f"Saved {out.shape} to data/processed/aibps_monthly.csv")

if __name__ == "__main__":
    main()
