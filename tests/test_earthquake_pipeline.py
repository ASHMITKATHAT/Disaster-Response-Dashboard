import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from earthquake_pipeline import EarthquakeDataPipeline

class TestEarthquakePipeline:
    def setup_method(self):
        self.pipeline = EarthquakeDataPipeline()

    def test_waveform_analysis(self):
        data = np.random.randn(1000) * 0.01
        data[200:400] += np.sin(np.linspace(0, 20*np.pi, 200)) * 0.1
        result = self.pipeline.process_seismic_waveform(data, 100)
        assert result is not None
        assert "rms_amplitude" in result
        assert "peak_amplitude" in result
        assert result["peak_amplitude"] > result["rms_amplitude"]

    def test_magnitude_calculation(self):
        result = self.pipeline.calculate_magnitude(10.0, 50.0, 10.0)
        assert "local_magnitude_ml" in result
        assert "classification" in result
        assert result["local_magnitude_ml"] > 0

    def test_shaking_intensity(self):
        result = self.pipeline.assess_shaking_intensity(6.0, 30.0, 10.0)
        assert "mmi" in result
        assert "pga_g" in result
        assert "damage_level" in result

    def test_empty_waveform(self):
        data = np.array([])
        result = self.pipeline.process_seismic_waveform(data, 100)
        assert "error" in result

    def test_epicenter_location_insufficient_stations(self):
        result = self.pipeline.locate_epicenter([])
        assert "error" in result

    def test_station_loading(self):
        assert len(self.pipeline.stations) > 0
        assert all("id" in s for s in self.pipeline.stations)

    def test_magnitude_classification(self):
        result = self.pipeline.calculate_magnitude(1.0, 10.0, 5.0)
        assert result["classification"] in self.pipeline.MAGNITUDE_CLASSES

    def test_full_event_processing(self):
        wf_data = np.random.randn(1000) * 0.01
        wf_data[200:400] += np.sin(np.linspace(0, 20*np.pi, 200)) * 0.1
        waveforms = [{"data": wf_data.tolist(), "sample_rate": 100, "station_id": "STN001"}]
        stations = [{"id": "STN001", "lat": 26.2389, "lon": 73.0243, "p_arrival": 1.0, "s_arrival": 3.5}]
        event = self.pipeline.process_event(waveforms, stations)
        assert "event_id" in event
        assert "magnitude" in event
        assert "intensity" in event
