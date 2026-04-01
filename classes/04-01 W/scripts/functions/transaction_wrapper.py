from pathlib import Path

from create_transaction import (
    append_transaction,
    build_market_event_rows,
    load_transactions,
    replay_transactions,
    save_transactions,
)


TRANSACTIONS_FILE = Path("transactions.csv")
DIVIDENDS_FILE = Path("portfolio_dividends_including_synthetic.csv")
SPLITS_FILE = Path("portfolio_splits_true_splits_only.csv")


def prompt_manual_transaction() -> dict | None:
    print("\nEnter a new transaction.")
    print("TYPE choices: BUY, SELL, CNTRB, WDRW")
    tx_type = input("TYPE (or X to exit): ").strip().upper()

    if tx_type == "X":
        return None

    if tx_type not in {"BUY", "SELL", "CNTRB", "WDRW"}:
        print("Invalid TYPE.")
        return {}

    date_text = input("DATE (YYYY-MM-DD or YYYYMMDD): ").strip()

    if tx_type in {"CNTRB", "WDRW"}:
        cash = input("CASH amount: ").strip()
        note = input("NOTE (optional): ").strip()
        return {
            "DATE": date_text,
            "TYPE": tx_type,
            "TICKER": "$$$$",
            "CASH": cash,
            "NOTE": note,
        }

    ticker = input("TICKER: ").strip().upper()
    shares = input("SHARES: ").strip()
    price = input("PRICE: ").strip()
    note = input("NOTE (optional): ").strip()

    return {
        "DATE": date_text,
        "TYPE": tx_type,
        "TICKER": ticker,
        "SHARES": shares,
        "PRICE": price,
        "NOTE": note,
    }


def main() -> None:
    print("Portfolio transaction wrapper")
    print("============================")
    print("1) Start from scratch")
    print("2) Load existing transaction file")

    choice = input("Choose 1 or 2: ").strip()

    if choice == "1":
        tx = build_market_event_rows(DIVIDENDS_FILE, SPLITS_FILE)
        save_transactions(tx, TRANSACTIONS_FILE)
        print(f"Created {TRANSACTIONS_FILE} with preloaded DIV and SPLT records.")
    elif choice == "2":
        tx = load_transactions(TRANSACTIONS_FILE)
        print(f"Loaded {len(tx)} rows from {TRANSACTIONS_FILE}.")
    else:
        print("Invalid choice.")
        return

    while True:
        print("\nCurrent file:", TRANSACTIONS_FILE)
        try:
            positions, cash = replay_transactions(tx)
        except ValueError as exc:
            print("Current transaction file is invalid:", exc)
            return

        print(f"Current cash: {cash:,.2f}")
        print("Current positions:", positions if positions else "{}")

        row = prompt_manual_transaction()
        if row is None:
            print("Exiting wrapper.")
            break
        if row == {}:
            continue

        try:
            tx, positions, cash = append_transaction(tx, row)
            save_transactions(tx, TRANSACTIONS_FILE)
            print("Transaction added.")
            print(f"Updated cash: {cash:,.2f}")
            print("Updated positions:", positions if positions else "{}")
        except ValueError as exc:
            print("Transaction rejected:", exc)


if __name__ == "__main__":
    main()
