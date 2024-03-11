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
