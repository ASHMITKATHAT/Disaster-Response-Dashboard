import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from relief_coordination import ReliefCoordinator

class TestReliefCoordination:
    def setup_method(self):
        self.rc = ReliefCoordinator()

    def test_create_operation(self):
        op = self.rc.create_operation("DIS001", "rescue", {"lat": 26.0, "lon": 74.0}, "high")
        assert op["id"] is not None
        assert op["phase"] == "alert"

    def test_assign_volunteer(self):
        op = self.rc.create_operation("DIS001", "rescue", {"lat": 26.0, "lon": 74.0}, "high")
        result = self.rc.assign_volunteer(op["id"], "V001")
        assert result["success"]

    def test_update_phase(self):
        op = self.rc.create_operation("DIS001", "rescue", {"lat": 26.0, "lon": 74.0}, "high")
        result = self.rc.update_operation_phase(op["id"], "mobilization")
        assert result["success"]
        assert result["operation"]["phase"] == "mobilization"

    def test_add_situation_report(self):
        op = self.rc.create_operation("DIS001", "rescue", {"lat": 26.0, "lon": 74.0}, "high")
        result = self.rc.add_situation_report(op["id"], {"people_helped": 50, "supplies_distributed": 200})
        assert result["success"]

    def test_find_volunteers(self):
        result = self.rc.find_nearest_volunteers(26.0, 74.0, "rescue")
        assert isinstance(result, list)

    def test_register_donation(self):
        result = self.rc.register_donation("Test Donor", "individual", [{"food": 100}], 5000)
        assert result["id"] is not None

    def test_operation_summary(self):
        self.rc.create_operation("DIS001", "rescue", {"lat": 26.0, "lon": 74.0}, "high")
        summary = self.rc.get_operations_summary()
        assert summary["total_operations"] > 0
        assert "total_people_helped" in summary
