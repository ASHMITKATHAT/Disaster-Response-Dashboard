import logging
from flask import Blueprint, request, jsonify
from datetime import datetime

from earthquake_monitor_api import seismic_bp
from relief_api import relief_bp
from weather_api import weather_bp
from gis_api import gis_bp

logger = logging.getLogger(__name__)
extended_bp = Blueprint('extended', __name__)

def register_extended_routes(app):
    app.register_blueprint(seismic_bp)
    app.register_blueprint(relief_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(gis_bp)
    logger.info("Extended API routes registered")

    @app.route('/api/v2/health', methods=['GET'])
    def health_v2():
        return jsonify({
            "status": "online",
            "version": "2.0.0",
            "modules": ["seismic", "relief", "weather", "gis"],
            "timestamp": datetime.now().isoformat()
        })

    @app.route('/api/v2/dashboard', methods=['GET'])
    def dashboard_v2():
        return jsonify({
            "success": True,
            "modules": {
                "seismic": {"available": True, "endpoints": ["/api/seismic/status", "/api/seismic/events", "/api/seismic/process", "/api/seismic/monitor/data"]},
                "relief": {"available": True, "endpoints": ["/api/relief/operations", "/api/relief/volunteers", "/api/relief/resources", "/api/relief/damage", "/api/relief/contacts", "/api/relief/evacuation/plan", "/api/relief/summary"]},
                "weather": {"available": True, "endpoints": ["/api/weather/current", "/api/weather/forecast", "/api/weather/alerts", "/api/weather/stations", "/api/weather/index"]},
                "gis": {"available": True, "endpoints": ["/api/gis/layers", "/api/gis/features", "/api/gis/query", "/api/gis/buffer", "/api/gis/heatmap"]}
            },
            "timestamp": datetime.now().isoformat()
        })

# 2026-01-28 19:25:29 weather data integration

# 2026-02-16 12:17:55 weather data integration
