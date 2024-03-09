import time
from datetime import datetime

import pandas as pd
import pytz

from src.helpers.helpers import MarketHours


class SimpleOpenTradingAlgo:
	def __init__(self, trader, symbols, quantity):
		self.trader = trader
		self.symbols = symbols
		self.quantity = quantity
		self.purchase_prices = {}

	def run(self):
		# Wait for market open
		self.wait_for_market_open()
		# Buy the stocks
		self.buy_stocks()
		# Monitor and sell when profitable
		self.monitor_and_sell()

	def wait_for_market_open(self):
		print("Waiting for market to open")
		market_hours = MarketHours()
		market_open_time = datetime.now(pytz.timezone('US/Eastern')).replace(hour=9, minute=30, second=0, microsecond=0)
		while datetime.now(pytz.timezone('US/Eastern')) < market_open_time:
			current_time = pd.Timestamp.now(pytz.timezone('US/Eastern'))
			print("time unitl open: ", market_hours.time_until_open(current_time))
			time.sleep(5)  # Check every minute # todo change back to 60
		print("Market is open!")

	def buy_stocks(self):
		for symbol in self.symbols:
			order = {
				"orderType": "Market",
				"timeInForce": "Day",
				"legs": [
					{
						"instrumentType": "Equity",
						"symbol": symbol,
						"action": "Buy",
						"quantity": self.quantity
					}
				]
			}
			response = self.trader.order_client.create_order(self.trader.account_number, order)
			self.purchase_prices[symbol] = response["price"]
			print(f"Bought {self.quantity} shares of {symbol} at {response['price']}")

	def monitor_and_sell(self):
		while self.purchase_prices:
			for symbol in list(self.purchase_prices.keys()):
				current_price = self.trader.instrument_client.get_symbol_data(symbol)[0]["last"]
				if current_price > self.purchase_prices[symbol]:
					order = {
						"orderType": "Market",
						"timeInForce": "Day",
						"legs": [
							{
								"instrumentType": "Equity",
								"symbol": symbol,
								"action": "Sell",
								"quantity": self.quantity
							}
						]
					}
					self.trader.order_client.create_order(self.trader.account_number, order)
					print(f"Sold {self.quantity} shares of {symbol} at {current_price}")
					del self.purchase_prices[symbol]
			time.sleep(60)  # Check every minute