from src.accounts.account_handler import *
from src.authentication import *
from src.gitignore.access import *
from src.symbology import *
from src.trading.trading_main import simple_trading_algo

def init_account(auth):
	# Log in to the API
	auth_data = auth.login()
	print("Session token:", auth.session_token)

	account = TastytradeAccount(auth.session_token, api_url())
	accounts = account.get_accounts()

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
	simple_trading_algo("AAPL", 10, account_number(), auth.session_token, api_url())

def main():
	auth = TastytradeAuth(username(), password())
	get_first_account_number(auth)
	setup_trading(auth)


if __name__ == '__main__':
	main()