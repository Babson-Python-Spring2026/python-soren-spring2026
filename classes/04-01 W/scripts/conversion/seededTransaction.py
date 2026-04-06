import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import pandas as pd


PRICING_CSV = "pricing.csv"
MARKET_DATES_JSON = "market_dates.json"
TICKER_UNIVERSE_JSON = "ticker_universe.json"
OUTPUT_CSV = "seeded_transactions.csv"

TARGET_RECORDS = 28
RANDOM_SEED = 17

VALID_TYPES = {"BUY", "SELL", "CNTRB", "WDRW", "DIV", "SPLT"}


def yyyymmdd_to_iso(value: int) -> str:
    if value == 99999999:
        raise ValueError("99999999 is open-ended and cannot be converted to a concrete date")
    s = str(value)
    return f"{s[:4]}-{s[4:6]}-{s[6:]}"


def load_market_dates(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        dates = json.load(f)
    dates = sorted(set(dates))
    if not dates:
        raise ValueError("market_dates.json is empty")
    return dates


def load_ticker_universe(path: str) -> dict[str, list[tuple[str, str | None]]]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    universe: dict[str, list[tuple[str, str | None]]] = {}
    for ticker, ranges in raw.items():
        parsed = []
        for r in ranges:
            start_date = yyyymmdd_to_iso(int(r["start_date"]))
            end_raw = int(r["end_date"])
            end_date = None if end_raw == 99999999 else yyyymmdd_to_iso(end_raw)
            parsed.append((start_date, end_date))
        universe[ticker] = parsed
    return universe


def ticker_valid_on_date(ticker: str, date: str, universe: dict[str, list[tuple[str, str | None]]]) -> bool:
    for start_date, end_date in universe.get(ticker, []):
        if date >= start_date and (end_date is None or date <= end_date):
            return True
    return False


def build_price_table(pricing_csv: str, market_dates: list[str], universe: dict[str, list[tuple[str, str | None]]]) -> pd.DataFrame:
    prices = pd.read_csv(pricing_csv, usecols=["Date", "Ticker", "raw_close", "adjusted_close"])
    prices["Date"] = prices["Date"].astype(str)
    prices["Ticker"] = prices["Ticker"].astype(str).str.upper()

    prices = prices[
        prices["Date"].isin(set(market_dates))
        & prices["Ticker"].notna()
        & prices["raw_close"].notna()
        & prices["adjusted_close"].notna()
    ].copy()

    prices = prices.drop_duplicates(subset=["Date", "Ticker"], keep="last")
    prices["price"] = prices["adjusted_close"].astype(float)

    prices = prices[
        prices.apply(lambda r: ticker_valid_on_date(r["Ticker"], r["Date"], universe), axis=1)
    ].copy()

    if prices.empty:
        raise ValueError("No valid pricing rows remain after filtering against market dates and ticker universe")

    return prices[["Date", "Ticker", "price"]].sort_values(["Date", "Ticker"]).reset_index(drop=True)


def pick_candidate_tickers(price_table: pd.DataFrame, min_days: int = 40, max_tickers: int = 5) -> list[str]:
    counts = price_table.groupby("Ticker")["Date"].nunique().sort_values(ascending=False)
    tickers = [ticker for ticker, n in counts.items() if n >= min_days]
    if len(tickers) < 3:
        tickers = counts.index.tolist()
    return tickers[:max_tickers]


def build_price_lookup(price_table: pd.DataFrame) -> dict[tuple[str, str], float]:
    return {
        (row.Date, row.Ticker): float(row.price)
        for row in price_table.itertuples(index=False)
    }


def dates_for_ticker(price_table: pd.DataFrame, ticker: str) -> list[str]:
    return sorted(price_table.loc[price_table["Ticker"] == ticker, "Date"].unique().tolist())


def nearest_affordable_shares(cash: float, price: float, target_weight: float = 0.18) -> int:
    budget = max(0.0, cash * target_weight)
    shares = int(budget // price)
    return max(1, shares)


def round_money(x: float) -> float:
    return round(float(x) + 1e-12, 2)


def choose_dividend_amount(position_shares: float, price: float) -> float:
    # Small plausible cash dividend.
    raw = position_shares * max(0.05, min(0.8, price * 0.0025))
    return max(5.0, round_money(raw))


def create_record(date: str, type_: str, ticker: str = "", shares: float = 0.0, price: float = 0.0,
                  amount: float = 0.0, split_ratio: float = 0.0, note: str = "") -> dict:
    if type_ not in VALID_TYPES:
        raise ValueError(f"Invalid TYPE: {type_}")
    return {
        "Date": date,
        "TYPE": type_,
        "Ticker": ticker,
        "Shares": "" if shares == 0.0 else round(shares, 6),
        "Price": "" if price == 0.0 else round_money(price),
        "Amount": "" if amount == 0.0 else round_money(amount),
        "SplitRatio": "" if split_ratio == 0.0 else round(split_ratio, 6),
        "Note": note,
    }


def apply_record(record: dict, cash: float, positions: dict[str, float]) -> tuple[float, dict[str, float]]:
    cash = float(cash)
    positions = dict(positions)

    t = record["TYPE"]
    ticker = record["Ticker"] or ""
    shares = float(record["Shares"]) if record["Shares"] != "" else 0.0
    price = float(record["Price"]) if record["Price"] != "" else 0.0
    amount = float(record["Amount"]) if record["Amount"] != "" else 0.0
    split_ratio = float(record["SplitRatio"]) if record["SplitRatio"] != "" else 0.0

    if t == "CNTRB":
        cash += amount
    elif t == "WDRW":
        cash -= amount
    elif t == "BUY":
        cash -= shares * price
        positions[ticker] += shares
    elif t == "SELL":
        cash += shares * price
        positions[ticker] -= shares
    elif t == "DIV":
        cash += amount
    elif t == "SPLT":
        positions[ticker] *= split_ratio
    else:
        raise ValueError(t)

    if cash < -1e-9:
        raise ValueError(f"Negative cash after record: {record}")
    for tk, sh in positions.items():
        if sh < -1e-9:
            raise ValueError(f"Negative shares for {tk} after record: {record}")

    cleaned = defaultdict(float)
    for tk, sh in positions.items():
        cleaned[tk] = 0.0 if abs(sh) < 1e-9 else sh

    return round_money(cash), cleaned


def choose_split_ticker(candidates: list[str], ticker_dates_map: dict[str, list[str]]) -> str:
    ranked = sorted(candidates, key=lambda t: len(ticker_dates_map[t]), reverse=True)
    return ranked[0]


def build_seeded_transactions(
    pricing_csv: str,
    market_dates_json: str,
    ticker_universe_json: str,
    output_csv: str,
    target_records: int = TARGET_RECORDS,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    random.seed(seed)

    market_dates = load_market_dates(market_dates_json)
    universe = load_ticker_universe(ticker_universe_json)
    price_table = build_price_table(pricing_csv, market_dates, universe)
    price_lookup = build_price_lookup(price_table)

    candidates = pick_candidate_tickers(price_table)
    if len(candidates) < 3:
        raise ValueError("Need at least 3 usable tickers")

    ticker_dates_map = {ticker: dates_for_ticker(price_table, ticker) for ticker in candidates}

    common_dates = sorted(set(market_dates).intersection(set(price_table["Date"].unique())))
    if len(common_dates) < 80:
        raise ValueError("Not enough common valid market dates to build a plausible transaction history")

    records: list[dict] = []
    cash = 0.0
    positions: dict[str, float] = defaultdict(float)

    # 1) Start with contributions.
    initial_dates = [common_dates[2], common_dates[9], common_dates[20]]
    initial_amounts = [25000.00, 12000.00, 8000.00]
    for d, amt in zip(initial_dates, initial_amounts):
        rec = create_record(d, "CNTRB", amount=amt, note="initial funding")
        cash, positions = apply_record(rec, cash, positions)
        records.append(rec)

    # 2) Early buys across several tickers.
    buy_plan = [
        (common_dates[3], candidates[0]),
        (common_dates[6], candidates[1]),
        (common_dates[11], candidates[2]),
        (common_dates[16], candidates[0]),
        (common_dates[22], candidates[1]),
        (common_dates[24], candidates[3] if len(candidates) > 3 else candidates[2]),
    ]

    for d, ticker in buy_plan:
        if (d, ticker) not in price_lookup:
            continue
        price = price_lookup[(d, ticker)]
        shares = nearest_affordable_shares(cash, price, target_weight=0.14)
        cost = shares * price
        if cost > cash:
            shares = max(1, int(cash // price))
        if shares < 1:
            continue
        rec = create_record(d, "BUY", ticker=ticker, shares=shares, price=price, note="seed buy")
        cash, positions = apply_record(rec, cash, positions)
        records.append(rec)

    # 3) Add another contribution.
    rec = create_record(common_dates[30], "CNTRB", amount=7000.00, note="monthly contribution")
    cash, positions = apply_record(rec, cash, positions)
    records.append(rec)

    # 4) A few dividends on held names.
    dividend_points = [common_dates[33], common_dates[41], common_dates[48]]
    held_tickers = [t for t in candidates if positions[t] > 0]
    for d in dividend_points:
        if not held_tickers:
            break
        ticker = random.choice(held_tickers)
        if (d, ticker) not in price_lookup:
            continue
        div_amt = choose_dividend_amount(positions[ticker], price_lookup[(d, ticker)])
        rec = create_record(d, "DIV", ticker=ticker, amount=div_amt, note="cash dividend")
        cash, positions = apply_record(rec, cash, positions)
        records.append(rec)

    # 5) One split event on a long-held ticker.
    split_ticker = choose_split_ticker(candidates, ticker_dates_map)
    split_date_candidates = [
        d for d in ticker_dates_map[split_ticker]
        if d > common_dates[26] and d < common_dates[-20] and positions[split_ticker] > 0
    ]
    if split_date_candidates:
        split_date = split_date_candidates[len(split_date_candidates) // 2]
        rec = create_record(split_date, "SPLT", ticker=split_ticker, split_ratio=2.0, note="2-for-1 split")
        cash, positions = apply_record(rec, cash, positions)
        records.append(rec)

    # 6) Repeated buys and sells on same names.
    trade_points = [
        (common_dates[52], "SELL"),
        (common_dates[56], "BUY"),
        (common_dates[60], "SELL"),
        (common_dates[65], "BUY"),
        (common_dates[69], "SELL"),
        (common_dates[73], "BUY"),
    ]

    for d, action in trade_points:
        tradable = [t for t in candidates if (d, t) in price_lookup]
        if not tradable:
            continue

        if action == "SELL":
            owned = [t for t in tradable if positions[t] > 0]
            if not owned:
                continue
            ticker = random.choice(owned)
            max_shares = math.floor(positions[ticker])
            if max_shares < 1:
                continue
            shares = max(1, max_shares // 3)
            price = price_lookup[(d, ticker)]
            rec = create_record(d, "SELL", ticker=ticker, shares=shares, price=price, note="partial trim")
        else:
            ticker = random.choice(tradable)
            price = price_lookup[(d, ticker)]
            shares = nearest_affordable_shares(cash, price, target_weight=0.10)
            shares = min(shares, max(1, int(cash // price)))
            if shares < 1:
                continue
            rec = create_record(d, "BUY", ticker=ticker, shares=shares, price=price, note="add position")

        cash, positions = apply_record(rec, cash, positions)
        records.append(rec)

    # 7) Withdrawals, but keep cash nonnegative.
    withdrawal_points = [common_dates[58], common_dates[76]]
    for d in withdrawal_points:
        max_withdraw = min(cash, 3500.00)
        if max_withdraw >= 500.00:
            amt = round_money(max_withdraw * 0.55)
            rec = create_record(d, "WDRW", amount=amt, note="cash withdrawal")
            cash, positions = apply_record(rec, cash, positions)
            records.append(rec)

    # 8) More dividends later.
    for d in [common_dates[79], common_dates[84]]:
        owned = [t for t in candidates if positions[t] > 0 and (d, t) in price_lookup]
        if not owned:
            continue
        ticker = random.choice(owned)
        amt = choose_dividend_amount(positions[ticker], price_lookup[(d, ticker)])
        rec = create_record(d, "DIV", ticker=ticker, amount=amt, note="cash dividend")
        cash, positions = apply_record(rec, cash, positions)
        records.append(rec)

    # 9) Add filler trades until target length is reached.
    filler_dates = common_dates[85:]
    for d in filler_dates:
        if len(records) >= target_records:
            break

        available = [t for t in candidates if (d, t) in price_lookup]
        if not available:
            continue

        if random.random() < 0.35 and any(positions[t] > 0 for t in available):
            ticker = random.choice([t for t in available if positions[t] > 0])
            shares = max(1, math.floor(positions[ticker] * random.choice([0.2, 0.25, 0.33])))
            shares = min(shares, math.floor(positions[ticker]))
            if shares < 1:
                continue
            price = price_lookup[(d, ticker)]
            rec = create_record(d, "SELL", ticker=ticker, shares=shares, price=price, note="rebalance sell")
        else:
            ticker = random.choice(available)
            price = price_lookup[(d, ticker)]
            max_affordable = int(cash // price)
            if max_affordable < 1:
                continue
            shares = max(1, min(max_affordable, random.randint(1, max(1, min(20, max_affordable)))))
            rec = create_record(d, "BUY", ticker=ticker, shares=shares, price=price, note="rebalance buy")

        cash, positions = apply_record(rec, cash, positions)
        records.append(rec)

    # 10) Final safety checks.
    records = sorted(records, key=lambda r: (r["Date"], r["TYPE"], r["Ticker"]))
    cash_check = 0.0
    positions_check: dict[str, float] = defaultdict(float)
    for rec in records:
        cash_check, positions_check = apply_record(rec, cash_check, positions_check)

    if len(records) < 25:
        raise ValueError(f"Generated only {len(records)} records; need at least 25")

    if len(records) > 30:
        records = records[:30]
        cash_check = 0.0
        positions_check = defaultdict(float)
        for rec in records:
            cash_check, positions_check = apply_record(rec, cash_check, positions_check)

    df = pd.DataFrame(records, columns=[
        "Date", "TYPE", "Ticker", "Shares", "Price", "Amount", "SplitRatio", "Note"
    ])
    df.to_csv(output_csv, index=False)

    print(f"Wrote {len(df)} records to {output_csv}")
    print(f"Ending cash: {cash_check:.2f}")
    print("Ending positions:")
    for ticker, shares in sorted(positions_check.items()):
        if shares > 0:
            print(f"  {ticker}: {shares:.6f}")

    return df


if __name__ == "__main__":
    build_seeded_transactions(
        pricing_csv=PRICING_CSV,
        market_dates_json=MARKET_DATES_JSON,
        ticker_universe_json=TICKER_UNIVERSE_JSON,
        output_csv=OUTPUT_CSV,
        target_records=28,
        seed=RANDOM_SEED,
    )