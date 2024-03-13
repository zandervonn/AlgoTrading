import asyncio
import logging
import configparser

from gitignore.access import username, password, websocket_url, dx_websocket
from src.authentication import TastytradeAuth
from src.streamer.dx_feed_handler import CometdWebsocketClient
from src.streamer.dx_mapping import Quote


async def dx_token_builder():
	logger = logging.getLogger(__name__)

	log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	log_handler = logging.StreamHandler()
	log_handler.setFormatter(log_format)

	root_logger = logging.getLogger()
	root_logger.setLevel(logging.DEBUG)
	root_logger.addHandler(log_handler)

	logging.getLogger("websockets").setLevel(logging.DEBUG)

	config = configparser.ConfigParser()
	config.read("config.ini")
	username = config.get("ACCOUNT", "username")
	password = config.get("ACCOUNT", "password")
	TTClient = TastytradeAuth(username, password)
	TTClient.login()
	get_token = TTClient.get_dxfeed_token()
	dxfeedtoken = get_token["data"]["token"]
	logger.debug("DxFeed Token:", dxfeedtoken)

	return dxfeedtoken


async def on_handshake_success(client):
	event_type = "Trade"
	symbols = ["VIX"]
	for symbol in symbols:
		await client.send_subscription_message(client.websocket, event_type, symbol)


async def consume_data(queue):
	while True:
		data = await queue.get()
		if data is None:
			break
		try:
			print("This is the raw data: ", data)
			quotes = Quote.from_list(data)
			for quote in quotes:
				print("Data received in script:", quote)
		except ValueError:
			print("Invalid data list received")


async def main():
	websocket_url = "wss://tasty-live-web.dxfeed.com/live/cometd"
	data_queue = asyncio.Queue()

	client = CometdWebsocketClient(
		websocket_url, dx_token_builder(), data_queue, on_handshake_success
	)

	connect_task = asyncio.create_task(client.connect())
	consume_data_task = asyncio.create_task(consume_data(data_queue))

	await asyncio.gather(connect_task, consume_data_task)

async def main2():
	# Authenticate and get access token
	print("main2")
	dx_token = TastytradeAuth(username(), password()).get_dxfeed_token()
	print(dx_token)
	dx_token = dx_token["data"]["token"]
	print(dx_token)

	# Connect to WebSocket and subscribe to option data
	data_queue = asyncio.Queue()
	client = CometdWebsocketClient(dx_websocket(), dx_token, data_queue, on_handshake_success2)
	await client.connect()

	# Consume and process data
	await consume_data2(data_queue)

async def on_handshake_success2(client):
	# Subscribe to option data
	option_symbol = "AAPL220121C00150000"  # Example option symbol
	await client.send_subscription_message(client.websocket, "Quote", option_symbol)

async def consume_data2(queue):
	while True:
		data = await queue.get()
		if data is None:
			break
		quotes = Quote.from_list(data)
		for quote in quotes:
			print(f"Symbol: {quote.symbol}, Bid Price: {quote.bid_price}")


if __name__ == "__main__":
	asyncio.run(main2(), debug=True)