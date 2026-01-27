import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from resource_management import ResourceManager

class TestResourceManagement:
    def setup_method(self):
        self.rm = ResourceManager()

    def test_add_resource(self):
        result = self.rm.add_resource("food", 1000, "DEP001")
        assert result["success"]
        assert self.rm.inventory["food"]["total"] > 0

    def test_allocate_resources(self):
        self.rm.add_resource("water", 5000, "DEP001")
        result = self.rm.allocate_resources("DIS001", "water", 100, {"lat": 26.0, "lon": 74.0})
        assert result["success"]
        assert result["allocation"]["status"] == "in_transit"

    def test_insufficient_resources(self):
        result = self.rm.allocate_resources("DIS001", "medical", 99999, {"lat": 26.0, "lon": 74.0})
        assert not result["success"]
        assert "Insufficient" in result.get("error", "")

    def test_release_resources(self):
        self.rm.add_resource("blankets", 2000, "DEP001")
        alloc = self.rm.allocate_resources("DIS001", "blankets", 100, {"lat": 26.0, "lon": 74.0})
        result = self.rm.release_resources(alloc["allocation"]["id"])
        assert result["success"]

    def test_invalid_resource_type(self):
        result = self.rm.add_resource("invalid_type", 100, "DEP001")
        assert not result["success"]

    def test_inventory_summary(self):
        summary = self.rm.get_inventory_summary()
        assert "food" in summary
        assert "usage_percent" in summary["food"]

    def test_depot_status(self):
        status = self.rm.get_depot_status()
        assert len(status) > 0
        assert "current_load_pct" in status[0]

    def test_find_nearest_depot(self):
        self.rm.add_resource("water", 1000, "DEP001")
        result = self.rm.allocate_resources("DIS001", "water", 10, {"lat": 26.0, "lon": 74.0})
        assert result["success"]

# 2026-01-27 19:48:45 weather data integration
