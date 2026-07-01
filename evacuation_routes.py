import json
import logging
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import os
import heapq

logger = logging.getLogger(__name__)

class EvacuationRouter:
    TERRAIN_SPEED_FACTORS = {
        "highway": 60.0,
        "primary": 45.0,
        "secondary": 30.0,
        "residential": 20.0,
        "trail": 10.0,
        "offroad": 5.0,
        "flooded": 0.0
    }

    def __init__(self, data_dir: str = "data/evacuation"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.shelters = self._init_shelters()
        self.road_network = self._init_road_network()
        self.zone_risk_levels = {}

    def _init_shelters(self) -> List[Dict]:
        return [
            {"id": "SHEL001", "name": "Jodhpur Stadium", "lat": 26.2800, "lon": 73.0200, "capacity": 5000, "occupied": 0, "type": "primary"},
            {"id": "SHEL002", "name": "Jaipur Convention Center", "lat": 26.9200, "lon": 75.7900, "capacity": 8000, "occupied": 0, "type": "primary"},
            {"id": "SHEL003", "name": "Udaipur School Complex", "lat": 24.5900, "lon": 73.7200, "capacity": 3000, "occupied": 0, "type": "secondary"},
            {"id": "SHEL004", "name": "Bikaner Community Hall", "lat": 28.0200, "lon": 73.3200, "capacity": 2000, "occupied": 0, "type": "secondary"},
            {"id": "SHEL005", "name": "Kota Medical College", "lat": 25.1800, "lon": 75.8500, "capacity": 4000, "occupied": 0, "type": "primary"},
            {"id": "SHEL006", "name": "Ajmer Relief Camp", "lat": 26.4500, "lon": 74.6400, "capacity": 3500, "occupied": 0, "type": "secondary"}
        ]

    def _init_road_network(self) -> Dict:
        return {
            "nodes": [
                {"id": "N1", "lat": 26.2389, "lon": 73.0243},
                {"id": "N2", "lat": 26.2800, "lon": 73.0200},
                {"id": "N3", "lat": 26.9124, "lon": 75.7873},
                {"id": "N4", "lat": 26.9200, "lon": 75.7900},
                {"id": "N5", "lat": 24.5854, "lon": 73.7125},
                {"id": "N6", "lat": 24.5900, "lon": 73.7200},
                {"id": "N7", "lat": 28.0229, "lon": 73.3119},
                {"id": "N8", "lat": 28.0200, "lon": 73.3200},
                {"id": "N9", "lat": 25.2138, "lon": 75.8648},
                {"id": "N10", "lat": 25.1800, "lon": 75.8500},
                {"id": "N11", "lat": 26.4499, "lon": 74.6399},
                {"id": "N12", "lat": 26.4500, "lon": 74.6400}
            ],
            "edges": [
                {"from": "N1", "to": "N2", "distance_km": 5.0, "road_type": "primary"},
                {"from": "N1", "to": "N3", "distance_km": 300.0, "road_type": "highway"},
                {"from": "N3", "to": "N4", "distance_km": 2.0, "road_type": "primary"},
                {"from": "N3", "to": "N9", "distance_km": 200.0, "road_type": "highway"},
                {"from": "N3", "to": "N11", "distance_km": 150.0, "road_type": "secondary"},
                {"from": "N5", "to": "N6", "distance_km": 1.5, "road_type": "primary"},
                {"from": "N5", "to": "N1", "distance_km": 250.0, "road_type": "secondary"},
                {"from": "N7", "to": "N8", "distance_km": 1.0, "road_type": "primary"},
                {"from": "N7", "to": "N1", "distance_km": 250.0, "road_type": "secondary"},
                {"from": "N9", "to": "N10", "distance_km": 4.0, "road_type": "primary"},
                {"from": "N9", "to": "N3", "distance_km": 200.0, "road_type": "highway"},
                {"from": "N11", "to": "N12", "distance_km": 1.0, "road_type": "primary"},
                {"from": "N11", "to": "N3", "distance_km": 150.0, "road_type": "secondary"}
            ]
        }

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    def _find_nearest_node(self, lat: float, lon: float) -> str:
        best_node, best_dist = None, float('inf')
        for node in self.road_network["nodes"]:
            d = self._haversine(lat, lon, node["lat"], node["lon"])
            if d < best_dist:
                best_dist = d
                best_node = node["id"]
        return best_node

    def _dijkstra(self, start_node: str, end_node: str, blocked_edges: List[str] = None) -> Optional[Dict]:
        blocked = set(blocked_edges or [])
        adj = {n["id"]: [] for n in self.road_network["nodes"]}

        for edge in self.road_network["edges"]:
            edge_key = f"{edge['from']}-{edge['to']}"
            if edge_key in blocked:
                continue
            speed = self.TERRAIN_SPEED_FACTORS.get(edge["road_type"], 30)
            time_h = edge["distance_km"] / speed if speed > 0 else float('inf')
            adj[edge["from"]].append((edge["to"], time_h, edge["distance_km"], edge["road_type"]))
            adj[edge["to"]].append((edge["from"], time_h, edge["distance_km"], edge["road_type"]))

        dist = {n["id"]: float('inf') for n in self.road_network["nodes"]}
        prev = {n["id"]: None for n in self.road_network["nodes"]}
        dist[start_node] = 0
        pq = [(0, start_node)]

        while pq:
            d, node = heapq.heappop(pq)
            if node == end_node:
                break
            if d > dist[node]:
                continue
            for neighbor, time, dist_km, rtype in adj[node]:
                nd = d + time
                if nd < dist[neighbor]:
                    dist[neighbor] = nd
                    prev[neighbor] = (node, dist_km, rtype)
                    heapq.heappush(pq, (nd, neighbor))

        if dist[end_node] == float('inf'):
            return None

        path = []
        curr = end_node
        total_distance = 0
        while prev[curr] is not None:
            pnode, dkm, rtype = prev[curr]
            path.append({"from": pnode, "to": curr, "distance_km": dkm, "road_type": rtype})
            total_distance += dkm
            curr = pnode
        path.reverse()

        node_lookup = {n["id"]: n for n in self.road_network["nodes"]}
        coordinates = []
        waypoints = [start_node]
        for p in path:
            if p["from"] not in waypoints:
                waypoints.append(p["from"])
            coordinates.append({"lat": node_lookup[p["from"]]["lat"], "lon": node_lookup[p["from"]]["lon"]})
        coordinates.append({"lat": node_lookup[end_node]["lat"], "lon": node_lookup[end_node]["lon"]})

        return {
            "path": path,
            "coordinates": coordinates,
            "waypoints": waypoints,
            "total_distance_km": round(total_distance, 2),
            "estimated_time_hours": round(dist[end_node], 2),
            "estimated_time_minutes": round(dist[end_node] * 60, 1)
        }

    def plan_evacuation(self, origin_lat: float, origin_lon: float, population: int = 100, blocked_edges: List[str] = None) -> Dict:
        start_node = self._find_nearest_node(origin_lat, origin_lon)
        logger.info(f"Planning evacuation from node {start_node} for {population} people")

        available_shelters = [s for s in self.shelters if s["occupied"] < s["capacity"]]
        if not available_shelters:
            return {"success": False, "error": "No available shelters"}

        routes = []
        for shelter in available_shelters:
            end_node = self._find_nearest_node(shelter["lat"], shelter["lon"])
            result = self._dijkstra(start_node, end_node, blocked_edges)
            if result:
                remaining = shelter["capacity"] - shelter["occupied"]
                vehicles_needed = math.ceil(population / 50)
                routes.append({
                    "shelter": shelter,
                    "route": result,
                    "remaining_capacity": remaining,
                    "can_accommodate": remaining >= population,
                    "vehicles_needed": vehicles_needed
                })

        routes.sort(key=lambda r: r["route"]["estimated_time_minutes"])

        primary_route = None
        for r in routes:
            if r["can_accommodate"]:
                primary_route = r
                break
        primary_route = primary_route or (routes[0] if routes else None)

        if not primary_route:
            return {"success": False, "error": "No viable evacuation route found"}

        shelter_id = primary_route["shelter"]["id"]
        for s in self.shelters:
            if s["id"] == shelter_id:
                s["occupied"] = min(s["capacity"], s["occupied"] + population)

        return {
            "success": True,
            "evacuation_plan": {
                "primary_route": primary_route["route"],
                "destination": primary_route["shelter"],
                "population": population,
                "vehicles_needed": primary_route["vehicles_needed"],
                "estimated_time_minutes": primary_route["route"]["estimated_time_minutes"],
                "total_distance_km": primary_route["route"]["total_distance_km"]
            },
            "alternative_routes": [r["route"] for r in routes[1:4]],
            "shelter_occupancy": {s["id"]: {"capacity": s["capacity"], "occupied": s["occupied"]} for s in self.shelters}
        }

    def get_shelter_status(self) -> List[Dict]:
        return [{"id": s["id"], "name": s["name"], "capacity": s["capacity"], "occupied": s["occupied"],
                 "available": s["capacity"] - s["occupied"], "fill_pct": round(s["occupied"] / s["capacity"] * 100 if s["capacity"] > 0 else 0, 1)}
                for s in self.shelters]

    def block_road(self, edge_from: str, edge_to: str) -> str:
        block_id = f"BLK_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return block_id

    def get_risk_zone(self, lat: float, lon: float) -> str:
        key = f"{lat:.1f}_{lon:.1f}"
        return self.zone_risk_levels.get(key, "low")
