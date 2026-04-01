from pprint import pprint as pp
dates = []
with open('classes\03-30 M\sp100_daily_prices.csv', 'r') as f:
    f.readline()
    for line in f:
        line = line.split(',')
        if line[0] not in dates:
            dates.append(line[0])

print(len(dates))

dates.sort()
pp(dates)