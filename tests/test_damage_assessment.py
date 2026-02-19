import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from damage_assessment import DamageAssessment

class TestDamageAssessment:
    def setup_method(self):
        self.da = DamageAssessment()

    def test_create_report(self):
        report = self.da.create_report("DIS001", {"lat": 26.0, "lon": 74.0}, 25.0)
        assert report["id"] is not None
        assert report["status"] == "initialized"

    def test_structural_assessment(self):
        report = self.da.create_report("DIS001", {"lat": 26.0, "lon": 74.0}, 25.0)
        result = self.da.assess_structural_damage(report["id"], 200, 12, 35, 60)
        assert result["success"]
        assert result["score"] > 0

    def test_composite_score(self):
        report = self.da.create_report("DIS001", {"lat": 26.0, "lon": 74.0}, 25.0)
        self.da.assess_structural_damage(report["id"], 100, 10, 20, 30)
        self.da.assess_infrastructure_damage(report["id"], 5, 1, 10, 2, 50)
        self.da.assess_social_impact(report["id"], 500, 2, 50, 2000, 10000)
        r = self.da.get_report(report["id"])
        assert r["composite_score"] is not None
        assert r["severity"] in ("critical", "severe", "moderate", "minor")

    def test_generate_summary(self):
        report = self.da.create_report("DIS001", {"lat": 26.0, "lon": 74.0}, 25.0)
        self.da.assess_structural_damage(report["id"], 100, 5, 15, 30)
        summary = self.da.generate_summary(report["id"])
        assert summary is not None
        assert "recommendation" in summary
        assert "severity" in summary

    def test_list_reports(self):
        self.da.create_report("DIS001", {"lat": 26.0, "lon": 74.0}, 10.0)
        reports = self.da.list_reports()
        assert len(reports) > 0
        assert "id" in reports[0]

    def test_economic_assessment(self):
        report = self.da.create_report("DIS001", {"lat": 26.0, "lon": 74.0}, 25.0)
        result = self.da.assess_economic_damage(report["id"], 500000, 200000, 100000, 300000)
        assert result["success"]
        assert result["details"]["total_economic_impact_usd"] == 1100000

# 2026-02-02 16:47:19 weather data integration

# 2026-02-19 11:47:00 weather data integration
