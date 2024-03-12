import datetime

import pandas as pd
import pandas_market_calendars as mcal

class MarketHours:
	def __init__(self):
		self.market_calendar = mcal.get_calendar('NYSE')
		self.market_open = self.market_calendar.open_time
		self.market_close = self.market_calendar.close_time
		self.holidays = self._get_holidays()

	def _get_holidays(self):
		holidays = self.market_calendar.holidays().holidays
		return {pd.to_datetime(holiday).date() for holiday in holidays}

	def is_market_open(self, current_time):
		if current_time.weekday() >= 5:  # Saturday (5) or Sunday (6)
			return False
		if current_time.date() in self.holidays:
			return False
		if self.market_open <= current_time.time() <= self.market_close:
			return True
		return False

	def time_until_open(self, current_time):
		if current_time.time() > self.market_close:
			next_open = current_time + pd.Timedelta(days=1)
		else:
			next_open = current_time
		while next_open.weekday() >= 5 or next_open.date() in self.holidays:
			next_open += pd.Timedelta(days=1)
		next_open = pd.Timestamp.combine(next_open.date(), self.market_open)
		return next_open - current_time

	def is_holiday(self, current_time):
		return current_time.date() in self.holidays

	def next_holiday(self, current_time):
		for holiday in sorted(self.holidays):
			if holiday > current_time.date():
				return holiday
		return None

	def list_holidays(self):
		today = datetime.date.today()
		one_year_from_now = today + datetime.timedelta(days=365)
		upcoming_holidays = [holiday for holiday in self.holidays if today <= holiday <= one_year_from_now]
		upcoming_holidays.sort()
		return upcoming_holidays

