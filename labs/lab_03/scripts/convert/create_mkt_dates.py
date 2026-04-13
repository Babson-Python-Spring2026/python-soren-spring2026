import json

mkt_dates = []
with open('classes/04-01 W/data/source/portfolio_prices_raw_and_split_adjusted_20260331b.csv', 'r') as f:
    next(f)
    for line in f:
        tokens = line.strip().split(',')
        if tokens[0] not in mkt_dates:
            mkt_dates.append(tokens[0])

    mkt_dates.sort()

with open('classes/04-01 W/data/system/mkt_dates.json', 'w') as f:
    json.dump(mkt_dates, f, indent=2)

#version 2

mkt_dates = set()
with open('classes/04-01 W/data/source/portfolio_prices_raw_and_split_adjusted_20260331b.csv', 'r') as f:
    next(f)
    for line in f:
        tokens = line.strip().split(',')        
        mkt_dates.add(tokens[0])

    mkt_dates = sorted(list(mkt_dates))

with open('classes/04-01 W/data/system/mkt_dates2.json', 'w') as f:
    json.dump(mkt_dates, f, indent=2)

#which version is better ?