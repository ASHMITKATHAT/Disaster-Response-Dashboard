import asyncio
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from collections import deque

logger = logging.getLogger(__name__)

class SeismicMonitor:
    def __init__(self, buffer_seconds: int = 60, sample_rate: int = 100):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_seconds * sample_rate
        self.buffers: Dict[str, deque] = {}
        self.callbacks: List[Callable] = []
        self.alert_thresholds = {
            "pga": {"yellow": 0.05, "orange": 0.15, "red": 0.35},
            "pgv": {"yellow": 2.0, "orange": 8.0, "red": 20.0}
        }
        self.monitoring = False
        self.stations = {}
        self.event_count = 0

    def register_station(self, station_id: str, lat: float, lon: float):
        self.stations[station_id] = {
            "id": station_id, "lat": lat, "lon": lon,
            "registered": datetime.now().isoformat(),
            "last_heartbeat": None, "status": "active"
        }
        self.buffers[station_id] = deque(maxlen=self.buffer_size)
        logger.info(f"Registered seismic station {station_id}")

    def ingest_waveform(self, station_id: str, samples: List[float], timestamp: float = None):
        if station_id not in self.buffers:
            logger.warning(f"Unknown station: {station_id}")
            return
        ts = timestamp or datetime.now().timestamp()
        for s in samples:
            self.buffers[station_id].append({"value": s, "timestamp": ts})
        if station_id in self.stations:
            self.stations[station_id]["last_heartbeat"] = datetime.now().isoformat()

    def compute_sta_lta(self, station_id: str, sta_window: int = 50, lta_window: int = 200) -> Optional[float]:
        if station_id not in self.buffers or len(self.buffers[station_id]) < lta_window:
            return None
        data = np.array([d["value"] for d in self.buffers[station_id]])
        abs_data = np.abs(data)
        sta = np.mean(abs_data[-sta_window:]) if len(abs_data) >= sta_window else np.mean(abs_data)
        lta = np.mean(abs_data[:lta_window])
        return sta / (lta + 1e-10)

    def detect_event(self, station_id: str, threshold: float = 4.0) -> bool:
        ratio = self.compute_sta_lta(station_id)
        return ratio is not None and ratio > threshold

    def estimate_magnitude(self, max_amplitude_m: float, distance_km: float) -> float:
        if max_amplitude_m <= 0 or distance_km <= 0:
            return 0.0
        return np.log10(max_amplitude_m * 1000) + 1.11 * np.log10(distance_km) + 0.00189 * distance_km - 2.09

    def get_peak_ground_acceleration(self, station_id: str, window_s: float = 5.0) -> Optional[float]:
        if station_id not in self.buffers or len(self.buffers[station_id]) == 0:
            return None
        window_samples = int(window_s * self.sample_rate)
        data = np.array([d["value"] for d in self.buffers[station_id]])
        if len(data) > window_samples:
            data = data[-window_samples:]
        return float(np.max(np.abs(data)))

    def get_current_alert_level(self, station_id: str) -> str:
        pga = self.get_peak_ground_acceleration(station_id)
        if pga is None:
            return "unknown"
        if pga >= self.alert_thresholds["pga"]["red"]:
            return "red"
        if pga >= self.alert_thresholds["pga"]["orange"]:
            return "orange"
        if pga >= self.alert_thresholds["pga"]["yellow"]:
            return "yellow"
        return "green"

    def register_callback(self, callback: Callable):
        self.callbacks.append(callback)

    def _notify_callbacks(self, event: Dict):
        for cb in self.callbacks:
            try:
                cb(event)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    async def monitor_loop(self, check_interval: float = 0.5):
        self.monitoring = True
        logger.info("Seismic monitoring loop started")

        while self.monitoring:
            for station_id in self.stations:
                if self.detect_event(station_id):
                    pga = self.get_peak_ground_acceleration(station_id)
                    alert_level = self.get_current_alert_level(station_id)

                    if alert_level != "green":
                        self.event_count += 1
                        event = {
                            "event_id": f"EVT_{self.event_count:06d}",
                            "station_id": station_id,
                            "timestamp": datetime.now().isoformat(),
                            "pga": pga,
                            "sta_lta_ratio": self.compute_sta_lta(station_id),
                            "alert_level": alert_level,
                            "magnitude": self.estimate_magnitude(pga or 0, 10)
                        }
                        self._notify_callbacks(event)

            await asyncio.sleep(check_interval)

    def stop(self):
        self.monitoring = False
        logger.info("Seismic monitoring stopped")

    def get_status(self) -> Dict:
        return {
            "monitoring": self.monitoring,
            "stations": len(self.stations),
            "active_stations": sum(1 for s in self.stations.values() if s["status"] == "active"),
            "event_count": self.event_count,
            "buffer_size_s": self.buffer_size // self.sample_rate,
            "sample_rate_hz": self.sample_rate
        }
