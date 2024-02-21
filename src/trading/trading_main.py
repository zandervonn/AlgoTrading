import time

# Authentication and initialization
from src.authentication import TastytradeAuth
from src.market_data.instrument import TastytradeInstruments
from src.trading.order import TastytradeOrder


#


# Simple trading algorithm
def simple_trading_algo(symbol, quantity, account_number, session_token, api_url):

	order_client = TastytradeOrder(session_token)
	instrument_client = TastytradeInstruments(session_token, api_url)

	prev_price = None

	while True:
		# Get the latest price of the instrument
		instrument_data = instrument_client.get_symbol_data(symbol)
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
				order_client.create_order(account_number, buy_order)
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
				order_client.create_order(account_number, sell_order)
				print(f"Placed a sell order for {quantity} shares of {symbol} at {current_price}")

		prev_price = current_price
		time.sleep(60)  # Check the market condition every minute

# Example usage
simple_trading_algo(symbol="AAPL", quantity=10)
