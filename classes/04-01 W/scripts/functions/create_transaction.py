from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


TRANSACTION_COLUMNS = ["DATE", "TYPE", "TICKER", "SHARES", "PRICE", "CASH", "FACTOR", "NOTE"]

TYPE_ORDER = {
    "SPLT": 0,
    "DIV": 1,
    "CNTRB": 2,
    "BUY": 3,
    "SELL": 4,
    "WDRW": 5,
}

VALID_TYPES = set(TYPE_ORDER)


def empty_transaction_df() -> pd.DataFrame:
    return pd.DataFrame(columns=TRANSACTION_COLUMNS)


def load_transactions(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return empty_transaction_df()

    df = pd.read_csv(path, dtype=str)

    for col in TRANSACTION_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[TRANSACTION_COLUMNS].copy()
    return _clean_transaction_df(df)


def save_transactions(df: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()

    # Write blanks instead of NaN for readability.
    out = out.replace({pd.NA: "", "nan": "", "None": ""})
    out.to_csv(path, index=False)


def build_market_event_rows(
    dividends_file: str | Path | None = None,
    splits_file: str | Path | None = None,
) -> pd.DataFrame:
    rows = []

    if dividends_file:
        divs = pd.read_csv(dividends_file)
        for _, row in divs.iterrows():
            rows.append(
                {
                    "DATE": _normalize_date(row["Date"]),
                    "TYPE": "DIV",
                    "TICKER": str(row["Ticker"]).upper(),
                    "SHARES": "",
                    "PRICE": "",
                    "CASH": float(row["Dividend"]),
                    "FACTOR": "",
                    "NOTE": "Loaded from dividend source file",
                }
            )

    if splits_file:
        splits = pd.read_csv(splits_file)
        for _, row in splits.iterrows():
            rows.append(
                {
                    "DATE": _normalize_date(row["Date"]),
                    "TYPE": "SPLT",
                    "TICKER": str(row["Ticker"]).upper(),
                    "SHARES": "",
                    "PRICE": "",
                    "CASH": "",
                    "FACTOR": float(row["Split Ratio"]),
                    "NOTE": "Loaded from split source file",
                }
            )

    if not rows:
        return empty_transaction_df()

    df = pd.DataFrame(rows, columns=TRANSACTION_COLUMNS)
    return _clean_transaction_df(df)


def append_transaction(
    existing_df: pd.DataFrame,
    new_row: dict,
) -> tuple[pd.DataFrame, Dict[str, float], float]:
    df = existing_df.copy()
    row = normalize_transaction_row(new_row)

    candidate = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    state, cash = replay_transactions(candidate)

    return _clean_transaction_df(candidate), state, cash


def normalize_transaction_row(row: dict) -> dict:
    clean = {col: "" for col in TRANSACTION_COLUMNS}
    clean.update(row)

    clean["DATE"] = _normalize_date(clean["DATE"])
    clean["TYPE"] = str(clean["TYPE"]).upper().strip()
    clean["TICKER"] = str(clean.get("TICKER", "")).upper().strip()

    if clean["TYPE"] not in VALID_TYPES:
        raise ValueError(f"Invalid TYPE: {clean['TYPE']}")

    if clean["TYPE"] in {"CNTRB", "WDRW"}:
        clean["TICKER"] = "$$$$"

    clean["SHARES"] = _to_number_or_blank(clean.get("SHARES", ""))
    clean["PRICE"] = _to_number_or_blank(clean.get("PRICE", ""))
    clean["CASH"] = _to_number_or_blank(clean.get("CASH", ""))
    clean["FACTOR"] = _to_number_or_blank(clean.get("FACTOR", ""))
    clean["NOTE"] = str(clean.get("NOTE", "")).strip()

    _validate_row_fields(clean)
    return clean


def replay_transactions(df: pd.DataFrame) -> tuple[Dict[str, float], float]:
    tx = _clean_transaction_df(df)

    if tx.empty:
        return {}, 0.0

    ordered = tx.copy()
    ordered["__DATE_SORT"] = pd.to_datetime(ordered["DATE"], format="%Y%m%d")
    ordered["__TYPE_ORDER"] = ordered["TYPE"].map(TYPE_ORDER)
    ordered["__ROW_ORDER"] = range(len(ordered))
    ordered = ordered.sort_values(["__DATE_SORT", "__TYPE_ORDER", "__ROW_ORDER"])

    cash = 0.0
    shares = defaultdict(float)

    for row in ordered.itertuples(index=False):
        tx_type = row.TYPE
        ticker = row.TICKER

        if tx_type == "CNTRB":
            cash += float(row.CASH)

        elif tx_type == "WDRW":
            cash -= float(row.CASH)
            if cash < -1e-9:
                raise ValueError(
                    f"Cash would become negative after WDRW on {row.DATE}."
                )

        elif tx_type == "BUY":
            cost = float(row.SHARES) * float(row.PRICE)
            cash -= cost
            shares[ticker] += float(row.SHARES)
            if cash < -1e-9:
                raise ValueError(
                    f"Cash would become negative after BUY of {ticker} on {row.DATE}."
                )

        elif tx_type == "SELL":
            shares[ticker] -= float(row.SHARES)
            if shares[ticker] < -1e-9:
                raise ValueError(
                    f"Shares of {ticker} would become negative after SELL on {row.DATE}."
                )
            proceeds = float(row.SHARES) * float(row.PRICE)
            cash += proceeds

        elif tx_type == "DIV":
            held = shares[ticker]
            if held > 0:
                cash += held * float(row.CASH)

        elif tx_type == "SPLT":
            held = shares[ticker]
            if held > 0:
                shares[ticker] = held * float(row.FACTOR)

        _assert_share_invariant(shares)

    shares = {ticker: qty for ticker, qty in shares.items() if qty > 1e-9}
    return shares, cash


def _validate_row_fields(row: dict) -> None:
    tx_type = row["TYPE"]

    if tx_type in {"BUY", "SELL"}:
        if row["TICKER"] == "$$$$":
            raise ValueError(f"{tx_type} cannot use ticker $$$$.")
        if row["SHARES"] == "" or row["PRICE"] == "":
            raise ValueError(f"{tx_type} requires SHARES and PRICE.")
        if float(row["SHARES"]) <= 0 or float(row["PRICE"]) <= 0:
            raise ValueError(f"{tx_type} requires positive SHARES and PRICE.")

    elif tx_type in {"CNTRB", "WDRW"}:
        if row["CASH"] == "":
            raise ValueError(f"{tx_type} requires CASH.")
        if float(row["CASH"]) <= 0:
            raise ValueError(f"{tx_type} requires positive CASH.")

    elif tx_type == "DIV":
        if row["TICKER"] == "$$$$":
            raise ValueError("DIV requires a stock ticker.")
        if row["CASH"] == "":
            raise ValueError("DIV requires per-share CASH.")
        if float(row["CASH"]) <= 0:
            raise ValueError("DIV requires positive per-share CASH.")

    elif tx_type == "SPLT":
        if row["TICKER"] == "$$$$":
            raise ValueError("SPLT requires a stock ticker.")
        if row["FACTOR"] == "":
            raise ValueError("SPLT requires FACTOR.")
        if float(row["FACTOR"]) <= 0:
            raise ValueError("SPLT requires a positive FACTOR.")

    if row["DATE"] == "":
        raise ValueError("DATE is required.")


def _assert_share_invariant(shares: Dict[str, float]) -> None:
    for ticker, qty in shares.items():
        if ticker == "$$$$":
            continue
        if abs(qty - round(qty)) > 1e-9:
            raise ValueError(
                f"Share invariant failed for {ticker}. Non-cash shares must remain integers."
            )


def _normalize_date(value: object) -> str:
    text = str(value).strip()
    if text == "":
        raise ValueError("DATE cannot be blank.")
    dt = pd.to_datetime(text)
    return dt.strftime("%Y%m%d")


def _to_number_or_blank(value: object):
    text = str(value).strip()
    if text in {"", "nan", "None"}:
        return ""
    return float(text)


def _clean_transaction_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    for col in TRANSACTION_COLUMNS:
        if col not in out.columns:
            out[col] = ""

    out = out[TRANSACTION_COLUMNS].copy()

    out["DATE"] = out["DATE"].apply(lambda x: _normalize_date(x) if str(x).strip() != "" else "")
    out["TYPE"] = out["TYPE"].astype(str).str.upper().str.strip()
    out["TICKER"] = out["TICKER"].astype(str).str.upper().str.strip()

    numeric_cols = ["SHARES", "PRICE", "CASH", "FACTOR"]
    for col in numeric_cols:
        out[col] = out[col].apply(_to_number_or_blank)

    out["NOTE"] = out["NOTE"].fillna("").astype(str)

    return out
