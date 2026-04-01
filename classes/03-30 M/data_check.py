import pandas as pd
import numpy as np
from pathlib import Path

import os

# Get the current working directory as a string
print(os.getcwd())

BASE_DIR = Path(__file__).parent

PRICES_FILE = BASE_DIR / "sp100_daily_prices.csv"
DIVIDENDS_FILE = BASE_DIR / "sp100_dividends.csv"
SPLITS_FILE = BASE_DIR / "sp100_splits.csv"

TOL = 1e-3

prices = pd.read_csv(PRICES_FILE, parse_dates=["Date"]).sort_values(["Ticker", "Date"])
divs = pd.read_csv(DIVIDENDS_FILE, parse_dates=["Date"]).sort_values(["Ticker", "Date"])
splits = pd.read_csv(SPLITS_FILE, parse_dates=["Date"]).sort_values(["Ticker", "Date"])

issues = []

# --------------------------------------------------
# 1) DUPLICATE RECORD CHECKS
# --------------------------------------------------
for name, df in [
    ("PRICE_DUPLICATE", prices),
    ("DIVIDEND_DUPLICATE", divs),
    ("SPLIT_DUPLICATE", splits),
]:
    dup = df.duplicated(subset=["Ticker", "Date"], keep=False)
    if dup.any():
        temp = df.loc[dup, ["Ticker", "Date"]].copy()
        temp["Issue"] = name
        issues.append(temp)

# --------------------------------------------------
# 2) RETURN CONSISTENCY CHECK
# --------------------------------------------------
df = (
    prices
    .merge(divs, on=["Ticker", "Date"], how="left")
    .merge(splits, on=["Ticker", "Date"], how="left")
)

df["Dividend"] = df["Dividend"].fillna(0.0)
df["Split Ratio"] = df["Split Ratio"].fillna(1.0)

df["Prev Close"] = df.groupby("Ticker")["Close"].shift(1)
df["Prev Adj Close"] = df.groupby("Ticker")["Adj Close"].shift(1)

valid = (
    df["Prev Close"].notna()
    & df["Prev Adj Close"].notna()
    & (df["Prev Close"] != 0)
    & (df["Prev Adj Close"] != 0)
)

df["Observed"] = np.nan
df["Expected"] = np.nan
df["Abs Error"] = np.nan

df.loc[valid, "Observed"] = df.loc[valid, "Adj Close"] / df.loc[valid, "Prev Adj Close"]
df.loc[valid, "Expected"] = (df.loc[valid, "Close"] + df.loc[valid, "Dividend"]) / df.loc[valid, "Prev Close"]
df.loc[valid, "Abs Error"] = (df.loc[valid, "Observed"] - df.loc[valid, "Expected"]).abs()

bad = df.loc[valid & (df["Abs Error"] > TOL), ["Ticker", "Date", "Abs Error"]].copy()
bad["Issue"] = "RETURN_MISMATCH"
issues.append(bad[["Ticker", "Date", "Issue"]])

# --------------------------------------------------
# 3) FINAL OUTPUT
# --------------------------------------------------
if issues:
    flagged = (
        pd.concat(issues, ignore_index=True)
        .drop_duplicates()
        .sort_values(["Issue", "Ticker", "Date"])
    )
else:
    flagged = pd.DataFrame(columns=["Ticker", "Date", "Issue"])

flagged.to_csv(BASE_DIR / "data_issues.csv", index=False)
print(flagged.to_string(index=False))
print(f"\nRows flagged: {len(flagged)}")