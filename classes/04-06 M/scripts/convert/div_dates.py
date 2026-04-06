import csv
import json
from collections import defaultdict

input_csv = "sp100_dividends.csv"
output_json = "sp100_dividends.json"

# Structure:
# {
#   "2026-01-15": [
#     {"ticker": "AAPL", "dividend": 0.25},
#     {"ticker": "MSFT", "dividend": 0.75}
#   ],
#   ...
# }

data = defaultdict(list)

with open(input_csv, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, fieldnames=["date", "dividend", "ticker"])
    for row in reader:
        data[row["date"]].append({
            "ticker": row["ticker"],
            "dividend": float(row["dividend"])
        })

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(dict(data), f, indent=2)

print(f"Saved to {output_json}")