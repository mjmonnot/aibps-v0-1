# src/aibps/fetch_capex_macro.py
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path("data")
PROC_OUT = DATA_DIR / "processed" / "macro_capex_processed.csv"
START = "1980-01-01"  # or "1947-01-01" if you want the full PNFI span

PNFI = "PNFI"     # Private Nonresidential Fixed Investment (Q, SAAR, $) [FRED]
UNXANO = "UNXANO" # New Orders: Nondefense Cap Goods ex-Aircraft (M, $)  [FRED]

def _as_monthly(s: pd.Series) -> pd.Series:
    s = s.sort_index()
    s.index = pd.to_datetime(s.index)
    s.index.name = "date"
    return s.resample("M").last()

def _rebase_100(s: pd.Series) -> pd.Series:
    s = s.copy()
    first = s.dropna().iloc[0] if s.notna().any() else np.nan
    if pd.notna(first) and first != 0:
        s = (s / first) * 100.0
    else:
        s[:] = np.nan
    return s

def main():
    key = os.getenv("FRED_API_KEY")
    if not key:
        print("⚠️ No FRED_API_KEY — cannot fetch PNFI/UNXANO.")
        return

    from fredapi import Fred
    fred = Fred(api_key=key)

    def get(sid):
        s = fred.get_series(sid, observation_start=START)
        s = pd.Series(s, name=sid).sort_index()
        s.index = pd.to_datetime(s.index)
        s.index.name = "date"
        return s

    # Fetch
    pnfi_q = get(PNFI)     # quarterly
    unx_m = get(UNXANO)    # monthly

    # Convert PNFI to monthly by taking quarter-end and forward-filling within quarter
    pnfi_m = pnfi_q.resample("Q").last().resample("M").ffill()
    pnfi_m.name = "PNFI_m"

    # Align both to monthly
    unx_m = _as_monthly(unx_m).rename("UNXANO_m")

    # Rebase each to 100 at first valid point
    pnfi_idx = _rebase_100(pnfi_m)
    unx_idx = _rebase_100(unx_m)

    # Equal-weight composite (only where available)
    df = pd.concat([pnfi_idx, unx_idx], axis=1)
    capex_macro = df.mean(axis=1, skipna=True).rename("Capex_Supply_Macro")

    out = pd.DataFrame({"Capex_Supply_Macro": capex_macro}).dropna(how="all")
    out.index.name = "date"

    PROC_OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(PROC_OUT)
    print("---- capex_macro tail ----")
    print(out.tail(6))
    print(f"💾 Wrote {PROC_OUT} (rows={len(out)}) span: {out.index.min().date()} → {out.index.max().date()}")

if __name__ == "__main__":
    main()
