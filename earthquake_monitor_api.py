import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
import numpy as np

from earthquake_pipeline import EarthquakeDataPipeline
from seismic_monitor import SeismicMonitor
from gis_integration import GISIntegration

logger = logging.getLogger(__name__)

seismic_bp = Blueprint('seismic', __name__, url_prefix='/api/seismic')
eq_pipeline = EarthquakeDataPipeline()
seismic_monitor = SeismicMonitor()
gis = GISIntegration()

@seismic_bp.route('/status', methods=['GET'])
def get_seismic_status():
    return jsonify({
        "success": True,
        "data": {
            "pipeline": {"events_processed": len(eq_pipeline.events)},
            "monitor": seismic_monitor.get_status(),
            "stations": eq_pipeline.stations,
            "timestamp": datetime.now().isoformat()
        }
    })

@seismic_bp.route('/events', methods=['GET'])
def get_seismic_events():
    hours = request.args.get('hours', 24, type=int)
    events = eq_pipeline.get_recent_events(hours)
    return jsonify({"success": True, "count": len(events), "events": events})

@seismic_bp.route('/events/<event_id>', methods=['GET'])
def get_seismic_event(event_id):
    event = eq_pipeline.get_event_summary(event_id)
    if event:
        return jsonify({"success": True, "event": event})
    return jsonify({"success": False, "error": "Event not found"}), 404

@seismic_bp.route('/process', methods=['POST'])
def process_seismic_event():
    try:
        data = request.get_json()
        waveforms = data.get('waveforms', [])
        stations = data.get('stations', [])

        if not waveforms:
            wf_data = np.random.randn(1000) * 0.01
            wf_data[200:400] += np.sin(np.linspace(0, 20*np.pi, 200)) * 0.1
            waveforms = [{"data": wf_data.tolist(), "sample_rate": 100, "station_id": "STN001"}]

        if not stations:
            stations = eq_pipeline.stations[:3]

        event = eq_pipeline.process_event(waveforms, stations)
        eq_pipeline.events.append(event)

        return jsonify({"success": True, "event": event})
    except Exception as e:
        logger.error(f"Process error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@seismic_bp.route('/monitor/data', methods=['GET'])
def get_monitor_data():
    station_id = request.args.get('station', 'STN001')
    data = np.random.randn(500) * 0.005
    data[100:150] += np.sin(np.linspace(0, 10*np.pi, 50)) * 0.05
    return jsonify({
        "success": True,
        "data": {
            "station_id": station_id,
            "waveform": data.tolist(),
            "sample_rate": 100,
            "sta_lta": seismic_monitor.compute_sta_lta(station_id) or 1.2,
            "alert_level": seismic_monitor.get_current_alert_level(station_id),
            "timestamp": datetime.now().isoformat()
        }
    })

# 2026-03-17 10:35:31 weather data integration

// 2026-05-21 14:54:57 UI component update
