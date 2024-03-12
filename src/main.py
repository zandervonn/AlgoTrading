from src.accounts.account_handler import *
from src.accounts.balances_positions import TastytradeAccountPositions
from src.authentication import TastytradeAuth
from gitignore.access import *
from src.helpers.helpers import *
from src.symbology import to_tastytrade_option_symbol
from src.trading.DiagonalSpreadTrader import DiagonalSpreadTrader
from src.trading.simple_verticle_trade import VerticalSpreadTrader
from src.trading.trading_main import *
import pandas as pd


#todo printing error on 201 reply
def init_account(session_token):
	account = TastytradeAccount(session_token, api_url())
	accounts = account.get_customer()
	print(accounts)

def get_first_account_number(session_token):
	account = TastytradeAccount(session_token, api_url())
	accounts = account.get_accounts()
	if accounts:
		first_account = accounts[0]
		return first_account["account-number"]
	else:
		print("No accounts found")
		return None

def test_hours():
	market_hours = MarketHours()

	current_time = pd.Timestamp.now(pytz.timezone('US/Eastern'))
	print("Current Time:", current_time)
	print("Is Market Open:", market_hours.is_market_open(current_time))
	print("Time Until Open:", market_hours.time_until_open(current_time))
	print("Is Holiday:", market_hours.is_holiday(current_time))
	print("Next Holiday:", market_hours.next_holiday(current_time))
	print("List of Holidays:", market_hours.list_holidays())

def test():
	session_token = TastytradeAuth(username(), password()).get_session()
	headers = {"Authorization": f"{session_token}"}
	# response = requests.get(f"{api_url()}/instruments/cryptocurrencies/BTC%2FUSD", headers=headers) # working
	# response = requests.get(f"{api_url()}/instruments/equities/", headers=headers) # working
	response = requests.get(f"{api_url()}/option-chains/XBI", headers=headers) # working
	# response = requests.get(f"{api_url()}/accounts/{account_number()}/trading-status", headers=headers) # working
	# response = requests.get(f"{api_url()}/accounts/{account_number()}/positions", headers=headers)

	with open('data.txt', 'w') as file:
		json.dump(response.text, file, indent=4)

	print(session_token)
	print(response.request.url)
	print(response)
	print(response.text)
	print(response.status_code)

def get_orders():
	session_token = TastytradeAuth(username(), password()).get_session()
	positions = TastytradeAccountPositions(session_token, api_url())
	orders = TastytradeOrder(session_token, api_url())

	print("Balances: ", json.dumps(positions.get_account_balances(account_number()), indent=4))
	print("Positions: ", json.dumps(positions.get_positions(account_number()), indent=4))
	print("Orders: ", json.dumps(orders.get_orders(account_number()), indent=4))

	return positions


def make_simple_order():
	session_token = TastytradeAuth(username(), password()).get_session()
	buy_order = {
		"time-in-force": "GTC",
		"order-type": "Stop",
		"stop-trigger": 105,
		"legs": [
			{
				"instrument-type": "Equity",
				"symbol": "AAPL",
				"quantity": 1,
				"action": "Sell to Close"
			}
		]
	}


def test_symbols():
	symbol = 'XBI'
	session_token = TastytradeAuth(username(), password()).get_session()
	# instrument = TastytradeInstruments(session_token, api_url())
	apple = to_tastytrade_option_symbol(symbol, 170, "C", "2024-03-15")
	# optionsAppl = instrument.get_equity_options(symbols=apple)
	# print(optionsAppl)

def make_vertical_order():
	# Authenticate and get session token
	session_token = TastytradeAuth(username(), password()).get_session()

	trader = Trader(session_token, api_url(), account_number())

	# Set up and run VerticalSpreadTrader
	symbol = "AAPL"
	days_to_expiration = 45
	sell_strike = 155
	buy_strike = 150
	quantity = 1
	price = 0.25
	vertical_spread_trader = VerticalSpreadTrader(trader, symbol, days_to_expiration, sell_strike, buy_strike, quantity, price)
	vertical_spread_trader.run()


def make_vertical_SPX_order():
	# Authenticate and get session token
	session_token = TastytradeAuth(username(), password()).get_session()

	trader = Trader(session_token, api_url(), account_number())

	# Set up and run VerticalSpreadTrader
	symbol = "AAPL"
	days_to_expiration = 45
	sell_strike = 155
	buy_strike = 150
	quantity = 1
	price = 0.25
	vertical_spread_trader = VerticalSpreadTrader(trader, symbol, days_to_expiration, sell_strike, buy_strike, quantity, price)
	vertical_spread_trader.run()



def make_diagonal_order():
	# Authenticate and get session token
	session_token = TastytradeAuth(username(), password()).get_session()

	trader = Trader(session_token, api_url(), account_number())

	# Set up and run
	symbol = "AAPL"
	long_days_to_expiration = 0
	short_days_to_expiration = 30
	long_strike = 150
	short_strike = 155
	quantity = 1
	price = 2.45
	diagonal_spread_trader = DiagonalSpreadTrader(trader, symbol, long_days_to_expiration, short_days_to_expiration, long_strike, short_strike, quantity, price)
	diagonal_spread_trader.run()


def main():

	# make_diagonal_order()
	make_vertical_order()
	# get_orders()
	# test()

if __name__ == '__main__':
	main()
