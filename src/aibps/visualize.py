import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
PRO = os.path.join(ROOT, "data", "processed")

def radar(ax, values, labels):
    N = len(values)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    values = list(values) + values[:1]
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticks([20, 40, 60, 80, 100])

def main():
    df = pd.read_csv(os.path.join(PRO, "aibps_monthly.csv"), index_col=0, parse_dates=True)
    latest = df.iloc[-1]
    pillars = ["Market", "Capex_Supply", "Infra", "Adoption", "Credit"]
    # Fill missing pillars with NaN-safe zeros for demo
    for p in pillars:
        if p not in df.columns:
            df[p] = np.nan
    df.fillna(method="ffill", inplace=True)

    # Radar (latest)
    fig = plt.figure(figsize=(6,6))
    ax = plt.subplot(111, polar=True)
    radar(ax, [latest.get(p, np.nan) for p in pillars], pillars)
    ax.set_title("AIBPS Radar — Latest")
    fig.savefig(os.path.join(PRO, "radar_latest.png"), dpi=160)

    # Time series
    plt.figure(figsize=(9,4.5))
    df["AIBPS"].rolling(3).mean().plot()
    plt.axhline(50, linestyle="--", linewidth=1)
    plt.axhline(70, linestyle="--", linewidth=1)
    plt.axhline(85, linestyle="--", linewidth=1)
    plt.title("AIBPS — 3M Rolling Average")
    plt.ylabel("Score (0–100)")
    plt.tight_layout()
    plt.savefig(os.path.join(PRO, "aibps_timeseries.png"), dpi=160)

if __name__ == "__main__":
    main()
