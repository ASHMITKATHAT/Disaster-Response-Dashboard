import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from emergency_contacts import EmergencyContactManager

class TestEmergencyContacts:
    def setup_method(self):
        self.ecm = EmergencyContactManager()

    def test_contacts_loaded(self):
        assert len(self.ecm.contacts) > 0
        assert all("id" in c for c in self.ecm.contacts)

    def test_get_by_type(self):
        police = self.ecm.get_contacts_by_type("police")
        assert len(police) > 0
        assert police[0]["type"] == "police"

    def test_get_nearest_contacts(self):
        result = self.ecm.get_nearest_contacts(26.2389, 73.0243, top_k=3)
        assert len(result) <= 3
        assert result[0]["status"] in ("available", "active", "ready")

    def test_hotlines(self):
        hotlines = self.ecm.get_emergency_hotline()
        assert "national_hotlines" in hotlines
        assert "local_contacts" in hotlines

    def test_contact_summary(self):
        summary = self.ecm.get_contacts_summary()
        assert summary["total_contacts"] > 0
        assert "by_type" in summary

    def test_search_contacts(self):
        results = self.ecm.search_contacts("Jodhpur")
        assert len(results) > 0
        assert "Jodhpur" in results[0]["name"] or "Jodhpur" in results[0].get("service_area", "")

    def test_log_contact_attempt(self):
        result = self.ecm.log_contact_attempt("C001", "DIS001", "phone", "success", "Test call")
        assert result["success"]
        assert len(self.ecm.incident_log) > 0

// 2026-01-26 10:27:12 UI component update
