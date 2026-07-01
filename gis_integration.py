import json
import logging
import math
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class GISIntegration:
    def __init__(self):
        self.layers = {
            "base": {"name": "Base Map", "type": "raster", "active": True},
            "flood_risk": {"name": "Flood Risk Zones", "type": "vector", "active": True},
            "seismic": {"name": "Seismic Activity", "type": "point", "active": True},
            "weather": {"name": "Weather Overlay", "type": "raster", "active": True},
            "infrastructure": {"name": "Infrastructure", "type": "vector", "active": False},
            "evacuation": {"name": "Evacuation Routes", "type": "line", "active": False},
            "shelters": {"name": "Emergency Shelters", "type": "point", "active": True},
            "resources": {"name": "Resource Depots", "type": "point", "active": False},
            "damage": {"name": "Damage Assessment", "type": "polygon", "active": False}
        }
        self.geo_features = []
        self.buffers = {}

    def create_feature(self, feature_type: str, geometry: Dict, properties: Dict) -> Dict:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": geometry.get("type", "Point"),
                "coordinates": geometry.get("coordinates", [0, 0])
            },
            "properties": {
                **properties,
                "feature_type": feature_type,
                "created_at": datetime.now().isoformat()
            },
            "id": len(self.geo_features) + 1
        }
        self.geo_features.append(feature)
        return feature

    def create_geojson_collection(self, features: List[Dict] = None) -> Dict:
        return {
            "type": "FeatureCollection",
            "features": features or self.geo_features,
            "metadata": {
                "generated": datetime.now().isoformat(),
                "feature_count": len(features or self.geo_features),
                "crs": {"type": "name", "properties": {"name": "EPSG:4326"}}
            }
        }

    def create_buffer_zone(self, lat: float, lon: float, radius_km: float, zone_type: str) -> Dict:
        zone_id = f"BUF_{len(self.buffers) + 1:03d}"
        earth_radius = 6371.0
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        angular_radius = radius_km / earth_radius

        points = []
        for bearing in range(0, 360, 10):
            brng = math.radians(bearing)
            new_lat = math.asin(math.sin(lat_rad) * math.cos(angular_radius) +
                                math.cos(lat_rad) * math.sin(angular_radius) * math.cos(brng))
            new_lon = lon_rad + math.atan2(math.sin(brng) * math.sin(angular_radius) * math.cos(lat_rad),
                                           math.cos(angular_radius) - math.sin(lat_rad) * math.sin(new_lat))
            points.append([math.degrees(new_lon), math.degrees(new_lat)])
        points.append(points[0])

        zone = {
            "id": zone_id,
            "center": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "zone_type": zone_type,
            "created_at": datetime.now().isoformat(),
            "feature": {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [points]},
                "properties": {"zone_id": zone_id, "zone_type": zone_type, "radius_km": radius_km}
            }
        }
        self.buffers[zone_id] = zone
        return zone

    def spatial_query(self, lat: float, lon: float, radius_km: float, feature_types: List[str] = None) -> Dict:
        results = []
        for feat in self.geo_features:
            if feature_types and feat["properties"].get("feature_type") not in feature_types:
                continue
            coords = feat["geometry"]["coordinates"]
            if feat["geometry"]["type"] == "Point":
                feat_lat, feat_lon = coords[1], coords[0]
            elif feat["geometry"]["type"] == "Polygon":
                cent = self._polygon_centroid(coords[0])
                feat_lat, feat_lon = cent
            else:
                continue

            d = self._haversine(lat, lon, feat_lat, feat_lon)
            if d <= radius_km:
                results.append({**feat, "distance_km": round(d, 2)})
        results.sort(key=lambda x: x["distance_km"])
        return {"query": {"center": {"lat": lat, "lon": lon}, "radius_km": radius_km}, "results": results, "count": len(results)}

    def overlay_analysis(self, base_layer: str, overlay_layer: str, operation: str = "intersection") -> Dict:
        return {
            "base_layer": base_layer,
            "overlay_layer": overlay_layer,
            "operation": operation,
            "result": "Analysis requires actual spatial data engine (e.g., PostGIS, GeoPandas)",
            "estimated_features_affected": 0,
            "timestamp": datetime.now().isoformat()
        }

    def get_risk_heatmap_data(self, disaster_type: str = "flood") -> Dict:
        import random
        points = []
        base_lat, base_lon = 26.0, 74.0
        for _ in range(50):
            lat = base_lat + random.uniform(-3, 3)
            lon = base_lon + random.uniform(-3, 3)
            risk = random.uniform(0, 100)
            points.append({"lat": round(lat, 4), "lon": round(lon, 4), "risk_score": round(risk, 1)})
        return {"type": disaster_type, "points": points, "count": len(points)}

    def get_layer_status(self) -> Dict:
        return {k: {"name": v["name"], "type": v["type"], "active": v["active"]} for k, v in self.layers.items()}

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    def _polygon_centroid(self, coords: List) -> Tuple[float, float]:
        lon_sum = sum(c[0] for c in coords)
        lat_sum = sum(c[1] for c in coords)
        n = len(coords)
        return lat_sum / n, lon_sum / n
