import json

# Load market dates from json
with open('classes/04-06 M/data/system/mkt_dates.json', 'r') as f:
    dates = json.load(f)

# Load prices keyed by ticker
with open('classes/04-06 M/data/system/prices_tickers.json', 'r') as f:
    price_tickers = json.load(f)

count = 0

for date in dates:
    for ticker in price_tickers:
        records = price_tickers[ticker]

        found = False

        for record in records:           

            if record['date'] == date:
                found = True
                break   # stop once we find a match

        if not found:
            count += 1
            print('date not found', count, date, ticker)

        if count > 10:
            break


symbols = set()
for ticker in price_tickers:
    symbols.add(ticker)

symbols=sorted(list(symbols))
with open('classes/04-06 M/data/system/ticker_universe.json', 'w') as f:
    json.dump(symbols, f, indent=2)   