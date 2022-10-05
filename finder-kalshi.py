from KalshiClientsBase import ExchangeClient, KalshiClient
import numpy as np
import config

def get_markets():
    client = ExchangeClient("https://trading-api.kalshi.com", config.email, 
config.password)

    events = client.get_events_cached()
    events = events["events"]
    
    processed_markets = []
    for event in events:
        if (all([(m["status"] != "active") for m in event["markets"]])):
            continue
        markets = [m for m in event["markets"] if m["status"] == "active"]
        contracts_prices = [(1 - market["yes_bid"]/100) for market in markets]
        
        new_market = {
            "name": event["ticker"],
            "mutually_exclusive": event["mutually_exclusive"],
            "contracts_prices": contracts_prices
        }
        
        processed_markets.append(new_market)
    return processed_markets

def check_arb(markets):
    # A market is arb-able if min(profit_1, profit_2, ...) > 0
    for market in markets:
        if not market["mutually_exclusive"]:
            # print(f'{ market["name"] } is not mutually exclusive.')
            continue
        
        contracts_prices = market["contracts_prices"]

        if(len(contracts_prices) == 0):
            continue

        ratio = get_optimal_ratio(contracts_prices)
        
        profits = get_profits(contracts_prices, ratio)
        
        if min(profits) > 0:
            print("=========================")
            print(f'Name: {market["name"]}')
            print(f'Prices: {contracts_prices}')
            print(f'Optimal ratio: {ratio}')
            print(f'Profits at optimal ratio: {profits}')

            # Find the minimum quantities of each contract that needs to be bought
            # to make a profit
            min_quantities = min_quantity_for_profit(contracts_prices, ratio)
            print(f'Minimum quantities to buy: {min_quantities}')
            print(f'Min profit at the minimum quantities: {min(get_profits(contracts_prices, min_quantities))}')
        
def min_quantity_for_profit(prices, ratio):
    multiplier = 1
    while(
        not min(get_profits(prices, [round(n * multiplier) for n in ratio])) > 0
    ):
        multiplier += 1
    return [round(n * multiplier) for n in ratio]

def get_profits(prices, quantities):
    profits = []

    for i in range(len(prices)):
        profit = 0
        for j in range(len(prices)):
            if i == j:
                term = -quantities[i] * prices[i]
            else:
                term = quantities[j] * 0.93 * (1 - prices[j])
            profit += term
        profits.append(profit)
            
    return profits
        
def get_optimal_ratio(prices):
    coefficient_matrix = []
    for i in range(len(prices)):
        matrix_row = [0] * len(prices)
        for j in range(len(prices)):
            if j == i:
                matrix_row[j] = -(prices[i])
            else:
                matrix_row[j] = 0.93 * (1 - prices[j])
        coefficient_matrix.append(matrix_row)
    A = np.array(coefficient_matrix)
    b = np.ones((len(prices)))
    x = np.linalg.solve(A, b)
    # make largest value in x --> 1
    x = x / x.max()
    return x

def run():
    markets = get_markets()
    arbritragable_markets = check_arb(markets)
    
run()
