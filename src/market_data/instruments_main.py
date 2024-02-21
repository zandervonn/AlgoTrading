from flask import json

from src.symbology import to_tastytrade_option_symbol
from src.market_data.instrument import TastytradeInstruments

def get_equities(session_token, api_url):
	instrument = TastytradeInstruments(session_token, api_url)
	crypto = instrument.get_cryptocurrencies(["BTC/USD", "SOL/USD"])
	print('Cryptos:', json.dumps(crypto, indent=4))

	crypto_by_symbol = instrument.get_cryptocurrency_by_symbol("BTC%2FUSD")
	print('Crypto by symbol:', json.dumps(crypto_by_symbol, indent=4))

	active_equities = instrument.get_active_equities()
	print('Active equities:', json.dumps(active_equities, indent=4))

	#Get_Equities implements /instruments/equities/ endpoint, when passing list of symbols
	# equities = instrument.get_equities(symbols=["AAPL", "MSFT", "SPY"])
	#Get_Equities implements /instruments/equities/{symbol} endpoint, when passing one symbol
	# equities = instrument.get_equities("TSLA")
	# equities = instrument.get_equities(lendability="Easy To Borrow")
	equities = instrument.get_equities(is_etf=True)
	print('Equities:', json.dumps(equities, indent=4))

def get_symbol_options(symbol, session_token, api_url):
	instrument = TastytradeInstruments(session_token, api_url)
	apple = to_tastytrade_option_symbol(symbol, 170, "C", "2024-03-15")
	optionsAppl = instrument.get_equity_options(symbols=apple)
	print(optionsAppl)

def get_futures(session_token, api_url):

	# Get_Futures implements /instruments/futures/ endpoint, when passing list of symbols or one symbol
	instrument = TastytradeInstruments(session_token, api_url)

	# futuresCL = instrument.get_futures(symbols=["/CLU3", "/CLV3"])
	# futuresCL = instrument.get_futures(symbols="/CLU3")
	futuresCL = instrument.get_futures(product_codes="CL")
	print('Equities:', json.dumps(futuresCL, indent=4))

	future_options_products = instrument.get_future_option_products()
	print('Equities:', json.dumps(future_options_products, indent=4))

	future_products = instrument.get_future_products()
	print('Future products:', json.dumps(future_products, indent=4))

	quantity_decimal_precisions = instrument.get_quantity_decimal_precisions()
	print('Quantity decimal precisions:', json.dumps(quantity_decimal_precisions, indent=4))
