import os
import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv

RAW = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
os.makedirs(RAW, exist_ok=True)

SERIES = {
    "HY_OAS": "BAMLH0A0HYM2",
    "IG_OAS": "BAMLCC0A0CM",
}

def main():
    load_dotenv()
    key = os.getenv("FRED_API_KEY")
    if not key:
        print("Warning: FRED_API_KEY not set; skipping fetch. Use sample data instead.")
        return
    fred = Fred(api_key=key)
    frames = []
    for name, code in SERIES.items():
        s = fred.get_series(code).rename(name).to_frame()
        frames.append(s)
    out = pd.concat(frames, axis=1)
    out.to_csv(os.path.join(RAW, "credit_fred.csv"))
    print(f"Saved {out.shape} to data/raw/credit_fred.csv")

if __name__ == "__main__":
    main()
