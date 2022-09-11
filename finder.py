from audioop import mul
import requests
import json
import pandas as pd
import numpy as np
import math

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

#print(get_profits([0.53, 0.66, 0.75, 0.97], [12, 12, 12, 10]))
#print(get_optimal_ratio([0.53, 0.66, 0.75, 0.97]))
#print(min_quantity_for_profit([0.53, 0.66, 0.75, 0.97], [1, 0.98654244, 0.9774359, 0.9558676]))