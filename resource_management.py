import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import uuid

logger = logging.getLogger(__name__)

class ResourceManager:
    RESOURCE_CATEGORIES = {
        "shelter": {"unit": "persons", "priority": 1},
        "food": {"unit": "meals", "priority": 1},
        "water": {"unit": "liters", "priority": 1},
        "medical": {"unit": "kits", "priority": 1},
        "rescue_team": {"unit": "teams", "priority": 2},
        "vehicle": {"unit": "units", "priority": 2},
        "heavy_machinery": {"unit": "units", "priority": 3},
        "communication": {"unit": "units", "priority": 3},
        "power_supply": {"unit": "generators", "priority": 2},
        "blankets": {"unit": "packs", "priority": 2},
        "clothing": {"unit": "packs", "priority": 3},
        "sanitation": {"unit": "kits", "priority": 2}
    }

    def __init__(self, data_dir: str = "data/resources"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.inventory = self._load_inventory()
        self.allocations = []
        self.depots = self._init_depots()

    def _init_depots(self) -> List[Dict]:
        return [
            {"id": "DEP001", "name": "Jodhpur Central Warehouse", "lat": 26.2389, "lon": 73.0243, "capacity": 50000, "current_load": 0, "status": "active"},
            {"id": "DEP002", "name": "Jaipur Relief Hub", "lat": 26.9124, "lon": 75.7873, "capacity": 75000, "current_load": 0, "status": "active"},
            {"id": "DEP003", "name": "Udaipur Forward Base", "lat": 24.5854, "lon": 73.7125, "capacity": 30000, "current_load": 0, "status": "active"},
            {"id": "DEP004", "name": "Bikaner Logistics Center", "lat": 28.0229, "lon": 73.3119, "capacity": 40000, "current_load": 0, "status": "standby"},
            {"id": "DEP005", "name": "Kota Emergency Depot", "lat": 25.2138, "lon": 75.8648, "capacity": 20000, "current_load": 0, "status": "active"},
            {"id": "DEP006", "name": "Ajmer Supply Point", "lat": 26.4499, "lon": 74.6399, "capacity": 25000, "current_load": 0, "status": "active"}
        ]

    def _load_inventory(self) -> Dict[str, Dict]:
        inv_file = os.path.join(self.data_dir, "inventory.json")
        if os.path.exists(inv_file):
            with open(inv_file) as f:
                return json.load(f)
        return self._init_inventory()

    def _init_inventory(self) -> Dict[str, Dict]:
        inv = {}
        for cat, info in self.RESOURCE_CATEGORIES.items():
            inv[cat] = {"total": 0, "allocated": 0, "reserved": 0, "available": 0, "unit": info["unit"]}
        return inv

    def add_resource(self, resource_type: str, quantity: int, depot_id: str = None) -> Dict:
        if resource_type not in self.RESOURCE_CATEGORIES:
            return {"success": False, "error": f"Unknown resource type: {resource_type}"}

        if depot_id and depot_id not in [d["id"] for d in self.depots]:
            return {"success": False, "error": f"Unknown depot: {depot_id}"}

        resource_id = str(uuid.uuid4())[:8]
        entry = {
            "id": resource_id,
            "type": resource_type,
            "quantity": quantity,
            "unit": self.RESOURCE_CATEGORIES[resource_type]["unit"],
            "depot_id": depot_id,
            "timestamp": datetime.now().isoformat(),
            "status": "available"
        }

        if resource_type not in self.inventory:
            self.inventory[resource_type] = {
                "total": 0, "allocated": 0, "reserved": 0, "available": 0,
                "unit": self.RESOURCE_CATEGORIES[resource_type]["unit"]
            }

        self.inventory[resource_type]["total"] += quantity
        self.inventory[resource_type]["available"] += quantity
        self._save_inventory()

        logger.info(f"Added {quantity} {resource_type} to depot {depot_id}")
        return {"success": True, "resource_id": resource_id, "entry": entry}

    def allocate_resources(self, disaster_id: str, resource_type: str, quantity: int, location: Dict) -> Dict:
        if resource_type not in self.inventory:
            return {"success": False, "error": f"No inventory for {resource_type}"}

        available = self.inventory[resource_type]["available"]
        if available < quantity:
            return {"success": False, "error": f"Insufficient {resource_type}: need {quantity}, have {available}"}

        nearest_depot = self._find_nearest_depot(location["lat"], location["lon"])
        allocation_id = str(uuid.uuid4())[:8]

        allocation = {
            "id": allocation_id,
            "disaster_id": disaster_id,
            "resource_type": resource_type,
            "quantity": quantity,
            "unit": self.RESOURCE_CATEGORIES[resource_type]["unit"],
            "source_depot": nearest_depot["id"],
            "destination": location,
            "status": "in_transit",
            "created_at": datetime.now().isoformat(),
            "estimated_arrival": None
        }

        self.inventory[resource_type]["available"] -= quantity
        self.inventory[resource_type]["allocated"] += quantity
        self.allocations.append(allocation)
        self._save_inventory()

        logger.info(f"Allocated {quantity} {resource_type} for disaster {disaster_id}")
        return {"success": True, "allocation": allocation}

    def _find_nearest_depot(self, lat: float, lon: float) -> Dict:
        import math
        best, best_dist = None, float('inf')
        for depot in self.depots:
            if depot["status"] != "active":
                continue
            d = math.sqrt((depot["lat"] - lat)**2 + (depot["lon"] - lon)**2)
            if d < best_dist:
                best_dist = d
                best = depot
        return best or self.depots[0]

    def release_resources(self, allocation_id: str) -> Dict:
        for alloc in self.allocations:
            if alloc["id"] == allocation_id:
                alloc["status"] = "completed"
                self.inventory[alloc["resource_type"]]["allocated"] -= alloc["quantity"]
                self.inventory[alloc["resource_type"]]["available"] += alloc["quantity"]
                self._save_inventory()
                return {"success": True, "allocation": alloc}
        return {"success": False, "error": "Allocation not found"}

    def get_inventory_summary(self) -> Dict:
        summary = {}
        for rtype, data in self.inventory.items():
            usage_pct = (data["allocated"] / data["total"] * 100) if data["total"] > 0 else 0
            summary[rtype] = {**data, "usage_percent": round(usage_pct, 1)}
        return summary

    def get_depot_status(self) -> List[Dict]:
        depot_status = []
        for depot in self.depots:
            total = sum(
                self.inventory[rt]["total"] for rt in self.inventory
                if any(a.get("source_depot") == depot["id"] for a in self.allocations)
            )
            depot_status.append({**depot, "current_load_pct": round((depot["current_load"] / depot["capacity"]) * 100 if depot["capacity"] > 0 else 0, 1)})
        return depot_status

    def get_active_allocations(self) -> List[Dict]:
        return [a for a in self.allocations if a["status"] in ("in_transit", "pending")]

    def _save_inventory(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(os.path.join(self.data_dir, "inventory.json"), 'w') as f:
            json.dump(self.inventory, f, indent=2)

# 2026-01-16 09:37:12 weather data integration

# 2026-03-06 19:10:18 weather data integration
