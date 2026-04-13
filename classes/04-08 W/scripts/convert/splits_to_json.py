from fractions import Fraction
import json

# Dictionary keyed by date:
#   date -> list of split records for that date
splits_by_date = {}


# Open CSV file
with open('classes/04-06 M/data/source/portfolio_splits_true_splits_only_20260331b.csv', 'r') as f:
    
    next(f)  # skip header line

    for line in f:
        # Remove newline and split into fields
        tokens = line.strip().split(',')

        date = tokens[0]
        ticker = tokens[1]
        split_str = tokens[2]

        # Convert split factor to exact rational number
        # Example: "1.5" -> Fraction(3, 2)
        split_factor = Fraction(split_str)

        # Interpretation:
        # input 'shares_in' -> receive 'shares_out'
        new_split = {
            'ticker': ticker,
            'shares_in':  split_factor.denominator,
            'shares_out': split_factor.numerator
        }

        # Initialize list for date if needed
        if date not in splits_by_date:
            splits_by_date[date] = []

        # Append this split record
        splits_by_date[date].append(new_split)


with open('classes/04-06 M/data/system/splits_dates.json', 'w') as f:
    json.dump(splits_by_date, f, indent=2)


# Dictionary keyed by ticker:
# ticker -> list of split records for that ticker
splits_by_tic = {}

# Open CSV file
with open('classes/04-06 M/data/source/portfolio_splits_true_splits_only_20260331b.csv', 'r') as f:
    
    next(f)  # skip header line

    for line in f:
        # Remove newline and split into fields
        tokens = line.strip().split(',')

        date = tokens[0]
        ticker = tokens[1]
        split_str = tokens[2]

        # Convert split factor to exact rational number
        # Example: "1.5" -> Fraction(3, 2)
        split_factor = Fraction(split_str)

        # Interpretation:
        # input 'shares_in' -> receive 'shares_out'
        new_split = {
            'date': date,
            'shares_in':  split_factor.denominator,
            'shares_out': split_factor.numerator
        }

        # Initialize list for ticker if needed
        if ticker not in splits_by_tic:
            splits_by_tic[ticker] = []

        # Append this split record
        splits_by_tic[ticker].append(new_split)

with open('classes/04-06 M/data/system/splits_ticker.json', 'w') as f:
    json.dump(splits_by_tic, f, indent=2)



        
        
