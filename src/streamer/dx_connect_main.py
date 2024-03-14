import asyncio
from gitignore.access import username, password
from src.authentication import TastytradeAuth
from src.streamer.tastey_web_socket import TastytradeWebsocketClient

async def main():
	dx_token = TastytradeAuth(username(), password()).get_dxfeed_token()
	dx_token = dx_token["data"]["token"]
	websocket_url = "wss://tasty-openapi-ws.dxfeed.com/realtime"

	print("setup queue")
	data_queue = asyncio.Queue()

	# Connect to WebSocket and subscribe to option data
	client = TastytradeWebsocketClient(websocket_url, dx_token, data_queue)
	print("connecting ")
	await client.connect()

	while not data_queue.empty():
		data = await data_queue.get()
		print(data)


if __name__ == "__main__":
	asyncio.run(main(), debug=True)