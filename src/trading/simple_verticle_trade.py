import datetime

from src.market_data.instrument import TastytradeInstruments
from src.trading.order import TastytradeOrder
from src.symbology import to_tastytrade_option_symbol


class VerticalSpreadTrader:
	def __init__(self, trader, symbol, days_to_expiration, sell_strike, buy_strike, quantity, price):
		self.trader = trader
		self.symbol = symbol
		self.days_to_expiration = days_to_expiration
		self.sell_strike = sell_strike
		self.buy_strike = buy_strike
		self.quantity = quantity
		self.price = price

	def find_option_by_strike(self, options, target_strike):
		# Find the option with a strike price closest to the target strike
		closest_option = min(options, key=lambda x: abs(float(x['strike-price']) - target_strike))
		return closest_option

	def run(self):
		# Get option chains
		instrument = TastytradeInstruments(self.trader.session_token, self.trader.api_url)
		option_chain_data = instrument.get_option_chains(self.symbol)
		# print("Option chain data:", option_chain_data)

		# Flatten the list of expirations and strikes
		flat_options = []
		for option_data in option_chain_data:
			for expiration_group in option_data['expirations']:
				for strike in expiration_group['strikes']:
					strike['expiration-date'] = expiration_group['expiration-date']
					flat_options.append(strike)
		# print("Flat options:", flat_options)

		# Find the closest expiration date to the target date
		target_date = datetime.datetime.now() + datetime.timedelta(days=self.days_to_expiration)
		closest_expiration_date = min(flat_options, key=lambda x: abs(datetime.datetime.strptime(x['expiration-date'], "%Y-%m-%d") - target_date))['expiration-date']
		print("Closest expiration date:", closest_expiration_date)

		# Filter options by the closest expiration date
		options_near_expiration = [option for option in flat_options if option['expiration-date'] == closest_expiration_date]
		print("Options near expiration:", options_near_expiration)

		# Filter for call options
		call_options = [option for option in options_near_expiration if 'call' in option]
		print("Call options:", call_options)

		# Find options for the spread
		sell_option = self.find_option_by_strike(call_options, self.sell_strike)
		buy_option = self.find_option_by_strike(call_options, self.buy_strike)
		print("Sell option:", sell_option)
		print("Buy option:", buy_option)

		sell_option_symbol = sell_option['call']
		buy_option_symbol = buy_option['call']

		# Construct the order details
		order = {
			"time-in-force": "GTC",
			"order-type": "Limit",
			"price": self.price,
			"price-effect": "Debit",
			"legs": [
				{
					"instrument-type": "Equity Option",
					"symbol": sell_option_symbol,
					"quantity": self.quantity,
					"action": "Sell to Open"
				},
				{
					"instrument-type": "Equity Option",
					"symbol": buy_option_symbol,
					"quantity": self.quantity,
					"action": "Buy to Open"
				}
			]
		}
		print("Order details:", order)

		# Place the order
		order_client = TastytradeOrder(self.trader.session_token, self.trader.api_url)
		order_response = order_client.create_order(self.trader.account_number, order)
		print("Order response:", order_response)
