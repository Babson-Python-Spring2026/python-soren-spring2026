from fractions import Fraction
import json

splits_by_date = {}
splits_by_tic = {}

with open('classes/04-06 M/data/source/portfolio_splits_true_splits_only_20260331b.csv', 'r') as f:

    next(f)  # skip header line

    for line in f:
        date, ticker, split_str = line.strip().split(',')

        split_factor = Fraction(split_str)
        shares_in = split_factor.denominator
        shares_out = split_factor.numerator

        splits_by_date.setdefault(date, []).append({
            'ticker': ticker,
            'shares_in': shares_in,
            'shares_out': shares_out
        })

        splits_by_tic.setdefault(ticker, []).append({
            'date': date,
            'shares_in': shares_in,
            'shares_out': shares_out
        })

with open('classes/04-06 M/data/system/splits_ticker.json', 'w') as f:
    json.dump(splits_by_tic, f, indent=2)

with open('classes/04-06 M/data/system/splits_dates.json', 'w') as f:
    json.dump(splits_by_tic, f, indent=2)