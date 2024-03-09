import time

from src.market_data.instrument import TastytradeInstruments
from src.trading.order import TastytradeOrder

class Trader:
	def __init__(self, session_token, api_url, account_number):
		self.session_token = session_token
		self.api_url = api_url
		self.account_number = account_number
		self.order_client = TastytradeOrder(session_token)
		self.instrument_client = TastytradeInstruments(session_token, api_url)

	def simple_trading_algo(self, symbol, quantity):
		prev_price = None
		while True:
			# Get the latest price of the instrument
			instrument_data = self.instrument_client.get_symbol_data(symbol)
			current_price = instrument_data[0]["last"]

			if prev_price is not None:
				if current_price > prev_price:
					# Market went up, place a buy order
					buy_order = {
						"orderType": "Market",
						"timeInForce": "Day",
						"legs": [
							{
								"instrumentType": "Equity",
								"symbol": symbol,
								"action": "Buy",
								"quantity": quantity
							}
						]
					}
					self.order_client.create_order(self.account_number, buy_order)
					print(f"Placed a buy order for {quantity} shares of {symbol} at {current_price}")

				elif current_price < prev_price:
					# Market went down, place a sell order
					sell_order = {
						"orderType": "Market",
						"timeInForce": "Day",
						"legs": [
							{
								"instrumentType": "Equity",
								"symbol": symbol,
								"action": "Sell",
								"quantity": quantity
							}
						]
					}
					self.order_client.create_order(self.account_number, sell_order)
					print(f"Placed a sell order for {quantity} shares of {symbol} at {current_price}")

			prev_price = current_price
			time.sleep(60)  # Check the market condition every minute

	def place_market_buy_order(self, symbol, quantity):
		# Place a market buy order
		buy_order = {
			"orderType": "Market",
			"timeInForce": "Day",
			"legs": [
				{
					"instrumentType": "Equity",
					"symbol": symbol,
					"action": "Buy",
					"quantity": quantity
				}
			]
		}
		self.order_client.create_order(self.account_number, buy_order)
		print(f"Placed a market buy order for {quantity} shares of {symbol}")