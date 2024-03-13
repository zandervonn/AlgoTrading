import json
import os

import requests
import time
from typing import Dict, Optional

from gitignore.access import api_url, storage_path


class TastytradeAuth:
	def __init__(self, username: str, password: str = None, remember_token: str = None):
		self.username = username
		self.password = password
		self.remember_token = remember_token
		self.url = f"{api_url()}/sessions"
		self.session_token = None
		self.user_data = None
		self.token_timestamp = None
		self.storage_path = storage_path()
		self.load_token()

	def login(self, two_factor_code: str = None) -> Optional[Dict[str, str]]:
		payload = {"login": self.username, "remember-me": "true"}

		if self.password:
			payload["password"] = self.password
		elif self.remember_token:
			payload["remember-token"] = self.remember_token
		else:
			print("Error: Either password or remember token must be provided")
			return None

		headers = {}
		if two_factor_code:
			headers["X-Tastyworks-OTP"] = two_factor_code

		response = requests.post(self.url, headers=headers, data=payload)

		if response.status_code == 201:
			data = response.json()
			self.session_token = data["data"]["session-token"]
			self.remember_token = data["data"]["remember-token"]
			self.user_data = data["data"]["user"]
			self.token_timestamp = time.time()
			self.save_token()
			return data
		else:
			print(f"Error: {response.status_code}")
			return None

	def validate_session(self) -> Optional[Dict[str, str]]:
		"""
		Validates the current session using the session token.

		Returns:
			Optional[Dict[str, str]]: A dictionary containing the user data if the session is valid.
			Returns None if the session is invalid or there's an error.
		"""
		url = f"{api_url()}/sessions/validate"
		headers = {"Authorization": self.session_token}

		response = requests.post(url, headers=headers)

		if response.status_code == 200 or response.status_code == 201:
			data = response.json()
			return data
		else:
			print(f"Error: {response.status_code}")
			print("Response text:", response.text)

			return None

	def destroy_session(self) -> bool:
		"""
		Destroys the current session, logging the user out.

		Returns:
			bool: True if the session was successfully destroyed, False otherwise.
		"""

		headers = {"Authorization": self.session_token}

		response = requests.delete(self.url, headers=headers)

		if response.status_code == 204:
			self.session_token = None
			self.remember_token = None
			self.user_data = None
			return True
		else:
			print(f"Error: {response.status_code}")
			return False

	def get_dxfeed_token(self) -> Optional[Dict[str, str]]:
		"""
		Retrieves the dxfeed token by making a request to the Tastytrade endpoint.

		Returns:
			Optional[Dict[str, str]]: A dictionary containing the dxfeed token and other related data.
			Returns None if there's an error.
		"""
		if not self.session_token:
			print("Error: Session token not found. Please login first.")
			return None

		url = f"{api_url()}/api-quote-tokens"
		headers = {"Authorization": self.session_token}

		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			data = response.json()
			return data
		else:
			print(f"Error: {response.status_code}")
			print("Response text:", response.text)
			return None

	def create_session(
			self,
			username: str,
			password: str,
			remember_me: bool = False,
			remember_token: str = None,
	) -> Optional[Dict[str, str]]:
		"""
		Creates a new user session with the Tastytrade API, using the specified username and password.

		Args:
			username (str): The username or email of the user.
			password (str): The password for the user's account.
			remember_me (bool): Whether the session should be extended for longer than normal via remember token.
			Defaults to False.
			remember_token (str): The remember token. Allows skipping for 2 factor within its window.

		Returns:
			Optional[Dict[str, str]]: A dictionary containing the user's session token and other related data.
			Returns None if there's an error.
		"""
		payload = {
			"login": username,
			"password": password,
			"remember-me": remember_me,
			"remember-token": remember_token,
		}

		headers = {}
		response = requests.post(self.url, headers=headers, json=payload)

		if response.status_code == 201:
			data = response.json()
			self.session_token = data["data"]["session-token"]
			self.remember_token = data["data"]["remember-token"]
			self.user_data = data["data"]["user"]
			self.token_timestamp = time.time()
			self.save_token()
			return data
		else:
			print(f"Error: {response.status_code}")
			return None

	def load_token(self):
		"""
		Loads the session token and timestamp from the storage file.
		"""
		if os.path.exists(self.storage_path):
			with open(self.storage_path, "r") as file:
				data = json.load(file)
				self.session_token = data.get("session_token")
				self.token_timestamp = data.get("token_timestamp")

	def save_token(self):
		"""
		Saves the current session token and timestamp to the storage file.
		"""
		data = {
			"session_token": self.session_token,
			"token_timestamp": self.token_timestamp
		}
		with open(self.storage_path, "w") as file:
			json.dump(data, file)

	def get_session(self) -> str:
		"""
		Gets the current session token, refreshing it if it's been more than 24 hours.
		Saves the refreshed token to storage.

		Returns:
			str: The current session token.
		"""

		if self.validate_session() == None:
			self.login()
			self.save_token()


		return self.session_token