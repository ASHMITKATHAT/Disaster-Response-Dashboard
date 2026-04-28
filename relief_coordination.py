import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import uuid

logger = logging.getLogger(__name__)

class ReliefCoordinator:
    OPERATION_PHASES = ["alert", "mobilization", "response", "recovery", "reconstruction"]

    def __init__(self, data_dir: str = "data/relief"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.operations = []
        self.volunteers = self._init_volunteers()
        self.supply_chains = []
        self.donations = []
        self.situation_reports = []

    def _init_volunteers(self) -> List[Dict]:
        return [
            {"id": "V001", "name": "Rahul Sharma", "phone": "+911111111111", "skills": ["first_aid", "rescue"], "lat": 26.2389, "lon": 73.0243, "status": "available", "rating": 4.5, "joined": "2025-06-01"},
            {"id": "V002", "name": "Priya Patel", "phone": "+911111111112", "skills": ["medical", "logistics"], "lat": 26.9124, "lon": 75.7873, "status": "available", "rating": 4.8, "joined": "2025-05-15"},
            {"id": "V003", "name": "Amit Singh", "phone": "+911111111113", "skills": ["driving", "heavy_machinery"], "lat": 24.5854, "lon": 73.7125, "status": "available", "rating": 4.2, "joined": "2025-07-01"},
            {"id": "V004", "name": "Sneha Verma", "phone": "+911111111114", "skills": ["communication", "coordination"], "lat": 28.0229, "lon": 73.3119, "status": "available", "rating": 4.6, "joined": "2025-08-01"},
            {"id": "V005", "name": "Vikram Joshi", "phone": "+911111111115", "skills": ["first_aid", "rescue", "driving"], "lat": 25.2138, "lon": 75.8648, "status": "available", "rating": 4.9, "joined": "2025-04-01"}
        ]

    def create_operation(self, disaster_id: str, op_type: str, location: Dict, severity: str) -> Dict:
        op_id = f"OP_{uuid.uuid4().hex[:8].upper()}"
        operation = {
            "id": op_id,
            "disaster_id": disaster_id,
            "type": op_type,
            "location": location,
            "severity": severity,
            "phase": "alert",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "assigned_volunteers": [],
            "assigned_resources": [],
            "situation_updates": [],
            "objectives": [],
            "metrics": {"people_helped": 0, "supplies_distributed": 0, "areas_cleared": 0}
        }
        self.operations.append(operation)
        self._save_operation(operation)
        logger.info(f"Created relief operation {op_id} for disaster {disaster_id}")
        return operation

    def assign_volunteer(self, operation_id: str, volunteer_id: str) -> Dict:
        op = self._find_operation(operation_id)
        if not op:
            return {"success": False, "error": "Operation not found"}
        vol = next((v for v in self.volunteers if v["id"] == volunteer_id), None)
        if not vol:
            return {"success": False, "error": "Volunteer not found"}
        if vol["status"] != "available":
            return {"success": False, "error": "Volunteer not available"}

        op["assigned_volunteers"].append(volunteer_id)
        vol["status"] = "deployed"
        return {"success": True, "operation_id": operation_id, "volunteer": vol}

    def update_operation_phase(self, operation_id: str, phase: str) -> Dict:
        if phase not in self.OPERATION_PHASES:
            return {"success": False, "error": f"Invalid phase. Must be one of {self.OPERATION_PHASES}"}
        op = self._find_operation(operation_id)
        if not op:
            return {"success": False, "error": "Operation not found"}

        op["phase"] = phase
        if phase == "mobilization":
            op["started_at"] = datetime.now().isoformat()
        elif phase == "reconstruction":
            op["completed_at"] = datetime.now().isoformat()
            op["status"] = "completed"

        return {"success": True, "operation": op}

    def add_situation_report(self, operation_id: str, report: Dict) -> Dict:
        op = self._find_operation(operation_id)
        if not op:
            return {"success": False, "error": "Operation not found"}

        report["id"] = f"SR_{uuid.uuid4().hex[:6].upper()}"
        report["timestamp"] = datetime.now().isoformat()
        op["situation_updates"].append(report)
        self.situation_reports.append(report)

        if "people_helped" in report:
            op["metrics"]["people_helped"] += report["people_helped"]
        if "supplies_distributed" in report:
            op["metrics"]["supplies_distributed"] += report["supplies_distributed"]

        return {"success": True, "report": report}

    def create_supply_chain(self, operation_id: str, source: Dict, destination: Dict,
                            items: List[Dict], priority: str = "normal") -> Dict:
        chain_id = f"SC_{uuid.uuid4().hex[:6].upper()}"
        chain = {
            "id": chain_id,
            "operation_id": operation_id,
            "source": source,
            "destination": destination,
            "items": items,
            "priority": priority,
            "status": "planned",
            "estimated_delivery": None,
            "actual_delivery": None,
            "created_at": datetime.now().isoformat(),
            "route": self._plan_route(source, destination),
            "tracking": []
        }
        self.supply_chains.append(chain)
        logger.info(f"Created supply chain {chain_id} for operation {operation_id}")
        return chain

    def _plan_route(self, source: Dict, destination: Dict) -> Dict:
        d = math.sqrt((source["lat"] - destination["lat"])**2 + (source["lon"] - destination["lon"])**2) * 111
        return {
            "distance_km": round(d, 1),
            "estimated_hours": round(d / 40, 1),
            "waypoints": [{"lat": source["lat"], "lon": source["lon"]}, {"lat": destination["lat"], "lon": destination["lon"]}]
        }

    def register_donation(self, donor_name: str, donor_type: str, items: List[Dict], value_usd: float = 0) -> Dict:
        donation_id = f"DON_{uuid.uuid4().hex[:6].upper()}"
        donation = {
            "id": donation_id,
            "donor_name": donor_name,
            "donor_type": donor_type,
            "items": items,
            "value_usd": value_usd,
            "status": "received",
            "timestamp": datetime.now().isoformat(),
            "dispatched_to": None
        }
        self.donations.append(donation)
        logger.info(f"Donation {donation_id} received from {donor_name}")
        return donation

    def find_nearest_volunteers(self, lat: float, lon: float, skill: str = None, top_k: int = 5) -> List[Dict]:
        available = [v for v in self.volunteers if v["status"] == "available"]
        if skill:
            available = [v for v in available if skill in v.get("skills", [])]

        scored = []
        for v in available:
            d = math.sqrt((v["lat"] - lat)**2 + (v["lon"] - lon)**2)
            scored.append((d, -v["rating"], v))
        scored.sort(key=lambda x: (x[0], x[1]))
        return [v for _, _, v in scored[:top_k]]

    def generate_operation_report(self, operation_id: str) -> Optional[Dict]:
        op = self._find_operation(operation_id)
        if not op:
            return None
        return {
            "operation_id": op["id"],
            "disaster_id": op["disaster_id"],
            "type": op["type"],
            "phase": op["phase"],
            "duration_hours": round((datetime.fromisoformat(op.get("completed_at") or datetime.now().isoformat()) - datetime.fromisoformat(op["created_at"])).total_seconds() / 3600, 1),
            "volunteers_deployed": len(op["assigned_volunteers"]),
            "resources_used": len(op["assigned_resources"]),
            "people_helped": op["metrics"]["people_helped"],
            "supplies_distributed": op["metrics"]["supplies_distributed"],
            "updates_count": len(op["situation_updates"]),
            "status": op["status"]
        }

    def get_active_operations(self) -> List[Dict]:
        return [op for op in self.operations if op["status"] in ("pending", "active")]

    def get_operations_summary(self) -> Dict:
        phase_counts = {}
        for op in self.operations:
            p = op["phase"]
            phase_counts[p] = phase_counts.get(p, 0) + 1
        total_helped = sum(op["metrics"]["people_helped"] for op in self.operations)
        total_supplies = sum(op["metrics"]["supplies_distributed"] for op in self.operations)
        return {
            "total_operations": len(self.operations),
            "active": len(self.get_active_operations()),
            "by_phase": phase_counts,
            "total_people_helped": total_helped,
            "total_supplies_distributed": total_supplies,
            "volunteers_available": sum(1 for v in self.volunteers if v["status"] == "available"),
            "volunteers_deployed": sum(1 for v in self.volunteers if v["status"] == "deployed"),
            "donations_received": len(self.donations),
            "supply_chains_active": len([sc for sc in self.supply_chains if sc["status"] in ("planned", "in_transit")])
        }

    def _find_operation(self, operation_id: str) -> Optional[Dict]:
        for op in self.operations:
            if op["id"] == operation_id:
                return op
        return None

    def _save_operation(self, operation: Dict):
        path = os.path.join(self.data_dir, f"{operation['id']}.json")
        with open(path, 'w') as f:
            json.dump(operation, f, indent=2)

# 2026-03-08 10:48:05 weather data integration

# 2026-04-28 18:23:30 weather data integration
