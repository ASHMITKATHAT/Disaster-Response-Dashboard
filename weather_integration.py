import asyncio
import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import aiohttp

logger = logging.getLogger(__name__)

class WeatherIntegration:
    def __init__(self, api_key: str = None, data_dir: str = "data/weather"):
        self.api_key = api_key
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.weather_stations = self._init_weather_stations()
        self.cache = {}
        self.session = None

    def _init_weather_stations(self) -> List[Dict]:
        return [
            {"id": "WX001", "name": "Jodhpur AWS", "lat": 26.2389, "lon": 73.0243, "elevation_m": 231, "status": "active"},
            {"id": "WX002", "name": "Jaipur Met Station", "lat": 26.9124, "lon": 75.7873, "elevation_m": 431, "status": "active"},
            {"id": "WX003", "name": "Udaipur Observatory", "lat": 24.5854, "lon": 73.7125, "elevation_m": 598, "status": "active"},
            {"id": "WX004", "name": "Bikaner Weather Post", "lat": 28.0229, "lon": 73.3119, "elevation_m": 227, "status": "active"},
            {"id": "WX005", "name": "Kota Radar Station", "lat": 25.2138, "lon": 75.8648, "elevation_m": 305, "status": "active"}
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def fetch_current_weather(self, lat: float, lon: float) -> Dict:
        cache_key = f"weather_{lat:.2f}_{lon:.2f}"
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=600):
                return cached_data

        if self.session and self.api_key:
            try:
                params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
                async with self.session.get("https://api.openweathermap.org/data/2.5/weather", params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result = {
                            "temperature_c": data["main"]["temp"],
                            "feels_like_c": data["main"]["feels_like"],
                            "humidity_percent": data["main"]["humidity"],
                            "pressure_hpa": data["main"]["pressure"],
                            "wind_speed_mps": data["wind"]["speed"],
                            "wind_gust_mps": data["wind"].get("gust", 0),
                            "wind_direction_deg": data["wind"].get("deg", 0),
                            "cloud_cover_percent": data["clouds"]["all"],
                            "visibility_m": data.get("visibility", 10000),
                            "weather_condition": data["weather"][0]["main"],
                            "weather_description": data["weather"][0]["description"],
                            "weather_icon": data["weather"][0]["icon"],
                            "rain_1h_mm": data.get("rain", {}).get("1h", 0),
                            "rain_3h_mm": data.get("rain", {}).get("3h", 0),
                            "snow_1h_mm": data.get("snow", {}).get("1h", 0),
                            "timestamp": datetime.now().isoformat(),
                            "source": "openweathermap"
                        }
                        self.cache[cache_key] = (datetime.now(), result)
                        return result
            except Exception as e:
                logger.warning(f"OpenWeather fetch failed: {e}")

        return self._simulate_weather(lat, lon)

    async def fetch_forecast(self, lat: float, lon: float, days: int = 7) -> Dict:
        cache_key = f"forecast_{lat:.2f}_{lon:.2f}_{days}"
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=1800):
                return cached_data

        if self.session and self.api_key:
            try:
                params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric", "cnt": days * 8}
                async with self.session.get("https://api.openweathermap.org/data/2.5/forecast", params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        daily = {}
                        for item in data["list"]:
                            dt = datetime.fromtimestamp(item["dt"])
                            day_key = dt.strftime("%Y-%m-%d")
                            if day_key not in daily:
                                daily[day_key] = {"temps": [], "humidity": [], "rain": 0, "wind": [], "conditions": []}
                            daily[day_key]["temps"].append(item["main"]["temp"])
                            daily[day_key]["humidity"].append(item["main"]["humidity"])
                            daily[day_key]["rain"] += item.get("rain", {}).get("3h", 0)
                            daily[day_key]["wind"].append(item["wind"]["speed"])
                            daily[day_key]["conditions"].append(item["weather"][0]["description"])

                        forecast_days = []
                        for day_key, day_data in sorted(daily.items()):
                            forecast_days.append({
                                "date": day_key,
                                "temp_min": round(min(day_data["temps"]), 1),
                                "temp_max": round(max(day_data["temps"]), 1),
                                "temp_avg": round(sum(day_data["temps"]) / len(day_data["temps"]), 1),
                                "humidity_avg": round(sum(day_data["humidity"]) / len(day_data["humidity"]), 1),
                                "total_rain_mm": round(day_data["rain"], 1),
                                "wind_avg": round(sum(day_data["wind"]) / len(day_data["wind"]), 1),
                                "conditions": max(set(day_data["conditions"]), key=day_data["conditions"].count)
                            })

                        result = {"latitude": lat, "longitude": lon, "forecast": forecast_days, "days": len(forecast_days), "timestamp": datetime.now().isoformat(), "source": "openweathermap"}
                        self.cache[cache_key] = (datetime.now(), result)
                        return result
            except Exception as e:
                logger.warning(f"Forecast fetch failed: {e}")

        return self._simulate_forecast(lat, lon, days)

    async def fetch_severe_weather_alerts(self, lat: float, lon: float) -> List[Dict]:
        alerts = []
        current = await self.fetch_current_weather(lat, lon)

        if current.get("wind_speed_mps", 0) > 20:
            alerts.append({"type": "high_wind", "severity": "warning", "message": f"High winds of {current['wind_speed_mps']} m/s detected"})
        if current.get("rain_3h_mm", 0) > 50:
            alerts.append({"type": "heavy_rain", "severity": "warning", "message": f"Heavy rainfall of {current['rain_3h_mm']}mm in 3 hours"})
        if current.get("visibility_m", 10000) < 1000:
            alerts.append({"type": "low_visibility", "severity": "advisory", "message": f"Low visibility at {current['visibility_m']}m"})

        forecast = await self.fetch_forecast(lat, lon, 3)
        for day in forecast.get("forecast", []):
            if day.get("total_rain_mm", 0) > 100:
                alerts.append({"type": "forecast_heavy_rain", "severity": "warning", "date": day["date"], "message": f"Heavy rain forecast: {day['total_rain_mm']}mm on {day['date']}"})

        return alerts

    def _simulate_weather(self, lat: float, lon: float) -> Dict:
        hour = datetime.now().hour
        base_temp = 30 - abs(hour - 13) * 2 + np_random(0, 5)
        humidity = 40 + np_random(-10, 20)
        return {
            "temperature_c": round(base_temp, 1),
            "feels_like_c": round(base_temp + 2, 1),
            "humidity_percent": round(humidity),
            "pressure_hpa": round(1013 + np_random(-5, 5)),
            "wind_speed_mps": round(np_random(2, 8), 1),
            "wind_gust_mps": round(np_random(5, 15), 1),
            "wind_direction_deg": round(np_random(0, 360)),
            "cloud_cover_percent": round(np_random(10, 80)),
            "visibility_m": round(np_random(5000, 15000)),
            "weather_condition": "Clear" if np_random(0, 1) > 0.5 else "Clouds",
            "weather_description": "clear sky" if np_random(0, 1) > 0.5 else "few clouds",
            "rain_1h_mm": round(max(0, np_random(0, 5)), 1),
            "rain_3h_mm": round(max(0, np_random(0, 15)), 1),
            "snow_1h_mm": 0,
            "timestamp": datetime.now().isoformat(),
            "source": "simulated"
        }

    def _simulate_forecast(self, lat: float, lon: float, days: int) -> Dict:
        forecast = []
        for d in range(days):
            dt = (datetime.now() + timedelta(days=d)).strftime("%Y-%m-%d")
            base_temp = 28 + np_random(-5, 5)
            forecast.append({
                "date": dt,
                "temp_min": round(base_temp - np_random(3, 7), 1),
                "temp_max": round(base_temp + np_random(3, 7), 1),
                "temp_avg": round(base_temp, 1),
                "humidity_avg": round(40 + np_random(-10, 20)),
                "total_rain_mm": round(max(0, np_random(0, 25)), 1),
                "wind_avg": round(np_random(2, 10), 1),
                "conditions": "Clear" if np_random(0, 1) > 0.5 else "Cloudy"
            })
        return {"latitude": lat, "longitude": lon, "forecast": forecast, "days": len(forecast), "timestamp": datetime.now().isoformat(), "source": "simulated"}

    def get_station_status(self) -> List[Dict]:
        return [{"id": s["id"], "name": s["name"], "lat": s["lat"], "lon": s["lon"], "elevation_m": s["elevation_m"], "status": s["status"]} for s in self.weather_stations]

    def compute_weather_index(self, weather_data: Dict) -> Dict:
        severity = 0
        if weather_data.get("wind_speed_mps", 0) > 15:
            severity += 20
        if weather_data.get("rain_3h_mm", 0) > 30:
            severity += 30
        if weather_data.get("humidity_percent", 50) > 85:
            severity += 10
        if weather_data.get("visibility_m", 10000) < 2000:
            severity += 15

        if severity >= 60:
            level = "severe"
        elif severity >= 35:
            level = "moderate"
        elif severity >= 15:
            level = "caution"
        else:
            level = "normal"

        return {"index": min(100, severity), "level": level, "factors": {
            "wind": min(100, weather_data.get("wind_speed_mps", 0) * 5),
            "rain": min(100, weather_data.get("rain_3h_mm", 0) * 2),
            "humidity": min(100, weather_data.get("humidity_percent", 50) * 1.2),
            "visibility": max(0, 100 - weather_data.get("visibility_m", 10000) / 100)
        }}

def np_random(low: float, high: float) -> float:
    import random
    return random.uniform(low, high)

# 2026-01-02 19:58:25 weather data integration
