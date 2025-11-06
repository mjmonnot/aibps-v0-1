import os
import pandas as pd
import yfinance as yf

RAW = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
os.makedirs(RAW, exist_ok=True)

TICKERS = ["SOXX", "QQQ"]  # proxies for AI beta / valuation
START = "2015-01-01"

def main():
    frames = []
    for t in TICKERS:
        df = yf.download(t, start=START, auto_adjust=True)["Close"].rename(t).to_frame()
        frames.append(df)
    out = pd.concat(frames, axis=1)
    out.to_csv(os.path.join(RAW, "market_prices.csv"))
    print(f"Saved {out.shape} to data/raw/market_prices.csv")

if __name__ == "__main__":
    main()
