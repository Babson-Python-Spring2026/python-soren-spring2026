import pandas as pd
import json

# Load CSV
df = pd.read_csv("pricing.csv", parse_dates=["Date"])

# Extract, deduplicate, sort
dates = (
    df["Date"]
    .dropna()
    .dt.strftime("%Y-%m-%d")
    .unique()
)

sorted_dates = sorted(dates)

# Write to JSON
with open("mkt_dates.json", "w") as f:
    json.dump(sorted_dates, f, indent=2)