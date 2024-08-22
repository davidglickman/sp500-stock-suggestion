# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 15:30:57 2024

@author: glick
"""

import yfinance as yf
import pandas as pd
import numpy as np

def fetch_stock_data(ticker, period='6mo'):
    """
    Fetch historical data for a given stock.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

def calculate_indicators(data):
    """
    Calculate indicators like 20-day and 50-day moving averages, RSI, and MACD.
    """
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    
    # RSI calculation
    delta = data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD calculation
    data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    return data

def scan_for_rising_stocks(tickers, period='6mo'):
    """
    Scan a list of stocks to find those likely to rise based on technical indicators.
    """
    rising_stocks = []

    for ticker in tickers:
        data = fetch_stock_data(ticker, period)
        data = calculate_indicators(data)
        
        # Criteria for rising stocks
        # 1. Price crosses above 20-day moving average
        # 2. MACD line is above the Signal line
        # 3. RSI is below 70 (not overbought)
        
        if data['Close'].iloc[-1] > data['MA20'].iloc[-1] and \
           data['MACD'].iloc[-1] > data['Signal_Line'].iloc[-1] and \
           data['RSI'].iloc[-1] < 70:
            rising_stocks.append(ticker)
            print (ticker)
        else:
            print ("No rising")
    
    return rising_stocks

def get_sp500_tickers():
    # Get the S&P 500 tickers
    sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    tickers = sp500_tickers['Symbol'].tolist()
    
    # Clean up tickers (in case there are any special cases like BRK.B)
    tickers = [ticker.replace('.', '-') for ticker in tickers]
    
    return tickers

# Get the list of S&P 500 tickers
sp500_tickers = get_sp500_tickers()

#tickers = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN']
rising_stocks = scan_for_rising_stocks(sp500_tickers)
print(f"Stocks likely to rise: {rising_stocks}")