import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import uuid

logger = logging.getLogger(__name__)

class EmergencyContactManager:
    CONTACT_TYPES = {
        "police": {"priority": 1, "icon": "police"},
        "fire": {"priority": 1, "icon": "fire"},
        "ambulance": {"priority": 1, "icon": "medical"},
        "hospital": {"priority": 2, "icon": "hospital"},
        "disaster_response": {"priority": 1, "icon": "disaster"},
        "coast_guard": {"priority": 2, "icon": "coast"},
        "military": {"priority": 2, "icon": "military"},
        "ngo": {"priority": 3, "icon": "ngo"},
        "volunteer": {"priority": 3, "icon": "volunteer"},
        "government": {"priority": 2, "icon": "government"},
        "utility": {"priority": 3, "icon": "utility"},
        "shelter": {"priority": 2, "icon": "shelter"}
    }

    def __init__(self, data_dir: str = "data/contacts"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.contacts = self._load_contacts()
        self.contact_groups = {}
        self.incident_log = []

    def _load_contacts(self) -> List[Dict]:
        path = os.path.join(self.data_dir, "contacts.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return self._seed_contacts()

    def _seed_contacts(self) -> List[Dict]:
        seed = [
            {"id": "C001", "name": "Jodhpur Police Control Room", "type": "police", "phone": "+911234567890", "alternate_phone": "+911234567891", "email": "jodhpur.police@gov.in", "lat": 26.2389, "lon": 73.0243, "service_area": "Jodhpur District", "operational_hours": "24x7", "status": "available", "language": ["hi", "en", "mr"], "priority": 1, "last_contacted": None},
            {"id": "C002", "name": "Jaipur Fire Station", "type": "fire", "phone": "+911234567892", "alternate_phone": None, "email": "jaipur.fire@gov.in", "lat": 26.9124, "lon": 75.7873, "service_area": "Jaipur District", "operational_hours": "24x7", "status": "available", "language": ["hi", "en"], "priority": 1, "last_contacted": None},
            {"id": "C003", "name": "Jodhpur Civil Hospital", "type": "hospital", "phone": "+911234567893", "alternate_phone": "+911234567894", "email": "hospital.jodhpur@gov.in", "lat": 26.2400, "lon": 73.0200, "service_area": "Jodhpur Region", "operational_hours": "24x7", "status": "available", "capacity": 500, "current_patients": 320, "priority": 2, "last_contacted": None},
            {"id": "C004", "name": "NDRF Rajasthan Team", "type": "disaster_response", "phone": "+911234567895", "alternate_phone": None, "email": "ndrf.rajasthan@gov.in", "lat": 26.2500, "lon": 73.0500, "service_area": "Rajasthan State", "operational_hours": "24x7", "status": "ready", "teams_available": 3, "priority": 1, "last_contacted": None},
            {"id": "C005", "name": "Red Cross Rajasthan", "type": "ngo", "phone": "+911234567896", "alternate_phone": "+911234567897", "email": "redcross.rajasthan@redcross.in", "lat": 26.9000, "lon": 75.8000, "service_area": "Rajasthan State", "operational_hours": "08:00-20:00", "status": "available", "volunteers": 200, "priority": 3, "last_contacted": None},
            {"id": "C006", "name": "Rajasthan State Emergency Operations", "type": "government", "phone": "+911234567898", "alternate_phone": None, "email": "seoc.rajasthan@gov.in", "lat": 26.9200, "lon": 75.7800, "service_area": "Rajasthan State", "operational_hours": "24x7", "status": "active", "priority": 2, "last_contacted": None},
            {"id": "C007", "name": "Army Disaster Relief Unit", "type": "military", "phone": "+911234567899", "alternate_phone": None, "email": "army.disaster@mod.in", "lat": 26.3000, "lon": 73.0500, "service_area": "National", "operational_hours": "24x7", "status": "standby", "personnel_available": 500, "priority": 2, "last_contacted": None},
            {"id": "C008", "name": "Ambulance Network Jodhpur", "type": "ambulance", "phone": "108", "alternate_phone": "+911234567900", "email": None, "lat": 26.2350, "lon": 73.0250, "service_area": "Jodhpur District", "operational_hours": "24x7", "status": "available", "vehicles": 25, "priority": 1, "last_contacted": None}
        ]
        self._save_contacts(seed)
        return seed

    def _save_contacts(self, contacts: List[Dict] = None):
        path = os.path.join(self.data_dir, "contacts.json")
        with open(path, 'w') as f:
            json.dump(contacts or self.contacts, f, indent=2)

    def add_contact(self, contact: Dict) -> Dict:
        contact["id"] = f"C{len(self.contacts) + 1:03d}"
        contact["last_contacted"] = None
        self.contacts.append(contact)
        self._save_contacts()
        return {"success": True, "contact": contact}

    def update_contact(self, contact_id: str, updates: Dict) -> Dict:
        for c in self.contacts:
            if c["id"] == contact_id:
                c.update(updates)
                self._save_contacts()
                return {"success": True, "contact": c}
        return {"success": False, "error": "Contact not found"}

    def get_contacts_by_type(self, contact_type: str) -> List[Dict]:
        return [c for c in self.contacts if c["type"] == contact_type]

    def get_contacts_by_service_area(self, area: str) -> List[Dict]:
        return [c for c in self.contacts if area.lower() in c.get("service_area", "").lower()]

    def get_nearest_contacts(self, lat: float, lon: float, top_k: int = 5, contact_types: List[str] = None) -> List[Dict]:
        import math
        scored = []
        for c in self.contacts:
            if contact_types and c["type"] not in contact_types:
                continue
            if c["status"] not in ("available", "active", "ready"):
                continue
            d = math.sqrt((c["lat"] - lat)**2 + (c["lon"] - lon)**2)
            priority_score = 100 / (c.get("priority", 3) + 1)
            scored.append((d, priority_score, c))
        scored.sort(key=lambda x: (x[0], -x[1]))
        return [c for _, _, c in scored[:top_k]]

    def log_contact_attempt(self, contact_id: str, disaster_id: str, method: str = "phone", status: str = "success", notes: str = "") -> Dict:
        log = {
            "id": str(uuid.uuid4())[:8],
            "contact_id": contact_id,
            "disaster_id": disaster_id,
            "method": method,
            "status": status,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        self.incident_log.append(log)
        for c in self.contacts:
            if c["id"] == contact_id:
                c["last_contacted"] = datetime.now().isoformat()
                break
        return {"success": True, "log": log}

    def create_contact_group(self, name: str, contact_ids: List[str]) -> Dict:
        group_id = f"GRP_{uuid.uuid4().hex[:6].upper()}"
        members = [c for c in self.contacts if c["id"] in contact_ids]
        self.contact_groups[group_id] = {"id": group_id, "name": name, "members": members, "created": datetime.now().isoformat()}
        return {"success": True, "group": self.contact_groups[group_id]}

    def broadcast_to_group(self, group_id: str, message: str, disaster_id: str) -> Dict:
        group = self.contact_groups.get(group_id)
        if not group:
            return {"success": False, "error": "Group not found"}
        results = []
        for member in group["members"]:
            res = self.log_contact_attempt(member["id"], disaster_id, "broadcast", "sent", message[:100])
            results.append(res)
        return {"success": True, "broadcast": {"group": group_id, "contacts_reached": len(results), "results": results}}

    def get_emergency_hotline(self, contact_type: str = None) -> List[Dict]:
        national_numbers = {
            "police": "100", "fire": "101", "ambulance": "102", "disaster_response": "108",
            "women_helpline": "1091", "child_helpline": "1098"
        }
        hotlines = []
        if contact_type and contact_type in national_numbers:
            hotlines.append({"type": contact_type, "number": national_numbers[contact_type], "national": True})
        elif not contact_type:
            for ctype, number in national_numbers.items():
                hotlines.append({"type": ctype, "number": number, "national": True})
        local = [{"type": c["type"], "name": c["name"], "number": c["phone"], "area": c["service_area"]} for c in self.contacts if c.get("priority", 3) <= 2]
        return {"national_hotlines": hotlines, "local_contacts": local}

    def get_contacts_summary(self) -> Dict:
        type_counts = {}
        for c in self.contacts:
            t = c["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        status_counts = {}
        for c in self.contacts:
            s = c["status"]
            status_counts[s] = status_counts.get(s, 0) + 1
        return {"total_contacts": len(self.contacts), "by_type": type_counts, "by_status": status_counts, "groups": len(self.contact_groups), "recent_incidents": len(self.incident_log)}

    def search_contacts(self, query: str) -> List[Dict]:
        q = query.lower()
        return [c for c in self.contacts if q in c["name"].lower() or q in c.get("service_area", "").lower() or q in c.get("phone", "")]
