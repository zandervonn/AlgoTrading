import logging

from src.accounts.account_handler import *
from src.accounts.balances_positions import TastytradeAccountPositions
from src.authentication import TastytradeAuth
from gitignore.access import *
from src.helpers.helpers import *
from src.symbology import to_tastytrade_option_symbol
from src.trading.simple_verticle_trade import VerticalSpreadTrader
from src.trading.tradeOpenAlgo import SimpleOpenTradingAlgo
from src.trading.trading_main import *
import pandas as pd


#todo printing error on 201 reply

def init_account(auth):
	# Log in to the API
	auth.login()
	print("Session token:", auth.session_token)

	account = TastytradeAccount(auth.session_token, api_url())
	# accounts = account.get_accounts()
	accounts = account.get_customer()
	accounts = get_positions(account_number(), api_url(), auth.session_token)
	print(accounts)

def get_first_account_number(auth):
	account = TastytradeAccount(auth.session_token, api_url())
	accounts = account.get_accounts()
	if accounts:
		first_account = accounts[0]
		return first_account["account-number"]
	else:
		print("No accounts found")
		return None

def setup_trading(auth):
	trader = Trader(auth.session_token, api_url(), account_number)
	Trader.place_market_buy_order(trader, "APPL", 1)

def setup_trading_open(auth):
	trader = Trader(auth.session_token, api_url(), account_number())
	algo = SimpleOpenTradingAlgo(trader, ["AAPL", "MSFT", "GOOGL"], 10)
	algo.run()

def test_hours():
	market_hours = MarketHours()

	current_time = pd.Timestamp.now(pytz.timezone('US/Eastern'))
	print("Current Time:", current_time)
	print("Is Market Open:", market_hours.is_market_open(current_time))
	print("Time Until Open:", market_hours.time_until_open(current_time))
	print("Is Holiday:", market_hours.is_holiday(current_time))
	print("Next Holiday:", market_hours.next_holiday(current_time))
	print("List of Holidays:", market_hours.list_holidays())

def simple_verticle_trade(session_token):
	trader = Trader(session_token, api_url(), account_number())
	vertical_spread_trader = VerticalSpreadTrader(
		trader=trader,
		symbol="APP",
		days_to_expiration=45,
		sell_delta=16,
		buy_delta=10,
		quantity=1,
		price=26
	)
	vertical_spread_trader.run()

def test():
	session_token = TastytradeAuth(username(), password()).get_session()
	headers = {"Authorization": f"{session_token}"}
	# response = requests.get(f"{api_url()}/instruments/cryptocurrencies/BTC%2FUSD", headers=headers) # working
	# response = requests.get(f"{api_url()}/instruments/equities/", headers=headers) # working
	# response = requests.get(f"{api_url()}/option-chains/GOOG", headers=headers) # working
	# response = requests.get(f"{api_url()}/accounts/{account_number()}/trading-status", headers=headers) # working
	response = requests.get(f"{api_url()}/accounts/{account_number()}/positions", headers=headers)

	with open('data.txt', 'w') as file:
		json.dump(response.text, file)

	print(session_token)
	print(response.request.url)
	print(response)
	print(response.text)
	# print(response.json())
	print(response.status_code)

def get_orders():
	session_token = TastytradeAuth(username(), password()).get_session()
	positions = TastytradeAccountPositions(session_token, api_url())
	orders = TastytradeOrder(session_token, api_url())

	print("Balances: ", json.dumps(positions.get_account_balances(account_number()), indent=4))
	print("Positions: ", json.dumps(positions.get_positions(account_number()), indent=4))
	print("Orders: ", json.dumps(orders.get_orders(account_number()), indent=4))

	return positions

def make_order():
	session_token = TastytradeAuth(username(), password()).get_session()
	simple_verticle_trade(session_token)


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
	logging.basicConfig(level=logging.DEBUG)
	TastytradeOrder(session_token, api_url()).create_order(account_number(), buy_order)

def main():

	# test_hours()
	# test()
	# get_orders()
	make_order()
	# make_simple_order()



if __name__ == '__main__':
	main()
