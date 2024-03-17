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
		self.subscribed_symbols = {}
		self.websocket = None

	async def connect(self):
		if self.websocket is not None:
			await self.websocket.close()

		self.reset_state()
		headers = {
			'Authorization': 'Bearer ' + self.auth_token,
			'User-Agent': 'My Python App'
		}
		try:
			self.websocket = await websockets.connect(self.url, extra_headers=headers)
		except websockets.InvalidStatusCode as e:
			logger.error(f"Connection failed with status code {e.status_code}")
			return
		except Exception as e:
			logger.error(f"Error during connection: {e}")
			return

		logger.info("Connection established")
		await self.setup_connection(self.websocket)
		await self.authorize(self.websocket)
		await self.request_channel(self.websocket)

		heartbeat_task = asyncio.create_task(self.send_heartbeat(self.websocket))
		listen_task = asyncio.create_task(self.process_messages(self.websocket))

		try:
			await asyncio.wait_for(self.channel_opened_event.wait(), timeout=10)
		except asyncio.TimeoutError:
			logger.error("Timeout waiting for channel to open")
			listen_task.cancel()
			return

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

	async def subscribe_to_options(self, websocket, symbols):
		self.subscribed_symbols = symbols
		subscription_message = {
			"channel": self.channel_id,
			"type": "FEED_SUBSCRIPTION",
			"add": [{"type": "Options", "symbol": symbol} for symbol in symbols]
		}
		await websocket.send(json.dumps(subscription_message))

	async def subscribe_to_greeks(self, websocket, symbols):
		subscription_message = {
			"channel": self.channel_id,
			"type": "FEED_SUBSCRIPTION",
			"add": [{"type": "Greeks", "symbol": symbol} for symbol in symbols]
		}
		for symbol in symbols:
			self.subscribed_symbols[symbol] = None
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

	async def disconnect(self):
		if self.websocket and self.websocket.open:
			await self.websocket.close()
			logger.info("Disconnected from WebSocket")

	async def send_heartbeat(self, websocket):
		heartbeat_message = {
			"type": "KEEPALIVE",
			"channel": 0
		}
		while True:
			await asyncio.sleep(10)  # Send a heartbeat every 30 seconds
			if websocket.open:
				logger.info("Sending heartbeat")
				await websocket.send(json.dumps(heartbeat_message))
			else:
				logger.info("Connection closed, stopping heartbeat")
				break

	async def listen(self, websocket):
		while True:
			try:
				message = await websocket.recv()
				logger.info(f"Received message: {message}")
				data = json.loads(message)
				if data.get("type") == "CHANNEL_OPENED":
					self.channel_id = data["channel"]
					self.channel_opened_event.set()
				elif data.get("type") == "FEED_DATA":
					for item in data['data']:
						symbol = item['eventSymbol']
						if symbol in self.subscribed_symbols:
							self.subscribed_symbols[symbol] = item
					yield data
			except websockets.ConnectionClosedOK as e:
				# logger.info(f"Connection closed normally with code {e.code}: {e.reason}")
				print(f"Connection closed normally with code {e.code}")
				await self.connect()
				break
			except websockets.ConnectionClosedError as e:
				# logger.error(f"Connection closed with error code {e.code}: {e.reason}")
				print(f"Connection closed with error code {e.code}")
				break
			except Exception as e:
				# logger.error(f"Error while processing message: {e}")
				print("Error while processing message")