"""
Download daily prices, dividends, and stock splits for the current S&P 100
using yfinance, then save them to separate CSV files.

Files written:
    sp100_tickers.csv
    sp100_daily_prices.csv
    sp100_dividends.csv
    sp100_splits.csv

Notes:
- The S&P 100 currently has 101 constituents because both GOOG and GOOGL are included.
- Yahoo Finance uses BRK-B instead of BRK.B.
- This script uses Wikipedia to fetch the current constituent list.
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import yfinance as yf


OUTPUT_DIR = Path("sp100_data")
OUTPUT_DIR.mkdir(exist_ok=True)

START_DATE = "2025-01-01"
END_DATE = None          # None means "through today"
PAUSE_BETWEEN_TICKERS = 0.2


def get_sp100_tickers():
    """
    Return a Yahoo-compatible list of S&P 100 tickers.
    """
    return [
        "AAPL", "ABBV", "ABT", "ACN", "ADBE", "AIG", "AMD", "AMGN", "AMT", "AMZN",
        "AVGO", "AXP", "BA", "BAC", "BK", "BKNG", "BLK", "BMY", "BRK-B", "C",
        "CAT", "CHTR", "CL", "CMCSA", "COF", "COP", "COST", "CRM", "CSCO", "CVS",
        "CVX", "DE", "DHR", "DIS", "DUK", "EMR", "F", "FDX", "GD", "GE",
        "GILD", "GM", "GOOG", "GOOGL", "GS", "HD", "HON", "IBM", "INTC", "JNJ",
        "JPM", "KMI", "KO", "LIN", "LLY", "LMT", "LOW", "MA", "MCD", "MDLZ",
        "MDT", "MET", "META", "MMM", "MO", "MRK", "MS", "MSFT", "NEE", "NFLX",
        "NKE", "NVDA", "ORCL", "PEP", "PFE", "PG", "PM", "PYPL", "QCOM", "RTX",
        "SBUX", "SCHW", "SO", "SPG", "T", "TGT", "TMO", "TMUS", "TSLA", "TXN",
        "UNH", "UNP", "UPS", "USB", "V", "VZ", "WFC", "WMT", "XOM"
    ]


def download_daily_prices(tickers: list[str], start: str, end: str | None) -> pd.DataFrame:
    """
    Bulk-download daily OHLCV and Adj Close for all tickers.
    Returns a long-form DataFrame:
        Date, Ticker, Open, High, Low, Close, Adj Close, Volume
    """
    raw = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,
        actions=False,
        group_by="ticker",
        progress=True,
        threads=True,
    )

    if raw.empty:
        raise ValueError("No price data returned.")

    frames = []

    # MultiIndex columns expected for multiple tickers
    if isinstance(raw.columns, pd.MultiIndex):
        for ticker in tickers:
            if ticker not in raw.columns.get_level_values(0):
                continue

            df_t = raw[ticker].copy()
            if df_t.empty:
                continue

            df_t = df_t.reset_index()
            df_t["Ticker"] = ticker
            frames.append(df_t)
    else:
        # Single ticker fallback
        df_t = raw.reset_index()
        df_t["Ticker"] = tickers[0]
        frames.append(df_t)

    prices = pd.concat(frames, ignore_index=True)

    # Standardize column names
    rename_map = {
        "Date": "Date",
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Adj Close": "Adj Close",
        "Volume": "Volume",
    }
    prices = prices.rename(columns=rename_map)

    # Reorder
    wanted = ["Date", "Ticker", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    prices = prices[[c for c in wanted if c in prices.columns]]

    # Normalize date type
    prices["Date"] = pd.to_datetime(prices["Date"]).dt.date

    return prices.sort_values(["Ticker", "Date"]).reset_index(drop=True)


def download_actions(
    tickers: list[str],
    start: str,
    end: str | None,
    pause: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Download dividends and stock splits ticker-by-ticker.
    Returns:
        dividends_df: Date, Ticker, Dividend
        splits_df: Date, Ticker, Stock Split
    """
    dividend_rows = []
    split_rows = []

    for i, ticker in enumerate(tickers, start=1):
        print(f"[{i}/{len(tickers)}] Downloading actions for {ticker}...")

        try:
            hist = yf.Ticker(ticker).history(
                start=start,
                end=end,
                interval="1d",
                auto_adjust=False,
                actions=True,
            )
        except Exception as exc:
            print(f"  Skipping {ticker}: {exc}")
            time.sleep(pause)
            continue

        if hist.empty:
            time.sleep(pause)
            continue

        hist = hist.reset_index()

        if "Dividends" in hist.columns:
            divs = hist.loc[hist["Dividends"].fillna(0) != 0, ["Date", "Dividends"]].copy()
            if not divs.empty:
                divs["Ticker"] = ticker
                divs["Date"] = pd.to_datetime(divs["Date"]).dt.date
                dividend_rows.append(divs)

        if "Stock Splits" in hist.columns:
            splits = hist.loc[hist["Stock Splits"].fillna(0) != 0, ["Date", "Stock Splits"]].copy()
            if not splits.empty:
                splits["Ticker"] = ticker
                splits["Date"] = pd.to_datetime(splits["Date"]).dt.date
                split_rows.append(splits)

        time.sleep(pause)

    dividends_df = (
        pd.concat(dividend_rows, ignore_index=True)
        .rename(columns={"Dividends": "Dividend"})
        .sort_values(["Ticker", "Date"])
        .reset_index(drop=True)
        if dividend_rows
        else pd.DataFrame(columns=["Date", "Ticker", "Dividend"])
    )

    splits_df = (
        pd.concat(split_rows, ignore_index=True)
        .rename(columns={"Stock Splits": "Split Ratio"})
        .sort_values(["Ticker", "Date"])
        .reset_index(drop=True)
        if split_rows
        else pd.DataFrame(columns=["Date", "Ticker", "Split Ratio"])
    )

    return dividends_df, splits_df


def main() -> None:
    tickers = get_sp100_tickers()
    print(f"Found {len(tickers)} S&P 100 tickers.")

    pd.DataFrame({"Ticker": tickers}).to_csv(
        OUTPUT_DIR / "sp100_tickers.csv",
        index=False
    )

    prices = download_daily_prices(tickers, START_DATE, END_DATE)
    prices.to_csv(OUTPUT_DIR / "sp100_daily_prices.csv", index=False)

    dividends, splits = download_actions(tickers, START_DATE, END_DATE)
    dividends.to_csv(OUTPUT_DIR / "sp100_dividends.csv", index=False)
    splits.to_csv(OUTPUT_DIR / "sp100_splits.csv", index=False)

    print("\nDone.")
    print(f"Saved files in: {OUTPUT_DIR.resolve()}")
    print(f"  - sp100_tickers.csv")
    print(f"  - sp100_daily_prices.csv")
    print(f"  - sp100_dividends.csv")
    print(f"  - sp100_splits.csv")


if __name__ == "__main__":
    main()