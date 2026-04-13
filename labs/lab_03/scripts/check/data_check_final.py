from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR.parent.parent / "data" / "source"

PRICES_FILE = SOURCE_DIR / "portfolio_prices_raw_and_split_adjusted_20260331b.csv"
DIVIDENDS_FILE = SOURCE_DIR / "portfolio_dividends_20260331b.csv"
SPLITS_FILE = SOURCE_DIR / "portfolio_splits_true_splits_only_20260331b.csv"
OUTPUT_FILE = SOURCE_DIR / "data_issues.csv"

ORIG_DAILY = SOURCE_DIR / "sp100_daily_prices.csv"

PRICE_TOL = 1e-6
RETURN_TOL = 1e-3
EXPECTED_TRUE_SPLITS = {(pd.Timestamp("2025-11-17"), "NFLX", 10.0)}


def add_issue(issues: list[dict], issue_type: str, ticker=None, date=None, details: str = "") -> None:
    issues.append(
        {
            "Issue Type": issue_type,
            "Ticker": ticker,
            "Date": None if pd.isna(date) else pd.Timestamp(date).strftime("%Y-%m-%d"),
            "Details": details,
        }
    )


# --------------------------------------------------
# LOAD FILES
# --------------------------------------------------
prices = pd.read_csv(PRICES_FILE, parse_dates=["Date"])
divs = pd.read_csv(DIVIDENDS_FILE, parse_dates=["Date"])
splits = pd.read_csv(SPLITS_FILE, parse_dates=["Date"])
issues: list[dict] = []

orig = None
orig_pairs: set[tuple[str, pd.Timestamp]] = set()
orig_tickers: set[str] = set()

if ORIG_DAILY.exists():
    orig = pd.read_csv(ORIG_DAILY, parse_dates=["Date"])
    if {"Date", "Ticker", "Close", "Adj Close"}.issubset(orig.columns):
        orig = (
            orig[["Date", "Ticker", "Close", "Adj Close"]]
            .dropna(subset=["Date", "Ticker", "Close", "Adj Close"])
            .sort_values(["Ticker", "Date"])
            .reset_index(drop=True)
        )
        orig_pairs = set(zip(orig["Ticker"], orig["Date"]))
        orig_tickers = set(orig["Ticker"])


# --------------------------------------------------
# REQUIRED COLUMNS
# --------------------------------------------------
required_price_cols = {"Date", "Ticker", "raw_close", "adjusted_close"}
required_div_cols = {"Date", "Ticker", "Dividend"}
required_split_cols = {"Date", "Ticker", "Split Ratio"}

if set(prices.columns) != required_price_cols:
    add_issue(issues, "PRICE_COLUMNS", details=f"Expected {sorted(required_price_cols)}, found {list(prices.columns)}")
if set(divs.columns) != required_div_cols:
    add_issue(issues, "DIVIDEND_COLUMNS", details=f"Expected {sorted(required_div_cols)}, found {list(divs.columns)}")
if set(splits.columns) != required_split_cols:
    add_issue(issues, "SPLIT_COLUMNS", details=f"Expected {sorted(required_split_cols)}, found {list(splits.columns)}")

if (
    not required_price_cols.issubset(prices.columns)
    or not required_div_cols.issubset(divs.columns)
    or not required_split_cols.issubset(splits.columns)
):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(issues).to_csv(OUTPUT_FILE, index=False)
    raise SystemExit(1)


# --------------------------------------------------
# SORT
# --------------------------------------------------
prices = prices.sort_values(["Ticker", "Date"]).reset_index(drop=True)
divs = divs.sort_values(["Ticker", "Date"]).reset_index(drop=True)
splits = splits.sort_values(["Ticker", "Date"]).reset_index(drop=True)


# --------------------------------------------------
# DUPLICATE RECORD CHECKS
# --------------------------------------------------
for name, df in [
    ("PRICE_DUPLICATE", prices),
    ("DIVIDEND_DUPLICATE", divs),
    ("SPLIT_DUPLICATE", splits),
]:
    dupes = df[df.duplicated(subset=["Ticker", "Date"], keep=False)]
    for _, row in dupes.iterrows():
        add_issue(issues, name, row["Ticker"], row["Date"], "Duplicate (Ticker, Date) record")


# --------------------------------------------------
# BASIC VALUE CHECKS
# --------------------------------------------------
for _, row in prices.iterrows():
    if pd.isna(row["Ticker"]) or str(row["Ticker"]).strip() == "":
        add_issue(issues, "PRICE_BAD_TICKER", row["Ticker"], row["Date"], "Missing or blank ticker")
    if pd.isna(row["raw_close"]):
        add_issue(issues, "RAW_PRICE_MISSING", row["Ticker"], row["Date"], "raw_close is missing")
    elif row["raw_close"] <= 0:
        add_issue(issues, "RAW_PRICE_NONPOSITIVE", row["Ticker"], row["Date"], f"raw_close={row['raw_close']}")
    if pd.isna(row["adjusted_close"]):
        add_issue(issues, "ADJ_PRICE_MISSING", row["Ticker"], row["Date"], "adjusted_close is missing")
    elif row["adjusted_close"] <= 0:
        add_issue(issues, "ADJ_PRICE_NONPOSITIVE", row["Ticker"], row["Date"], f"adjusted_close={row['adjusted_close']}")
    elif row["raw_close"] + PRICE_TOL < row["adjusted_close"]:
        add_issue(
            issues,
            "RAW_LT_ADJ",
            row["Ticker"],
            row["Date"],
            f"raw_close={row['raw_close']}, adjusted_close={row['adjusted_close']}",
        )

for _, row in divs.iterrows():
    if pd.isna(row["Dividend"]):
        add_issue(issues, "DIVIDEND_MISSING", row["Ticker"], row["Date"], "Dividend is missing")
    elif row["Dividend"] < 0:
        add_issue(issues, "DIVIDEND_NEGATIVE", row["Ticker"], row["Date"], f"Dividend={row['Dividend']}")

for _, row in splits.iterrows():
    if pd.isna(row["Split Ratio"]):
        add_issue(issues, "SPLIT_MISSING", row["Ticker"], row["Date"], "Split Ratio is missing")
    elif row["Split Ratio"] <= 0:
        add_issue(issues, "SPLIT_NONPOSITIVE", row["Ticker"], row["Date"], f"Split Ratio={row['Split Ratio']}")


# --------------------------------------------------
# VALIDITY UNIVERSE CHECK
# Original Yahoo price file defines valid (Ticker, Date) pairs.
# --------------------------------------------------
price_pairs = set(zip(prices["Ticker"], prices["Date"]))
price_tickers = set(prices["Ticker"])

if orig is not None:
    # rebuilt prices should match original valid pairs exactly
    for ticker, date in sorted(orig_pairs - price_pairs):
        add_issue(
            issues,
            "MISSING_PRICE_ROW",
            ticker,
            date,
            "Valid in original Yahoo price file but missing from rebuilt prices file",
        )

    for ticker, date in sorted(price_pairs - orig_pairs):
        add_issue(
            issues,
            "EXTRA_PRICE_ROW",
            ticker,
            date,
            "Present in rebuilt prices file but not valid in original Yahoo price file",
        )

    # dividends and splits must occur only on valid original price dates
    for _, row in divs.iterrows():
        if row["Ticker"] not in orig_tickers:
            add_issue(issues, "DIVIDEND_UNKNOWN_TICKER", row["Ticker"], row["Date"], "Ticker not found in original Yahoo prices")
        elif (row["Ticker"], row["Date"]) not in orig_pairs:
            add_issue(issues, "DIVIDEND_DATE_NOT_VALID", row["Ticker"], row["Date"], "Dividend date not valid for this ticker in original Yahoo prices")

    for _, row in splits.iterrows():
        if row["Ticker"] not in orig_tickers:
            add_issue(issues, "SPLIT_UNKNOWN_TICKER", row["Ticker"], row["Date"], "Ticker not found in original Yahoo prices")
        elif (row["Ticker"], row["Date"]) not in orig_pairs:
            add_issue(issues, "SPLIT_DATE_NOT_VALID", row["Ticker"], row["Date"], "Split date not valid for this ticker in original Yahoo prices")
else:
    # fallback if original file is unavailable
    for _, row in divs.iterrows():
        if row["Ticker"] not in price_tickers:
            add_issue(issues, "DIVIDEND_UNKNOWN_TICKER", row["Ticker"], row["Date"], "Ticker not found in prices file")
        elif (row["Ticker"], row["Date"]) not in price_pairs:
            add_issue(issues, "DIVIDEND_DATE_NOT_IN_PRICES", row["Ticker"], row["Date"], "Dividend date missing from prices file")

    for _, row in splits.iterrows():
        if row["Ticker"] not in price_tickers:
            add_issue(issues, "SPLIT_UNKNOWN_TICKER", row["Ticker"], row["Date"], "Ticker not found in prices file")
        elif (row["Ticker"], row["Date"]) not in price_pairs:
            add_issue(issues, "SPLIT_DATE_NOT_IN_PRICES", row["Ticker"], row["Date"], "Split date missing from prices file")


# --------------------------------------------------
# DATASET-SPECIFIC TRUE SPLIT EXPECTATION
# --------------------------------------------------
actual_splits = {(row["Date"], row["Ticker"], float(row["Split Ratio"])) for _, row in splits.iterrows()}
for date, ticker, ratio in actual_splits - EXPECTED_TRUE_SPLITS:
    add_issue(issues, "UNEXPECTED_SPLIT_RECORD", ticker, date, f"Unexpected split ratio {ratio}")
for date, ticker, ratio in EXPECTED_TRUE_SPLITS - actual_splits:
    add_issue(issues, "MISSING_EXPECTED_SPLIT", ticker, date, f"Expected split ratio {ratio}")


# --------------------------------------------------
# SPLIT-ONLY ADJUSTED-CLOSE LEVEL CHECK
# adjusted_close should equal raw_close divided by product of future true splits
# --------------------------------------------------
price_with_splits = prices.merge(splits, on=["Ticker", "Date"], how="left")
price_with_splits["Split Ratio"] = price_with_splits["Split Ratio"].fillna(1.0)

pieces = []
for ticker, g in price_with_splits.groupby("Ticker", sort=False):
    g = g.sort_values("Date").copy()
    future_factor = np.ones(len(g), dtype=float)
    running = 1.0
    for i in range(len(g) - 1, -1, -1):
        future_factor[i] = running
        running *= float(g.iloc[i]["Split Ratio"])
    g["future_split_factor"] = future_factor
    g["expected_adjusted_close"] = g["raw_close"] / g["future_split_factor"]
    pieces.append(g)

level_check = pd.concat(pieces, ignore_index=True)
level_check["level_diff"] = (level_check["adjusted_close"] - level_check["expected_adjusted_close"]).abs()
bad_level = level_check[level_check["raw_close"].notna() & (level_check["level_diff"] > PRICE_TOL)]

for _, row in bad_level.iterrows():
    add_issue(
        issues,
        "ADJ_CLOSE_LEVEL_MISMATCH",
        row["Ticker"],
        row["Date"],
        (
            f"adjusted_close={row['adjusted_close']:.6f}, "
            f"expected={row['expected_adjusted_close']:.6f}, "
            f"future_split_factor={row['future_split_factor']:.6f}"
        ),
    )


# --------------------------------------------------
# TOTAL RETURN RECONCILIATION CHECK
# Original Yahoo Adj Close defines total return.
# Rebuilt file should match it using:
#   (adjusted_close_t + dividend_t) / adjusted_close_{t-1}
# --------------------------------------------------
if orig is not None:
    recon = prices.merge(divs, on=["Ticker", "Date"], how="left")
    recon = recon.merge(orig, on=["Ticker", "Date"], how="inner")
    recon["Dividend"] = recon["Dividend"].fillna(0.0)
    recon = recon.sort_values(["Ticker", "Date"]).copy()

    recon["prev_new_adj"] = recon.groupby("Ticker")["adjusted_close"].shift(1)
    recon["prev_orig_adj"] = recon.groupby("Ticker")["Adj Close"].shift(1)

    valid = (
        recon["prev_new_adj"].notna()
        & recon["prev_orig_adj"].notna()
        & (recon["prev_new_adj"] != 0)
        & (recon["prev_orig_adj"] != 0)
    )

    recon["orig_total_return"] = np.nan
    recon["reconstructed_total_return"] = np.nan

    recon.loc[valid, "orig_total_return"] = recon.loc[valid, "Adj Close"] / recon.loc[valid, "prev_orig_adj"]
    recon.loc[valid, "reconstructed_total_return"] = (
        recon.loc[valid, "adjusted_close"] + recon.loc[valid, "Dividend"]
    ) / recon.loc[valid, "prev_new_adj"]

    recon["return_diff"] = (recon["orig_total_return"] - recon["reconstructed_total_return"]).abs()

    bad_ret = recon[valid & (recon["return_diff"] > RETURN_TOL)]
    for _, row in bad_ret.iterrows():
        add_issue(
            issues,
            "TOTAL_RETURN_RECON_MISMATCH",
            row["Ticker"],
            row["Date"],
            (
                f"orig_total_return={row['orig_total_return']:.6f}, "
                f"reconstructed_total_return={row['reconstructed_total_return']:.6f}, "
                f"dividend={row['Dividend']:.6f}"
            ),
        )


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------
issues_df = pd.DataFrame(issues)
if issues_df.empty:
    issues_df = pd.DataFrame(columns=["Issue Type", "Ticker", "Date", "Details"])

issues_df = issues_df.sort_values(["Issue Type", "Ticker", "Date"], na_position="last").reset_index(drop=True)
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
issues_df.to_csv(OUTPUT_FILE, index=False)

print(f"Wrote {len(issues_df)} issues to {OUTPUT_FILE}")
if len(issues_df) == 0:
    print("No issues found.")