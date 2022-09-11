import requests
import json
import pandas as pd
import numpy as np

def get_markets():
    response_API = requests.get('https://www.predictit.org/api/marketdata/all/')
    data = json.loads(response_API.text)
    
    markets = []
    
    for market in data["markets"]:
        # make sure that all no contracts are open
        # flag this market and skip
        for contract in market["contracts"]:
            if contract["status"] != "Open":
                print("Found a market with contracts not open, check it out")
                print(market)
                continue
        
        contracts_prices = [share["bestBuyNoCost"] for share in market["contracts"] if share["bestBuyNoCost"] is not None]
        
        new_market = {
            "name": market["name"],
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


def get_profits(prices, quantities):
    profits = []

    for i in range(len(prices)):
        profit = 0
        for j in range(len(prices)):
            if i == j:
                term = -quantities[i] * prices[i]
            else:
                term = quantities[j] * 0.9 * (1 - prices[j])
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
                matrix_row[j] = 0.9 * (1 - prices[j])
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