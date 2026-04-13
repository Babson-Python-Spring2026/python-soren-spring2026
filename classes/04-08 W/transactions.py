import json
from pathlib import Path


TRANSACTIONS_FILE = Path(__file__).parent / "transactions.json"


def load_transactions(file_path=TRANSACTIONS_FILE):
    """
    Load transactions from JSON if the file exists.
    Otherwise return an empty list.
    """
    if not file_path.exists():
        return []

    with open(file_path, "r") as f:
        return json.load(f)


def save_transactions(transactions, file_path=TRANSACTIONS_FILE):
    """
    Save the full transactions list back to JSON.
    """
    with open(file_path, "w") as f:
        json.dump(transactions, f, indent=4)


def get_positive_float(prompt):
    """
    Repeatedly ask until the user enters a positive number.
    """
    while True:
        try:
            value = float(input(prompt).strip())
            if value <= 0:
                print("Value must be greater than 0.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")


def get_transaction_type():
    """
    Ask for one of the four allowed transaction types.
    """
    valid_types = {"contribution", "withdrawal", "buy", "sell"}

    while True:
        txn_type = input(
            "Enter transaction type "
            "(contribution, withdrawal, buy, sell): "
        ).strip().lower()

        if txn_type in valid_types:
            return txn_type

        print("Invalid transaction type.")


def create_transaction(transaction_date):
    """
    Create one transaction for the given date.
    No cash/share validation yet.
    Only local field validation.
    """
    txn_type = get_transaction_type()

    transaction = {
        "date": transaction_date,
        "type": txn_type
    }

    if txn_type in {"contribution", "withdrawal"}:
        amount = get_positive_float("Enter amount: ")
        transaction["amount"] = amount

    elif txn_type in {"buy", "sell"}:
        ticker = input("Enter ticker: ").strip().upper()
        shares = get_positive_float("Enter number of shares: ")
        price = get_positive_float("Enter price per share: ")

        transaction["ticker"] = ticker
        transaction["shares"] = shares
        transaction["price"] = price

    return transaction


def transaction_entry_session():
    """
    Main workflow:
    - load prior transactions
    - set a working date
    - enter multiple transactions for that date
    - save after each new transaction
    """
    transactions = load_transactions()
    print(f"\nLoaded {len(transactions)} existing transaction(s).")

    current_date = input("Enter transaction date (YYYY-MM-DD): ").strip()

    while True:
        print("\nTransaction Menu")
        print("1. Add transaction")
        print("2. Change working date")
        print("3. Show all transactions")
        print("4. Save and exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            transaction = create_transaction(current_date)
            transactions.append(transaction)
            save_transactions(transactions)
            print("\nTransaction added:")
            print(transaction)

        elif choice == "2":
            current_date = input("Enter new transaction date (YYYY-MM-DD): ").strip()
            print(f"Working date changed to {current_date}")

        elif choice == "3":
            if not transactions:
                print("\nNo transactions recorded.")
            else:
                print("\nTransactions:")
                for txn in transactions:
                    print(txn)

        elif choice == "4":
            save_transactions(transactions)
            print("\nTransactions saved. Exiting.")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    transaction_entry_session()