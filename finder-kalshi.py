from KalshiClientsBase import ExchangeClient, KalshiClient
import numpy as np


def get_markets():
    client = ExchangeClient("https://trading-api.kalshi.com", "additionaldark@gmail.com", "Okboomer#123")

    markets = client.get_public_markets()

    markets = markets["markets"]
    markets = [m for m in markets if m["status"] == "active"]

    market_groups = {}

    for market in markets:
        group_ticker = market["ranged_group_ticker"]
        if group_ticker not in market_groups:
            market_groups[group_ticker] = []
            
        market_groups[group_ticker].append(market)
        
        if market["ticker_name"] == "INXW-22SEP16-B3925":
            print(market)
        elif market["ticker_name"] == "FRM-22SEP15-T5.80":
            print(market)
            
        elif market["ticker_name"] == "SFFA-COMPLETE":
            print(market)
        
        # print(market["rulebook_variables"])
        
        # print(client.get_ranged_market_by_ticker(group_ticker))


    markets = []
    for ticker in market_groups:
        title = market_groups[ticker][0]["title"]
        contracts_prices = [(1 - market["yes_bid"]/100) for market in market_groups[ticker]]
        
        new_market = {
            "name": ticker,
            "contracts_prices": contracts_prices
        }
        
        markets.append(new_market)
    return markets

def check_arb(markets):
    # A market is arb-able if min(profit_1, profit_2, ...) > 0
    for market in markets:
        # market["contracts_prices"] = [0.53, 0.66, 0.75, 0.97]
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
    # This works but does not ACTUALLY return the lowest
    # quantity for now. It gets close though.
    
    # Maybe just ask my Lin Alg TA on how to solve such that
    # output b specifies positive
    
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