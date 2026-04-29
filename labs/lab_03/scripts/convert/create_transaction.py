import json
import os

# paths
BASE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "system")

TRANSACTIONS_FILE   = os.path.join(BASE, "transactions", "transactions.json")
MKT_DATES_FILE      = os.path.join(BASE, "mkt_dates.json")
TICKER_FILE         = os.path.join(BASE, "ticker_universe.json")
PRICES_DATES_FILE   = os.path.join(BASE, "prices_dates.json")
PRICES_TICKERS_FILE = os.path.join(BASE, "prices_tickers.json")


def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"  ERROR: File not found -> {path}")
        raise
    except json.JSONDecodeError:
        print(f"  ERROR: Could not parse JSON -> {path}")
        raise

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# validation
def get_valid_date():
    
    mkt_dates = load_json(MKT_DATES_FILE)
    while True:
        date = input("  Enter date (YYYY-MM-DD): ").strip()
        if date in mkt_dates:
            return date
        print(f"    '{date}' is not a valid market date. Please try again.")

def get_valid_ticker():
    
    tickers = load_json(TICKER_FILE)
    while True:
        ticker = input("  Enter ticker: ").strip().upper()
        if ticker in tickers:
            return ticker
        print(f"    '{ticker}' is not in the ticker universe. Please try again.")

def get_valid_transaction_type():
    valid = {"buy", "sell", "contribution", "withdrawal"}
    while True:
        t = input("  Enter type (buy / sell / contribution / withdrawal): ").strip().lower()
        if t in valid:
            return t
        print(f"    '{t}' is not valid. Choose: buy, sell, contribution, withdrawal.")

def get_valid_shares(txn_type):
    label = "amount ($)" if txn_type in ("contribution", "withdrawal") else "shares"
    while True:
        raw = input(f"  Enter {label}: ").strip()
        try:
            val = float(raw)
            if val > 0:
                return val
            print("    Value must be positive.")
        except ValueError:
            print("    Please enter a number.")

def get_valid_price(ticker, date, txn_type):
    if txn_type in ("contribution", "withdrawal"):
        return 1.0

    prices_dates = load_json(PRICES_DATES_FILE)
    day_prices = {entry["ticker"]: entry["raw_price"]
                  for entry in prices_dates.get(date, [])}
    mkt_price = day_prices.get(ticker)

    if mkt_price is None:
        print(f"    Warning: no market price found for {ticker} on {date}. Accepting any price.")
        while True:
            raw = input("  Enter price: ").strip()
            try:
                val = float(raw)
                if val > 0:
                    return val
                print("    Price must be positive.")
            except ValueError:
                print("    Please enter a number.")
    else:
        low  = round(mkt_price * 0.85, 6)
        high = round(mkt_price * 1.15, 6)
        while True:
            raw = input(f"  Enter price  (market={mkt_price:.2f}, allowed {low:.2f}-{high:.2f}): ").strip()
            try:
                val = float(raw)
                if low <= val <= high:
                    return val
                print(f"    {val} is outside the +/-15% range ({low:.2f}-{high:.2f}).")
            except ValueError:
                print("    Please enter a number.")

def next_record_number(transactions):
    if not transactions:
        return 1
    return max(t["record_number"] for t in transactions) + 1

def confirm(prompt="  Confirm? (y/n): "):
    return input(prompt).strip().lower() in ("y", "yes")

# create transaction

def create_transaction():
    
    
    transactions = load_json(TRANSACTIONS_FILE)

    print("\n-- New Transaction ------------------------------------------")
    txn_type = get_valid_transaction_type()
    date     = get_valid_date()

    if txn_type in ("contribution", "withdrawal"):
        ticker = "$$$$"
        shares = get_valid_shares(txn_type)
        price  = 1.0
        if txn_type == "withdrawal":
            shares = -shares   # stored as negative cash flow
    else:
        ticker = get_valid_ticker()
        shares = get_valid_shares(txn_type)
        price  = get_valid_price(ticker, date, txn_type)

    # Confirmation summary
    print()
    print("  -- Review your transaction ---------------------------------")
    print(f"     Type   : {txn_type}")
    print(f"     Date   : {date}")
    print(f"     Ticker : {ticker}")
    print(f"     Shares : {abs(shares):,.4f}")
    print(f"     Price  : ${price:,.4f}")
    print(f"     Value  : ${abs(shares) * price:,.2f}")
    print()

    if not confirm("  Save this transaction? (y/n): "):
        print("  Transaction cancelled.\n")
        return None

    record = {
        "date":          date,
        "type":          txn_type,
        "record_number": next_record_number(transactions),
        "ticker":        ticker,
        "shares":        shares,
        "price":         price,
    }

    transactions.append(record)
    transactions.sort(key=lambda t: (t["date"], t["record_number"]))
    save_json(TRANSACTIONS_FILE, transactions)

    print(f"  Transaction saved (record #{record['record_number']})\n")
    return record

# transaction details recording
def get_transactions_for_ticker(ticker):
    transactions = load_json(TRANSACTIONS_FILE)
    return [t for t in transactions if t["ticker"] == ticker]

def print_transactions_table(ticker, rows):
    if not rows:
        print(f"\n  No transactions found for {ticker}.\n")
        return

    header = (f"{'#':>6}  {'Date':<12}  {'Type':<14}  "
              f"{'Shares':>10}  {'Price':>12}  {'Value':>14}")
    sep = "-" * len(header)

    print()
    print(f"  Transactions for {ticker}")
    print("  " + sep)
    print("  " + header)
    print("  " + sep)

    total_bought = 0.0
    total_sold   = 0.0

    for t in rows:
        shares_str = f"{abs(t['shares']):,.4f}"
        price_str  = f"{t['price']:,.4f}"
        value      = abs(t['shares']) * t['price']
        value_str  = f"{value:,.2f}"

        print(f"  {t['record_number']:>6}  {t['date']:<12}  {t['type']:<14}  "
              f"{shares_str:>10}  {price_str:>12}  {value_str:>14}")

        if t["type"] == "buy":
            total_bought += value
        elif t["type"] == "sell":
            total_sold += value

    print("  " + sep)
    print(f"  Total records : {len(rows)}")

    if ticker != "$$$$":
        print(f"  Total bought  : ${total_bought:>14,.2f}")
        print(f"  Total sold    : ${total_sold:>14,.2f}")
        net  = total_sold - total_bought
        sign = "+" if net >= 0 else ""
        print(f"  Net realized  : {sign}${net:>13,.2f}")

    print()

def list_transactions_for_ticker():
    ticker = get_valid_ticker()
    rows   = get_transactions_for_ticker(ticker)
    print_transactions_table(ticker, rows)

#building tools
def build_stocks_by_date():
: dict  {date: [{"ticker", "shares", "average_cost"}, ...]}
    transactions = load_json(TRANSACTIONS_FILE)
    prices_dates = load_json(PRICES_DATES_FILE)
    mkt_dates    = load_json(MKT_DATES_FILE)

    # Index stock transactions by date
    txns_by_date = {}
    for t in transactions:
        if t["type"] in ("buy", "sell"):
            txns_by_date.setdefault(t["date"], []).append(t)

    # Index splits by date  {date: {ticker: {shares_in, shares_out}}}
    splits_by_date = {}
    for date, entries in prices_dates.items():
        for e in entries:
            if e["shares_in"] != 1 or e["shares_out"] != 1:
                splits_by_date.setdefault(date, {})[e["ticker"]] = {
                    "shares_in":  e["shares_in"],
                    "shares_out": e["shares_out"],
                }

    positions = {}
    result    = {}

    for date in mkt_dates:

        # 1. carry forward
        positions = {
            ticker: {"shares": pos["shares"], "average_cost": pos["average_cost"]}
            for ticker, pos in positions.items()
        }

        # 2. apply splits
        for ticker, split in splits_by_date.get(date, {}).items():
            if ticker in positions:
                ratio = split["shares_out"] / split["shares_in"]
                positions[ticker]["shares"]       = round(positions[ticker]["shares"] * ratio, 6)
                positions[ticker]["average_cost"] = round(positions[ticker]["average_cost"] / ratio, 6)

        # 3. apply stock transactions
        for txn in txns_by_date.get(date, []):
            ticker = txn["ticker"]
            shares = txn["shares"]
            price  = txn["price"]

            if txn["type"] == "buy":
                if ticker in positions:
                    old_shares = positions[ticker]["shares"]
                    old_cost   = positions[ticker]["average_cost"]
                    new_shares = old_shares + shares
                    new_cost   = ((old_shares * old_cost) + (shares * price)) / new_shares
                    positions[ticker] = {
                        "shares":       round(new_shares, 6),
                        "average_cost": round(new_cost, 6),
                    }
                else:
                    positions[ticker] = {
                        "shares":       round(shares, 6),
                        "average_cost": round(price, 6),
                    }

            elif txn["type"] == "sell":
                if ticker in positions:
                    positions[ticker]["shares"] = round(
                        positions[ticker]["shares"] - shares, 6
                    )
                    if positions[ticker]["shares"] == 0:
                        del positions[ticker]

        # 4. snapshot
        result[date] = [
            {"ticker": ticker, "shares": pos["shares"], "average_cost": pos["average_cost"]}
            for ticker, pos in sorted(positions.items())
            if pos["shares"] > 0
        ]

    return result


def build_cash_by_date(stocks_by_date=None):
    """
    Reconstruct the cash balance for every market date.

    Accepts an optional pre-built stocks_by_date to avoid rebuilding it.

    Cash changes from:
        contribution / withdrawal  -> +/-(shares x price)
        buy                        -> -(shares x price)
        sell                       -> +(shares x price)
        dividend                   -> +(shares_held x dividend_per_share)

    State read   : transactions.json, prices_dates.json, mkt_dates.json
    Transition   : accumulate daily cash flows across all market dates
    Invariant    : cash_by_date[d] = cumulative net cash through date d
    Returns      : dict  {date: float}
    """
    transactions = load_json(TRANSACTIONS_FILE)
    prices_dates = load_json(PRICES_DATES_FILE)
    mkt_dates    = load_json(MKT_DATES_FILE)

    txns_by_date = {}
    for t in transactions:
        txns_by_date.setdefault(t["date"], []).append(t)

    dividends_by_date = {}
    for date, entries in prices_dates.items():
        for e in entries:
            if e["dividend"] > 0:
                dividends_by_date.setdefault(date, {})[e["ticker"]] = e["dividend"]

    # Use provided stocks_by_date or build it once
    if stocks_by_date is None:
        stocks_by_date = build_stocks_by_date()

    cash   = 0.0
    result = {}

    for date in mkt_dates:
        for txn in txns_by_date.get(date, []):
            if txn["type"] == "contribution":
                cash += txn["shares"] * txn["price"]
            elif txn["type"] == "withdrawal":
                cash += txn["shares"] * txn["price"]   # shares already negative
            elif txn["type"] == "buy":
                cash -= txn["shares"] * txn["price"]
            elif txn["type"] == "sell":
                cash += txn["shares"] * txn["price"]

        if date in dividends_by_date:
            position_map = {row["ticker"]: row["shares"]
                            for row in stocks_by_date.get(date, [])}
            for ticker, div_per_share in dividends_by_date[date].items():
                cash += position_map.get(ticker, 0) * div_per_share

        result[date] = round(cash, 2)

    return result

# retrieve cash balance
def get_cash_balance(as_of_date=None):

    if as_of_date is None:
        as_of_date = get_valid_date()

    cash_by_date = build_cash_by_date()

    if as_of_date not in cash_by_date:
        print(f"\n  No cash data for {as_of_date}.\n")
        return None

    balance = cash_by_date[as_of_date]
    print(f"\n  Cash balance as of {as_of_date}:  ${balance:>16,.2f}\n")
    return balance

# build portfolio
def build_portfolio(as_of_date=None):
    
    if as_of_date is None:
        as_of_date = get_valid_date()

    # Build stocks once and pass into cash builder — no double build
    stocks_by_date = build_stocks_by_date()
    cash_by_date   = build_cash_by_date(stocks_by_date=stocks_by_date)
    prices_dates   = load_json(PRICES_DATES_FILE)

    if as_of_date not in stocks_by_date:
        print(f"\n  No stock data for {as_of_date}.\n")
        return None

    # Price lookup for the requested date
    price_lookup = {
        entry["ticker"]: entry["raw_price"]
        for entry in prices_dates.get(as_of_date, [])
    }

    # Build stock rows
    portfolio = []
    for row in stocks_by_date[as_of_date]:
        ticker     = row["ticker"]
        shares     = row["shares"]
        avg_cost   = row["average_cost"]
        mkt_price  = price_lookup.get(ticker, avg_cost)
        total_cost = round(shares * avg_cost, 2)
        total_mkt  = round(shares * mkt_price, 2)
        gain_loss  = round(total_mkt - total_cost, 2)
        gain_pct   = round((gain_loss / total_cost) * 100, 2) if total_cost != 0 else 0.0

        portfolio.append({
            "ticker":          ticker,
            "shares":          shares,
            "average_cost":    round(avg_cost, 2),
            "mkt_price":       round(mkt_price, 2),
            "total_avg_cost":  total_cost,
            "total_mkt_value": total_mkt,
            "gain_loss":       gain_loss,
            "gain_loss_pct":   gain_pct,
        })

    # Cash row
    cash = cash_by_date.get(as_of_date, 0.0)
    portfolio.insert(0, {
        "ticker":          "$$$$",
        "shares":          round(cash, 2),
        "average_cost":    1.0,
        "mkt_price":       1.0,
        "total_avg_cost":  round(cash, 2),
        "total_mkt_value": round(cash, 2),
        "gain_loss":       0.0,
        "gain_loss_pct":   0.0,
    })

    # Print table
    col = {"t": 8, "sh": 12, "ac": 11, "mp": 11, "tc": 15, "tv": 15, "gl": 13, "gp": 8}

    header = (
        f"{'Ticker':<{col['t']}}  {'Shares':>{col['sh']}}  "
        f"{'Avg Cost':>{col['ac']}}  {'Mkt Price':>{col['mp']}}  "
        f"{'Total Cost':>{col['tc']}}  {'Mkt Value':>{col['tv']}}  "
        f"{'Gain/Loss':>{col['gl']}}  {'G/L %':>{col['gp']}}"
    )
    sep = "-" * len(header)

    print(f"\n  Portfolio as of {as_of_date}")
    print("  " + sep)
    print("  " + header)
    print("  " + sep)

    total_cost_sum = 0.0
    total_mkt_sum  = 0.0
    total_gl_sum   = 0.0

    for row in portfolio:
        gl_str = f"{row['gain_loss']:>+,.2f}" if row["ticker"] != "$$$$" else "    ---"
        gp_str = f"{row['gain_loss_pct']:>+.2f}%" if row["ticker"] != "$$$$" else "     ---"

        print(
            f"  {row['ticker']:<{col['t']}}  "
            f"{row['shares']:>{col['sh']},.2f}  "
            f"{row['average_cost']:>{col['ac']},.2f}  "
            f"{row['mkt_price']:>{col['mp']},.2f}  "
            f"{row['total_avg_cost']:>{col['tc']},.2f}  "
            f"{row['total_mkt_value']:>{col['tv']},.2f}  "
            f"{gl_str:>{col['gl']}}  "
            f"{gp_str:>{col['gp']}}"
        )

        total_cost_sum += row["total_avg_cost"]
        total_mkt_sum  += row["total_mkt_value"]
        total_gl_sum   += row["gain_loss"]

    total_gl_pct = round((total_gl_sum / total_cost_sum) * 100, 2) if total_cost_sum != 0 else 0.0

    print("  " + sep)
    print(
        f"  {'TOTAL':<{col['t']}}  {'':>{col['sh']}}  {'':>{col['ac']}}  {'':>{col['mp']}}  "
        f"{total_cost_sum:>{col['tc']},.2f}  "
        f"{total_mkt_sum:>{col['tv']},.2f}  "
        f"{total_gl_sum:>{col['gl']},.2f}  "
        f"{total_gl_pct:>{col['gp']}.2f}%"
    )

    # Summary stats
    stock_rows = [r for r in portfolio if r["ticker"] != "$$$$"]
    winners    = [r for r in stock_rows if r["gain_loss"] > 0]
    losers     = [r for r in stock_rows if r["gain_loss"] < 0]
    best       = max(stock_rows, key=lambda r: r["gain_loss_pct"], default=None)
    worst      = min(stock_rows, key=lambda r: r["gain_loss_pct"], default=None)

    print()
    print("  -- Summary -------------------------------------------------")
    print(f"     Positions     : {len(stock_rows)} stocks + cash")
    print(f"     Winners       : {len(winners)}    Losers : {len(losers)}")
    if best:
        print(f"     Best position : {best['ticker']}  ({best['gain_loss_pct']:+.2f}%)")
    if worst:
        print(f"     Worst position: {worst['ticker']}  ({worst['gain_loss_pct']:+.2f}%)")
    print(f"     Total invested: ${total_cost_sum:>16,.2f}")
    print(f"     Total value   : ${total_mkt_sum:>16,.2f}")
    sign = "+" if total_gl_sum >= 0 else ""
    print(f"     Total gain    : {sign}${total_gl_sum:>15,.2f}  ({total_gl_pct:+.2f}%)")
    print()

    return portfolio

# menu
def print_menu():
    print("\n" + "=" * 52)
    print("   Lab 3 -- Portfolio System")
    print("=" * 52)
    print("   1.  Create a transaction")
    print("   2.  List transactions for a ticker")
    print("   3.  Get cash balance on a date")
    print("   4.  Build portfolio on a date")
    print("   q.  Quit")
    print("=" * 52)

if __name__ == "__main__":
    while True:
        print_menu()
        choice = input("   Choose (1-4 or q): ").strip().lower()

        if choice == "q":
            print("\n  Goodbye!\n")
            break
        elif choice == "1":
            create_transaction()
        elif choice == "2":
            list_transactions_for_ticker()
        elif choice == "3":
            get_cash_balance()
        elif choice == "4":
            build_portfolio()
        else:
            print("\n  Invalid choice -- please enter 1, 2, 3, 4, or q.\n")
