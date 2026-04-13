import json
from collections import defaultdict

# path from check/ → up to data/system
FILE_PATH = "classes/04-08 W/data/system/prices_dates.json"

with open(FILE_PATH, "r") as f:
    data = json.load(f)

# count how many records each ticker has
ticker_counts = defaultdict(int)

for date in data:
    records = data[date]
    for record in records:
        ticker = record["ticker"]
        ticker_counts[ticker] += 1

# print tickers that do NOT have 308 records
for ticker, count in ticker_counts.items():
    if count != 308:
        print(f"{ticker}: {count}")