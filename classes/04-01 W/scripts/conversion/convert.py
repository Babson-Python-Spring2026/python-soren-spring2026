import json
import pandas as pd


PRICING_CSV = "pricing.csv"
MARKET_DATES_JSON = "mkt_dates.json"
TICKER_UNIVERSE_JSON = "ticker_universe.json"


def to_yyyymmdd(date_str: str) -> int:
    return int(date_str.replace("-", ""))


# Load inputs
prices = pd.read_csv(PRICING_CSV, usecols=["Date", "Ticker", "raw_close", "adjusted_close"])
with open(MARKET_DATES_JSON) as f:
    market_dates = json.load(f)

market_dates = sorted(market_dates)
market_date_set = set(market_dates)
last_market_date = market_dates[-1]

# Keep only rows on known market dates and require both prices to be present
valid_rows = prices[
    prices["Date"].isin(market_date_set)
    & prices["Ticker"].notna()
    & prices["raw_close"].notna()
    & prices["adjusted_close"].notna()
].copy()

# Remove duplicate ticker/date rows if any
valid_rows = valid_rows.drop_duplicates(subset=["Ticker", "Date"])

# Map each market date to its position in the master calendar
date_to_idx = {date: i for i, date in enumerate(market_dates)}

ticker_universe = {}

for ticker, group in valid_rows.groupby("Ticker", sort=True):
    ticker_dates = sorted(group["Date"].unique(), key=date_to_idx.__getitem__)
    idxs = [date_to_idx[d] for d in ticker_dates]

    ranges = []
    start_idx = idxs[0]
    prev_idx = idxs[0]

    for idx in idxs[1:]:
        # Continuous if the ticker is valid on the next market date
        if idx == prev_idx + 1:
            prev_idx = idx
            continue

        ranges.append({
            "start_date": to_yyyymmdd(market_dates[start_idx]),
            "end_date": to_yyyymmdd(market_dates[prev_idx]),
        })
        start_idx = prev_idx = idx

    # Final range
    end_date = 99999999 if prev_idx == len(market_dates) - 1 else to_yyyymmdd(market_dates[prev_idx])
    ranges.append({
        "start_date": to_yyyymmdd(market_dates[start_idx]),
        "end_date": end_date,
    })

    ticker_universe[ticker] = ranges

# Write sorted JSON by ticker
with open(TICKER_UNIVERSE_JSON, "w") as f:
    json.dump(ticker_universe, f, indent=2, sort_keys=True)