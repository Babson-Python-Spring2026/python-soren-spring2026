from pprint import pprint as pp
import json
market_dates = []
with open('sp100_daily_prices.csv', 'r',) as f:
    f.readline()
    for line in f:        
        line = line.split(',')
        if line[0] not in market_dates:
            market_dates.append(line[0])

market_dates.sort()

pp({'count':len(market_dates),'dates':market_dates})

with open('market_dates.json', 'w') as f:
    json.dump(market_dates, f, indent = 2)