import json
import os

TRANSACTIONS_FILE = "transactions.json"


def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, "r") as f:
            return json.load(f)
    return []


def save_transactions(transactions):
    with open(TRANSACTIONS_FILE, "w") as f:
        json.dump(transactions, f, indent=2)


def create_transaction(date, transaction_type, amount=None, ticker=None, shares=None, price=None):
    transaction = {
        "date": date,
        "type": transaction_type,
    }

    if transaction_type == "contribution" or transaction_type == "withdrawal":
        transaction["amount"] = amount

    elif transaction_type == "buy" or transaction_type == "sell":
        transaction["ticker"] = ticker
        transaction["shares"] = shares
        transaction["price"] = price

    return transaction


def get_cash_balance(as_of_date):
    pass


def build_portfolio(as_of_date):
    pass


def list_transactions_for_ticker(ticker):
    pass


def get_working_date():
    return input("Enter working date (YYYY-MM-DD): ")


def get_transaction_type():
    return input("Enter transaction type (contribution, withdrawal, buy, sell, done): ").strip().lower()


def enter_transaction(date):
    transaction_type = get_transaction_type()

    if transaction_type == "done":
        return None

    if transaction_type == "contribution" or transaction_type == "withdrawal":
        amount = float(input("Enter amount: "))
        transaction = create_transaction(date, transaction_type, amount=amount)

    elif transaction_type == "buy" or transaction_type == "sell":
        ticker = input("Enter ticker: ").strip().upper()
        shares = float(input("Enter shares: "))
        price = float(input("Enter price: "))
        transaction = create_transaction(
            date,
            transaction_type,
            ticker=ticker,
            shares=shares,
            price=price,
        )

    else:
        print("Invalid transaction type")
        return None

    return transaction


def main():
    transactions = load_transactions()

    print("Transaction entry")
    working_date = get_working_date()

    while True:
        transaction = enter_transaction(working_date)

        if transaction is None:
            again = input("Enter another transaction for this date? (y/n): ").strip().lower()
            if again != "y":
                break
            continue

        transactions.append(transaction)
        save_transactions(transactions)
        print("Saved transaction")

        again = input("Enter another transaction for this date? (y/n): ").strip().lower()
        if again != "y":
            break


if __name__ == "__main__":
    main()