import asyncio
import re

import websockets

from src.accounts.account_handler import *
from src.authentication import TastytradeAuth
from gitignore.access import *
from src.helpers.helpers import *
from src.streamer.tastey_web_socket import TastytradeWebsocketClient


def test():
	session_token = TastytradeAuth(username(), password()).get_session()
	headers = {"Authorization": f"{session_token}"}
	# response = requests.get(f"{api_url()}/instruments/cryptocurrencies/BTC%2FUSD", headers=headers) # working
	# response = requests.get(f"{api_url()}/instruments/equities/", headers=headers) # working
	response = requests.get(f"{api_url()}/option-chains/AAPL", headers=headers) # working
	# response = requests.get(f"{api_url()}/accounts/{account_number()}/trading-status", headers=headers) # working
	# response = requests.get(f"{api_url()}/accounts/{account_number()}/positions", headers=headers)

	with open('data.txt', 'w') as file:
		json.dump(response.text, file, indent=4)

	print(session_token)
	print(response.request.url)
	print(response)
	print(response.text)
	print(response.status_code)

data_queue = asyncio.Queue()

def main():
	# get_orders()
	# test()
	# getdxtoken()
	asyncio.run(make_vertical_SPY_order())

# data_queue = asyncio.Queue()

def getdxtoken():
	dx_token = TastytradeAuth(username(), password()).get_dxfeed_token()
	dx_token = dx_token["data"]["token"]
	print(dx_token)

async def make_vertical_SPY_order():
	# Authenticate and get session token
	options = find_options_by_expiration("AAPL", 30)
	options = [option for option in options if re.search(r'P\d+$', option)]
	print(options)
	symbol_deltas = await getDeltaSymbols(options)

	print(symbol_deltas)

	# Find the symbols closest to the target deltas
	low_delta_symbol = min(symbol_deltas, key=lambda k: abs(symbol_deltas[k] + 0.16))
	high_delta_symbol = min(symbol_deltas, key=lambda k: abs(symbol_deltas[k] - 0.20))

	print(f"Symbol closest to low delta (-0.16): {low_delta_symbol}")
	print(f"Symbol closest to high delta (0.20): {high_delta_symbol}")



def find_options_by_expiration(symbol, days_to_expiration):
	# Get option chains
	session_token = TastytradeAuth(username(), password()).get_session()
	headers = {"Authorization": f"{session_token}"}
	response = requests.get(f"{api_url()}/option-chains/{symbol}", headers=headers)
	response_data = json.loads(response.content)
	option_chain = response_data["data"]["items"]

	# Calculate the target expiration date
	target_date = datetime.datetime.now() + datetime.timedelta(days=days_to_expiration)

	# Find the expiration date closest to the target date
	closest_expiration_date = min(option_chain, key=lambda x: abs(datetime.datetime.strptime(x['expiration-date'], "%Y-%m-%d") - target_date))['expiration-date']

	# Filter options by the closest expiration date
	options_at_closest_expiration = [option for option in option_chain if option['expiration-date'] == closest_expiration_date]

	# Extract the symbols of the options
	option_symbols = [option['streamer-symbol'] for option in options_at_closest_expiration]

	return option_symbols

async def getDeltaSymbols(symbols):
	websocket_url = "wss://demo.dxfeed.com/dxlink-ws"
	client = TastytradeWebsocketClient(websocket_url, '', data_queue)

	symbol_deltas = {}
	for i, symbol in enumerate(symbols, start=1):
		print(f"Connecting to process symbol: {symbol} ({i}/{len(symbols)})")
		while True:
			try:
				await client.connect()
				break  # Exit the loop if the connection is successful
			except (websockets.ConnectionClosedOK, websockets.InvalidStatusCode):
				print("Error connecting. Retrying...")
				await asyncio.sleep(2)  # Wait for 2 seconds before retrying
				continue  # Retry connecting

		try:
			await client.subscribe_to_greeks(client.websocket, [symbol])

			print(f"Subscribed to symbol: {symbol}")

			data = await asyncio.wait_for(data_queue.get(), timeout=8)  # Adjust timeout as needed
			print(data)
			if 'delta' in data['data'][0]:
				symbol_deltas[symbol] = data['data'][0]['delta']
		except asyncio.TimeoutError as e:
			print(f"Timeout waiting for data for symbol {symbol}: {e}")

		# Disconnect after processing the symbol
		await client.disconnect()

	print("Deltas for symbols:", symbol_deltas)
	return symbol_deltas

if __name__ == '__main__':
	main()
