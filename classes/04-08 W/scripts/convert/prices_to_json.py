import json

# Final output structures
prices_by_date = {}
prices_by_tic = {}

# Load splits keyed by date
with open('classes/04-06 M/data/system/splits_dates.json', 'r') as f:
    splits_by_date = json.load(f)

# Load dividends keyed by date
with open('classes/04-06 M/data/system/dividends_dates.json', 'r') as f:
    dividends_by_date = json.load(f)

# Read the prices file
with open('classes/04-06 M/data/source/portfolio_prices_raw_and_split_adjusted_20260331b.csv', 'r') as fprices:
    next(fprices)  # skip header
   
    for line in fprices:       
        # Read one price record
        date, price_ticker, raw, adj = line.strip().split(',')
        
        # Default values:
        # no split on this date+ticker means 1-for-1
        # no dividend on this date+ticker means 0.0
        shares_in = 1
        shares_out = 1
        dividend = 0.0

        # Check whether this date has any splits
        if date in splits_by_date:
            for split_record in splits_by_date[date]:
                if split_record['ticker'] == price_ticker:
                    shares_in = split_record['shares_in']
                    shares_out = split_record['shares_out']
                    break

        # Check whether this date has any dividends
        if date in dividends_by_date:
            for div_record in dividends_by_date[date]:
                if div_record['ticker'] == price_ticker:
                    dividend = float(div_record['dividend'])
                    break

        # Store by date
        prices_by_date.setdefault(date, []).append({
            'ticker': price_ticker,
            'raw_price': float(raw),
            'shares_in': shares_in,
            'shares_out': shares_out,
            'dividend': dividend
        })

        

        # Store by ticker
        prices_by_tic.setdefault(price_ticker, []).append({
            'date': date,
            'raw_price': float(raw),
            'shares_in': shares_in,
            'shares_out': shares_out,
            'dividend': dividend
        })

        


# will sort dictionaires based on outer key
prices_by_date = dict(sorted(prices_by_date.items())) 
prices_by_tic = dict(sorted(prices_by_tic.items()))  



# sort the inner list of prices_by_date by ticker
def get_ticker(record):
    return record['ticker']

for date in prices_by_date:
    prices_by_date[date] = sorted(prices_by_date[date], key=get_ticker)

# same using lambda
for date in prices_by_date:
    prices_by_date[date] = sorted(prices_by_date[date], key=lambda x: x['ticker'])

# sort the inner list of prices_by_ticker by date
def get_date(record):
    return record['date']

for tic in prices_by_tic:
    prices_by_tic[tic] = sorted(prices_by_tic[tic], key=get_date)

# same using lambda
for tic in prices_by_tic:
    prices_by_tic[tic] = sorted(prices_by_tic[tic], key=lambda x: x['date'])

# Write ticker-keyed output
with open('classes/04-06 M/data/system/prices_tickers.json', 'w') as f:
    json.dump(prices_by_tic, f, indent=2)

# Write date-keyed output
with open('classes/04-06 M/data/system/prices_dates.json', 'w') as f:
    json.dump(prices_by_date, f, indent=2)

