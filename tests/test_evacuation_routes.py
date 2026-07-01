import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evacuation_routes import EvacuationRouter

class TestEvacuationRoutes:
    def setup_method(self):
        self.router = EvacuationRouter()

    def test_plan_evacuation(self):
        result = self.router.plan_evacuation(26.2389, 73.0243, 100)
        assert result["success"]
        assert "evacuation_plan" in result
        assert result["evacuation_plan"]["population"] == 100

    def test_shelter_status(self):
        shelters = self.router.get_shelter_status()
        assert len(shelters) > 0
        assert "available" in shelters[0]
        assert "fill_pct" in shelters[0]

    def test_nearest_node(self):
        node = self.router._find_nearest_node(26.2389, 73.0243)
        assert node is not None
        assert isinstance(node, str)

    def test_dijkstra_route(self):
        route = self.router._dijkstra("N1", "N3")
        assert route is not None
        assert "total_distance_km" in route
        assert len(route["coordinates"]) > 0

    def test_no_available_shelters(self):
        for s in self.router.shelters:
            s["occupied"] = s["capacity"]
        result = self.router.plan_evacuation(26.2389, 73.0243, 10)
        assert not result["success"]
