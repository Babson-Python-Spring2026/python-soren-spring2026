cash = 10000
positions = {"AAPL": 10, "MSFT": 5}
prices = {"AAPL": 190, "MSFT": 420}

port = {}


ticker = "AAPL"
shares_to_buy = 3
cost = prices[ticker] * shares_to_buy

if cost <= (cash - 200):
    cash -= cost
    positions[ticker] += shares_to_buy

def buy_stock(port):
    sys = input("Enter ticker for stock to buy: ")
    txt = "Enter ticker for stock to buy: "
    while True:
        try:
            shares = int(input(txt))
            break
        except ValueError:
            txt = "You must enter an integer"
    while True:
        try:
            price = float(input(txt))
            break
        except ValueError:
            txt = "You must enter a float"
    if shares * price > port['cash']:
        print('insufficient funds')
        return None
    else:
        new_position = {'sys': sym,}
