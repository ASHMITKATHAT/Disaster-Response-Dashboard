import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import os

logger = logging.getLogger(__name__)

class EarthquakeDataPipeline:
    MAGNITUDE_CLASSES = {
        'micro': (0, 2.9),
        'minor': (3.0, 3.9),
        'light': (4.0, 4.9),
        'moderate': (5.0, 5.9),
        'strong': (6.0, 6.9),
        'major': (7.0, 7.9),
        'great': (8.0, 10.0)
    }

    def __init__(self, data_dir: str = "data/seismic"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.stations = self._load_stations()
        self.events = []

    def _load_stations(self) -> List[Dict]:
        return [
            {"id": "STN001", "name": "Jodhpur Seismic Station", "lat": 26.2389, "lon": 73.0243, "status": "active"},
            {"id": "STN002", "name": "Jaipur Monitoring Hub", "lat": 26.9124, "lon": 75.7873, "status": "active"},
            {"id": "STN003", "name": "Udaipur Sensor Array", "lat": 24.5854, "lon": 73.7125, "status": "active"},
            {"id": "STN004", "name": "Bikaner Relay Station", "lat": 28.0229, "lon": 73.3119, "status": "maintenance"},
            {"id": "STN005", "name": "Kota Early Warning Post", "lat": 25.2138, "lon": 75.8648, "status": "active"}
        ]

    def process_seismic_waveform(self, raw_data: np.ndarray, sample_rate: int = 100) -> Dict:
        n = len(raw_data)
        if n == 0:
            return {"error": "Empty waveform data"}

        fft = np.fft.fft(raw_data)
        freqs = np.fft.fftfreq(n, 1/sample_rate)
        magnitude_spectrum = np.abs(fft[:n//2])

        p_phase = self._detect_p_phase(raw_data, sample_rate)
        s_phase = self._detect_s_phase(raw_data, sample_rate)

        rms_amplitude = np.sqrt(np.mean(raw_data**2))
        peak_amplitude = np.max(np.abs(raw_data))
        dominant_freq = freqs[np.argmax(magnitude_spectrum)]

        return {
            "rms_amplitude": rms_amplitude,
            "peak_amplitude": peak_amplitude,
            "dominant_frequency_hz": abs(dominant_freq),
            "p_phase_arrival": p_phase,
            "s_phase_arrival": s_phase,
            "spectral_energy": float(np.sum(magnitude_spectrum**2)),
            "waveform_duration_s": n / sample_rate
        }

    def _detect_p_phase(self, data: np.ndarray, sample_rate: int) -> Optional[float]:
        window = int(0.5 * sample_rate)
        if len(data) < window * 2:
            return None
        sta = np.convolve(np.abs(data), np.ones(window)/window, mode='valid')
        lta = np.convolve(np.abs(data), np.ones(window*4)/(window*4), mode='valid')
        min_len = min(len(sta), len(lta))
        ratio = sta[:min_len] / (lta[:min_len] + 1e-10)
        trigger_idx = np.where(ratio > 4.0)[0]
        if len(trigger_idx) > 0:
            return trigger_idx[0] / sample_rate
        return None

    def _detect_s_phase(self, data: np.ndarray, sample_rate: int) -> Optional[float]:
        window = int(0.5 * sample_rate)
        envelope = np.abs(data)
        smoothed = np.convolve(envelope, np.ones(window)/window, mode='valid')
        threshold = np.mean(smoothed) + 2 * np.std(smoothed)
        trigger = np.where(smoothed > threshold)[0]
        if len(trigger) > 0:
            return trigger[-1] / sample_rate
        return None

    def locate_epicenter(self, station_data: List[Dict]) -> Dict:
        if len(station_data) < 3:
            return {"error": "Need at least 3 stations for triangulation"}

        lat_sum, lon_sum = 0, 0
        weights = []
        for sd in station_data:
            p_arrival = sd.get("p_arrival", 0)
            s_arrival = sd.get("s_arrival", 0)
            if p_arrival and s_arrival:
                delta_t = s_arrival - p_arrival
                distance = delta_t * 8.0
                weight = 1.0 / max(distance, 0.1)
                weights.append({"lat": sd["lat"], "lon": sd["lon"], "dist": distance, "w": weight})
                lat_sum += sd["lat"] * weight
                lon_sum += sd["lon"] * weight

        total_weight = sum(w["w"] for w in weights)
        if total_weight == 0:
            return {"error": "Could not compute epicenter"}

        epicenter_lat = lat_sum / total_weight
        epicenter_lon = lon_sum / total_weight
        depth_km = np.random.uniform(5, 30)

        return {
            "epicenter": {"lat": epicenter_lat, "lon": epicenter_lon},
            "depth_km": depth_km,
            "stations_used": len(weights),
            "error_ellipse_km": 5.0
        }

    def calculate_magnitude(self, amplitude_mm: float, distance_km: float, depth_km: float) -> Dict:
        if amplitude_mm <= 0:
            return {"error": "Invalid amplitude"}

        ml = np.log10(amplitude_mm) + 1.11 * np.log10(distance_km) + 0.00189 * distance_km - 2.09
        mw = (2/3) * np.log10(amplitude_mm * distance_km * 1000) - 10.7

        for cls, (low, high) in self.MAGNITUDE_CLASSES.items():
            if low <= ml < high:
                classification = cls
                break
        else:
            classification = "unknown"

        return {
            "local_magnitude_ml": round(ml, 2),
            "moment_magnitude_mw": round(mw, 2),
            "classification": classification,
            "seismic_moment_nm": round(10**(1.5 * mw + 9.1), 2),
            "amplitude_mm": amplitude_mm,
            "distance_km": distance_km
        }

    def assess_shaking_intensity(self, magnitude: float, distance_km: float, depth_km: float) -> Dict:
        modified_mercalli = min(12, max(1, 1.5 * magnitude - 3.5 * np.log10(distance_km) + 1.5))
        pga = 10**(0.5 * magnitude - 0.5 * np.log10(distance_km) - 1.5)
        pgv = 10**(0.75 * magnitude - 1.0 * np.log10(distance_km) - 0.5)

        if modified_mercalli >= 8:
            damage_level = "severe"
            alert_level = "red"
        elif modified_mercalli >= 6:
            damage_level = "moderate"
            alert_level = "orange"
        elif modified_mercalli >= 4:
            damage_level = "light"
            alert_level = "yellow"
        else:
            damage_level = "none"
            alert_level = "green"

        return {
            "mmi": round(modified_mercalli, 1),
            "pga_g": round(pga, 4),
            "pgv_cm_s": round(pgv, 2),
            "damage_level": damage_level,
            "alert_level": alert_level
        }

    def process_event(self, raw_waveforms: List[Dict], station_data: List[Dict]) -> Dict:
        event_id = f"EQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Processing seismic event {event_id}")

        processed_waveforms = []
        for wf in raw_waveforms:
            data = np.array(wf.get("data", []))
            sr = wf.get("sample_rate", 100)
            result = self.process_seismic_waveform(data, sr)
            processed_waveforms.append({**wf, "analysis": result})

        epicenter = self.locate_epicenter(station_data)

        amplitudes = [pw["analysis"].get("peak_amplitude", 0) for pw in processed_waveforms if "analysis" in pw]
        max_amplitude = max(amplitudes) if amplitudes else 1.0
        avg_distance = np.mean([sd.get("p_arrival", 1) * 8.0 for sd in station_data if sd.get("p_arrival")]) if station_data else 10.0

        magnitude = self.calculate_magnitude(max_amplitude, avg_distance, epicenter.get("depth_km", 10))
        intensity = self.assess_shaking_intensity(
            magnitude.get("local_magnitude_ml", 3.0),
            avg_distance,
            epicenter.get("depth_km", 10)
        )

        event = {
            "event_id": event_id,
            "timestamp": datetime.now().isoformat(),
            "epicenter": epicenter,
            "magnitude": magnitude,
            "intensity": intensity,
            "stations_triggered": len(station_data),
            "processed_waveforms": len(processed_waveforms),
            "status": "processed"
        }

        self.events.append(event)
        self._save_event(event)
        return event

    def _save_event(self, event: Dict):
        filepath = os.path.join(self.data_dir, f"{event['event_id']}.json")
        with open(filepath, 'w') as f:
            json.dump(event, f, indent=2)

    def get_recent_events(self, hours: int = 24) -> List[Dict]:
        cutoff = datetime.now() - timedelta(hours=hours)
        return [e for e in self.events if datetime.fromisoformat(e["timestamp"]) >= cutoff]

    def get_event_summary(self, event_id: str) -> Optional[Dict]:
        filepath = os.path.join(self.data_dir, f"{event_id}.json")
        if os.path.exists(filepath):
            with open(filepath) as f:
                return json.load(f)
        for e in self.events:
            if e["event_id"] == event_id:
                return e
        return None

    def get_network_status(self) -> Dict:
        active = sum(1 for s in self.stations if s["status"] == "active")
        return {
            "total_stations": len(self.stations),
            "active_stations": active,
            "maintenance": len(self.stations) - active,
            "last_event": self.events[-1] if self.events else None,
            "events_processed": len(self.events)
        }

# 2026-03-22 13:57:29 weather data integration
