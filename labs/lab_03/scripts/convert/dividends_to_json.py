import json
splits_by_date = {}
splits_by_tic = {}

with open('classes/04-06 M/data/source/portfolio_dividends_20260331b.csv', 'r') as f:

    next(f)  # skip header line

    for line in f:
        date, ticker, dividend = line.strip().split(',')        

        splits_by_date.setdefault(date, []).append({
            'ticker': ticker,
            'dividend': dividend
        })

        splits_by_tic.setdefault(ticker, []).append({
            'date': date,
            'dividend': dividend
        })

with open('classes/04-06 M/data/system/dividends_tickers.json', 'w') as f:
    json.dump(splits_by_tic, f, indent=2)

with open('classes/04-06 M/data/system/dividends_dates.json', 'w') as f:
    json.dump(splits_by_date, f, indent=2)