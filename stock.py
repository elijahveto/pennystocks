import os
import requests
from date import yesterday
import time


# def api_limit(function):
#     def wrapper(*args, **kwargs):
#         time.sleep(51)
#         return function(*args, **kwargs)
#     return wrapper

class Stock:
    def __init__(self):
        self.api_key = os.environ.get('alpha_premium_key_new')
        self.url = 'https://www.alphavantage.co/query'

    # @api_limit
    def log_price(self, ticker):
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': ticker,
            'apikey': self.api_key,
        }
        try:
            response = requests.get(self.url, params=params).json()
            stock_price = response['Time Series (Daily)'][str(yesterday())]['4. close']
        except KeyError:
            return ''
        else:
            return stock_price

    #@api_limit
    def description(self, ticker):
        ticker = ticker
        params = {
            'function': 'OVERVIEW',
            'symbol': ticker,
            'apikey': self.api_key,
        }
        try:
            response = requests.get(self.url, params=params).json()
            description = response['Description']
        except KeyError:
            print(response)
        else:
            return description

    #@api_limit
    def sector(self, ticker):
        ticker = ticker
        params = {
            'function': 'OVERVIEW',
            'symbol': ticker,
            'apikey': self.api_key,
        }
        try:
            response = requests.get(self.url, params=params).json()
            sector = response['Sector']
        except KeyError:
            print(response)
        else:
            return sector

    #@api_limit
    def get_quote(self, ticker, date):
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': ticker,
            'apikey': self.api_key,
        }
        try:
            response = requests.get(self.url, params=params).json()
            stock_price = response['Time Series (Daily)']
        except KeyError:
            print(response)
        else:
            try:
                stock_price = response['Time Series (Daily)'][str(date)]['4. close']
                return float(stock_price)
            except KeyError:
                for key in response['Time Series (Daily)']:
                    last = key
                    break
                print(f'no data for {ticker}, last available {last}, but date given {date}')
                return 'no data'