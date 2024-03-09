from flask import json

from src.market_data.market_metrics import MarketMetrics


def get_market_metrics(session_token, api_url):
	market_metrics = MarketMetrics(session_token, api_url)
	symbols = ["AAPL", "FB", "BRK/B"]
	try:
		metrics_data = market_metrics.get_metrics(symbols)
		print('Metrics data:', json.dumps(metrics_data, indent=4))

	except Exception as e:
		print(str(e))

def get_dividends(session_token, api_url):

	market_metrics = MarketMetrics(session_token, api_url)

	# ----  Get dividend data
	symbol = "AAPL"
	try:
		dividend_data = market_metrics.get_dividend_data(symbol)
		print('Dividend data:', json.dumps(dividend_data, indent=4))
	except Exception as e:
		print(str(e))

def get_earnings(session_token, api_url):

	market_metrics = MarketMetrics(session_token, api_url)

	symbol = "AAPL"
	start_date = "2020-01-01"
	try:
		earnings_data = market_metrics.get_earnings_data(symbol, start_date)
		print('Earnings data:', json.dumps(earnings_data, indent=4))
	except Exception as e:
		print(str(e))