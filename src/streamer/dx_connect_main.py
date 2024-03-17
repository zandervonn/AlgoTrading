import asyncio
import re

from gitignore.access import username, password
from src.authentication import TastytradeAuth
from src.streamer.tastey_web_socket import TastytradeWebsocketClient

async def main():
	TastytradeAuth(username(), password()).get_session()
	dx_token = TastytradeAuth(username(), password()).get_dxfeed_token()
	dx_token = dx_token["data"]["token"]
	print(dx_token)
	websocket_url = "wss://demo.dxfeed.com/dxlink-ws"

	print("setup queue")
	data_queue = asyncio.Queue()

	# Connect to WebSocket and subscribe to option data
	client = TastytradeWebsocketClient(websocket_url, dx_token, data_queue)
	print("connecting ")
	await client.connect()

	# Wait for a few seconds before subscribing to quotes
	await asyncio.sleep(1)

	# await client.subscribe_to_quotes(client.websocket, ["AAPL", "GOOG"])
	# await client.subscribe_to_options(client.websocket, [".AAPL260618P250"])
	await client.subscribe_to_greeks(client.websocket, [".AAPL260618P250", ".AAPL260618P255"])

	# Process received data
	while True:
		data = await data_queue.get()
		print(data)


if __name__ == "__main__":
	asyncio.run(main(), debug=True)