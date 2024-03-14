import asyncio
import json
import websockets
import logging

logger = logging.getLogger(__name__)

class TastytradeWebsocketClient:
	def __init__(self, url, auth_token, data_queue):
		self.url = url
		self.auth_token = auth_token
		self.data_queue = data_queue
		self.channel_opened_event = asyncio.Event()
		self.subscribed_symbols = []

	async def connect(self):
		self.reset_state()
		headers = {
			'Authorization': 'Bearer ' + self.auth_token,
			'User-Agent': 'My Python App'
		}
		async with websockets.connect(self.url, extra_headers=headers) as websocket:
			self.websocket = websocket
			await self.setup_connection(websocket)
			await self.authorize(websocket)
			await self.request_channel(websocket)

			listen_task = asyncio.create_task(self.process_messages(websocket))

			try:
				await asyncio.wait_for(self.channel_opened_event.wait(), timeout=10)
			except asyncio.TimeoutError:
				logger.error("Timeout waiting for channel to open")
				listen_task.cancel()
				return

			# Re-subscribe to quotes if needed
			if self.subscribed_symbols:
				await self.subscribe_to_quotes(websocket, self.subscribed_symbols)


	async def setup_connection(self, websocket):
		setup_message = {
			"type": "SETUP",
			"channel": 0,
			"keepaliveTimeout": 60,
			"acceptKeepaliveTimeout": 60,
			"version": "0.1"
		}
		await websocket.send(json.dumps(setup_message))

	async def process_messages(self, websocket):
		async for message_data in self.listen(websocket):
			await self.data_queue.put(message_data)

	async def authorize(self, websocket):
		auth_message = {
			"type": "AUTH",
			"token": self.auth_token,
			"channel": 0
		}
		await websocket.send(json.dumps(auth_message))

	async def subscribe_to_quotes(self, websocket, symbols):
		self.subscribed_symbols = symbols
		subscription_message = {
			"channel": self.channel_id,
			"type": "FEED_SUBSCRIPTION",
			"add": [{"type": "Quote", "symbol": symbol} for symbol in symbols]
		}
		await websocket.send(json.dumps(subscription_message))

	async def request_channel(self, websocket):
		channel_request_message = {
			"type": "CHANNEL_REQUEST",
			"channel": 1,
			"service": "FEED",
			"parameters": {"contract": "AUTO"}
		}
		message_str = json.dumps(channel_request_message)
		logger.debug(f"Sending message: {message_str}")
		await websocket.send(message_str)


	def reset_state(self):
		self.channel_opened_event.clear()

	async def listen(self, websocket):
		while True:
			try:
				message = await websocket.recv()
				print("Websocket message: ", message)
				data = json.loads(message)
				if data.get("type") == "CHANNEL_OPENED":
					self.channel_id = data["channel"]
					self.channel_opened_event.set()
				elif data.get("type") == "FEED_DATA":
					yield data
			except websockets.exceptions.ConnectionClosedOK:
				print("Connection closed normally, attempting to reconnect...")
				await self.connect()  # Reconnect to the WebSocket
				break
			except websockets.exceptions.ConnectionClosedError as e:
				print(f"Connection closed with error: {e}")
				break
			except Exception as e:
				print(f"Error while processing message: {e}")