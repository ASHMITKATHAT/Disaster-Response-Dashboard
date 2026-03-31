import logging
from flask import Blueprint, request, jsonify
from datetime import datetime

from gis_integration import GISIntegration

logger = logging.getLogger(__name__)

gis_bp = Blueprint('gis', __name__, url_prefix='/api/gis')
gis = GISIntegration()

@gis_bp.route('/layers', methods=['GET'])
def get_layers():
    return jsonify({"success": True, "layers": gis.get_layer_status()})

@gis_bp.route('/features', methods=['GET'])
def get_features():
    feature_type = request.args.get('type')
    features = gis.geo_features
    if feature_type:
        features = [f for f in features if f["properties"].get("feature_type") == feature_type]
    collection = gis.create_geojson_collection(features)
    return jsonify({"success": True, "geojson": collection})

@gis_bp.route('/features', methods=['POST'])
def create_feature():
    data = request.get_json()
    feature = gis.create_feature(
        data.get('feature_type', 'generic'),
        data.get('geometry', {"type": "Point", "coordinates": [74.0, 26.0]}),
        data.get('properties', {})
    )
    return jsonify({"success": True, "feature": feature})

@gis_bp.route('/query', methods=['GET'])
def spatial_query():
    lat = request.args.get('lat', 26.0, type=float)
    lon = request.args.get('lon', 74.0, type=float)
    radius = request.args.get('radius', 50, type=float)
    types = request.args.get('types', '').split(',') if request.args.get('types') else None
    result = gis.spatial_query(lat, lon, radius, types)
    return jsonify({"success": True, "query": result})

@gis_bp.route('/buffer', methods=['POST'])
def create_buffer():
    data = request.get_json()
    zone = gis.create_buffer_zone(
        data.get('lat', 26.0), data.get('lon', 74.0),
        data.get('radius_km', 10), data.get('zone_type', 'danger')
    )
    return jsonify({"success": True, "zone": zone})

@gis_bp.route('/heatmap', methods=['GET'])
def get_heatmap():
    d_type = request.args.get('disaster_type', 'flood')
    data = gis.get_risk_heatmap_data(d_type)
    return jsonify({"success": True, "heatmap": data})

# 2026-01-02 18:34:39 weather data integration

# 2026-01-23 14:28:22 weather data integration

// 2026-03-31 09:16:45 UI component update
