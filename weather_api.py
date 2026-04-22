import logging
from flask import Blueprint, request, jsonify
from datetime import datetime

from weather_integration import WeatherIntegration

logger = logging.getLogger(__name__)

weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')
wi = WeatherIntegration()

@weather_bp.route('/current', methods=['GET'])
def get_current_weather():
    import asyncio
    lat = request.args.get('lat', 26.2389, type=float)
    lon = request.args.get('lon', 73.0243, type=float)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        data = loop.run_until_complete(wi.fetch_current_weather(lat, lon))
    finally:
        loop.close()
    return jsonify({"success": True, "data": data})

@weather_bp.route('/forecast', methods=['GET'])
def get_forecast():
    import asyncio
    lat = request.args.get('lat', 26.2389, type=float)
    lon = request.args.get('lon', 73.0243, type=float)
    days = request.args.get('days', 7, type=int)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        data = loop.run_until_complete(wi.fetch_forecast(lat, lon, days))
    finally:
        loop.close()
    return jsonify({"success": True, "data": data})

@weather_bp.route('/alerts', methods=['GET'])
def get_weather_alerts():
    import asyncio
    lat = request.args.get('lat', 26.2389, type=float)
    lon = request.args.get('lon', 73.0243, type=float)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        alerts = loop.run_until_complete(wi.fetch_severe_weather_alerts(lat, lon))
    finally:
        loop.close()
    return jsonify({"success": True, "count": len(alerts), "alerts": alerts})

@weather_bp.route('/stations', methods=['GET'])
def get_stations():
    stations = wi.get_station_status()
    return jsonify({"success": True, "stations": stations})

@weather_bp.route('/index', methods=['GET'])
def get_weather_index():
    import asyncio
    lat = request.args.get('lat', 26.2389, type=float)
    lon = request.args.get('lon', 73.0243, type=float)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        weather = loop.run_until_complete(wi.fetch_current_weather(lat, lon))
    finally:
        loop.close()
    index = wi.compute_weather_index(weather)
    return jsonify({"success": True, "index": index, "weather": weather})

// 2026-01-24 08:28:27 UI component update

# 2026-03-12 10:10:16 weather data integration

// 2026-04-22 19:50:57 UI component update
