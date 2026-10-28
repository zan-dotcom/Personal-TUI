"""Cached current weather from wttr.in; no API key required."""

import json
import time
from urllib.parse import quote
from urllib.request import urlopen


class Weather:
    def __init__(self, city):
        self.city = city
        self.updated = None
        self.lines = []

    def sample(self):
        if not self.city:
            return ['Set a location with --city "Kuala Lumpur"', 'Temperature and conditions from wttr.in']
        now = time.monotonic()
        if self.updated is not None and now - self.updated < 600:
            return self.lines
        try:
            url = 'https://wttr.in/' + quote(self.city, safe='') + '?format=j1'
            with urlopen(url, timeout=3) as response:
                data = json.load(response)
            current = data['current_condition'][0]
            temperature = float(current['temp_C'])
            feels = float(current['FeelsLikeC'])
            description = str(current['weatherDesc'][0]['value'])
            self.lines = [self.city, f'{temperature:g} °C | Feels like {feels:g} °C',
                          description, f'Observed: {current.get("localObsDateTime", "time unavailable")}',
                          'Source: wttr.in | cached for 10 minutes']
        except (OSError, ValueError, KeyError, IndexError, TypeError):
            self.lines = [self.city, 'Weather unavailable (network or provider error)',
                          'Retry in 10 minutes or restart the dashboard']
        self.updated = now
        return self.lines
