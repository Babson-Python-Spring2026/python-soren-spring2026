import csv
import json
from collections import defaultdict

data = defaultdict(list)

with open(r"C:\PythonClass\student_repo\classes\04-01 W\data\source\sp100_dividends.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data[row["Ticker"]].append({
            "date": row["Date"],
            "dividend": float(row["Dividend"])
        })

with open(r"C:\PythonClass\student_repo\classes\04-06 M\scripts\convert\sp100_dividends_by_ticker.json", "w", encoding="utf-8") as f:
    json.dump(dict(data), f, indent=2)

print("Done")

data = defaultdict(list)

with open(r"C:\PythonClass\student_repo\classes\04-01 W\data\source\sp100_dividends.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data[row["Date"]].append({
            "ticker": row["Ticker"],
            "dividend": float(row["Dividend"])
        })

with open(r"C:\PythonClass\student_repo\classes\04-06 M\scripts\convert\sp100_dividends_by_date.json", "w", encoding="utf-8") as f:
    json.dump(dict(data), f, indent=2)

print("Done")