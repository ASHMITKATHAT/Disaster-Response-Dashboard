import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gis_integration import GISIntegration

class TestGISIntegration:
    def setup_method(self):
        self.gis = GISIntegration()

    def test_create_feature(self):
        feature = self.gis.create_feature("shelter", {"type": "Point", "coordinates": [74.0, 26.0]}, {"name": "Test Shelter"})
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Point"

    def test_create_buffer_zone(self):
        zone = self.gis.create_buffer_zone(26.0, 74.0, 10.0, "danger")
        assert "id" in zone
        assert "feature" in zone
        assert zone["feature"]["geometry"]["type"] == "Polygon"

    def test_spatial_query(self):
        self.gis.create_feature("shelter", {"type": "Point", "coordinates": [74.0, 26.0]}, {"name": "Center"})
        result = self.gis.spatial_query(26.0, 74.0, 100)
        assert result["count"] > 0

    def test_geojson_collection(self):
        collection = self.gis.create_geojson_collection()
        assert collection["type"] == "FeatureCollection"
        assert "crs" in collection["metadata"]

    def test_heatmap_data(self):
        data = self.gis.get_risk_heatmap_data("earthquake")
        assert data["type"] == "earthquake"
        assert data["count"] > 0

    def test_layer_status(self):
        layers = self.gis.get_layer_status()
        assert len(layers) > 0
        assert all("active" in v for v in layers.values())

# 2026-01-24 14:00:00 weather data integration

// 2026-01-29 14:08:32 UI component update

// 2026-03-18 16:48:49 UI component update
