import datetime
import json

from src.market_data.instrument import TastytradeInstruments
from src.trading.order import TastytradeOrder


class DiagonalSpreadTrader:
	def __init__(self, trader, symbol, long_days_to_expiration, short_days_to_expiration, long_strike, short_strike, quantity, price):
		self.trader = trader
		self.symbol = symbol
		self.long_days_to_expiration = long_days_to_expiration
		self.short_days_to_expiration = short_days_to_expiration
		self.long_strike = long_strike
		self.short_strike = short_strike
		self.quantity = quantity
		self.price = price

	def find_option_by_strike_and_expiration(self, options, target_strike, target_date):
		# Find the option with a strike price and expiration date closest to the target
		closest_option = min(
			options,
			key=lambda x: abs(float(x['strike-price']) - target_strike)
			              + abs((datetime.datetime.strptime(x['expiration-date'], "%Y-%m-%d") - target_date).days)
		)
		return closest_option

	def run(self):
		# Get option chains
		instrument = TastytradeInstruments(self.trader.session_token, self.trader.api_url)
		option_chain_data = instrument.get_option_chains(self.symbol)

		# Flatten the list of expirations and strikes
		flat_options = []
		for option_data in option_chain_data:
			for expiration_group in option_data['expirations']:
				for strike in expiration_group['strikes']:
					strike['expiration-date'] = expiration_group['expiration-date']
					flat_options.append(strike)

		# Find options for the diagonal spread
		long_target_date = datetime.datetime.now() + datetime.timedelta(days=self.long_days_to_expiration)
		short_target_date = datetime.datetime.now() + datetime.timedelta(days=self.short_days_to_expiration)

		long_option = self.find_option_by_strike_and_expiration(flat_options, self.long_strike, long_target_date)
		short_option = self.find_option_by_strike_and_expiration(flat_options, self.short_strike, short_target_date)

		long_option_symbol = long_option['call']
		short_option_symbol = short_option['call']

		# Construct the order details
		order = {
			"time-in-force": "GTC",
			"order-type": "Limit",
			"price": self.price,
			"price-effect": "Debit",
			"legs": [
				{
					"instrument-type": "Equity Option",
					"symbol": long_option_symbol,
					"quantity": self.quantity,
					"action": "Buy to Open"
				},
				{
					"instrument-type": "Equity Option",
					"symbol": short_option_symbol,
					"quantity": self.quantity,
					"action": "Sell to Open"
				}
			]
		}

		# Place the order
		order_client = TastytradeOrder(self.trader.session_token, self.trader.api_url)
		order_response = order_client.create_order(self.trader.account_number, order)
		print("Order response:", json.dumps(order_response, indent=4))
		return order_response