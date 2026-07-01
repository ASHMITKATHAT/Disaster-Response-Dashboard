import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from weather_integration import WeatherIntegration

class TestWeatherIntegration:
    def setup_method(self):
        self.wi = WeatherIntegration()

    def test_simulate_weather(self):
        result = self.wi._simulate_weather(26.2389, 73.0243)
        assert "temperature_c" in result
        assert "humidity_percent" in result
        assert "wind_speed_mps" in result

    def test_simulate_forecast(self):
        result = self.wi._simulate_forecast(26.2389, 73.0243, 5)
        assert result["days"] == 5
        assert len(result["forecast"]) == 5

    def test_weather_index(self):
        weather = self.wi._simulate_weather(26.2389, 73.0243)
        index = self.wi.compute_weather_index(weather)
        assert "index" in index
        assert "level" in index
        assert 0 <= index["index"] <= 100

    def test_station_status(self):
        stations = self.wi.get_station_status()
        assert len(stations) > 0
        assert "status" in stations[0]

    def test_weather_alerts_generation(self):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            alerts = loop.run_until_complete(self.wi.fetch_severe_weather_alerts(26.2389, 73.0243))
        finally:
            loop.close()
        assert isinstance(alerts, list)
