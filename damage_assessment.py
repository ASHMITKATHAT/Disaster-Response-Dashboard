import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import uuid

logger = logging.getLogger(__name__)

class DamageAssessment:
    DAMAGE_CATEGORIES = {
        "structural": {"weight": 0.35, "max_score": 100},
        "infrastructure": {"weight": 0.25, "max_score": 100},
        "environmental": {"weight": 0.15, "max_score": 100},
        "economic": {"weight": 0.15, "max_score": 100},
        "social": {"weight": 0.10, "max_score": 100}
    }

    def __init__(self, data_dir: str = "data/damage_reports"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.reports = []

    def create_report(self, disaster_id: str, location: Dict, affected_area_sq_km: float) -> Dict:
        report_id = f"DR_{uuid.uuid4().hex[:6].upper()}"
        report = {
            "id": report_id,
            "disaster_id": disaster_id,
            "location": location,
            "affected_area_sq_km": affected_area_sq_km,
            "timestamp": datetime.now().isoformat(),
            "status": "initialized",
            "assessments": {},
            "composite_score": None,
            "severity": None
        }
        self.reports.append(report)
        logger.info(f"Created damage assessment report {report_id}")
        return report

    def assess_structural_damage(self, report_id: str, buildings_inspected: int,
                                 collapsed: int, partial_damage: int, minor_damage: int) -> Dict:
        if buildings_inspected == 0:
            return {"error": "No buildings inspected"}
        score = ((collapsed * 100 + partial_damage * 50 + minor_damage * 20) / buildings_inspected)
        score = min(100, score)
        details = {
            "buildings_inspected": buildings_inspected,
            "collapsed": collapsed,
            "partial_damage": partial_damage,
            "minor_damage": minor_damage,
            "damage_rate": round((collapsed + partial_damage) / buildings_inspected * 100, 1)
        }
        self._update_assessment(report_id, "structural", score, details)
        return {"success": True, "category": "structural", "score": score, "details": details}

    def assess_infrastructure_damage(self, report_id: str, roads_affected: int,
                                     bridges_damaged: int, power_lines_down: int,
                                     water_systems_affected: int, total_roads: int) -> Dict:
        if total_roads == 0:
            return {"error": "No infrastructure data"}
        score = ((roads_affected * 30 + bridges_damaged * 100 + power_lines_down * 20 + water_systems_affected * 50) / total_roads)
        score = min(100, score)
        details = {
            "roads_affected": roads_affected,
            "bridges_damaged": bridges_damaged,
            "power_lines_down": power_lines_down,
            "water_systems_affected": water_systems_affected,
            "infrastructure_damage_rate": round(roads_affected / total_roads * 100, 1)
        }
        self._update_assessment(report_id, "infrastructure", score, details)
        return {"success": True, "category": "infrastructure", "score": score, "details": details}

    def assess_environmental_damage(self, report_id: str, area_burned_sq_km: float,
                                    trees_destroyed: int, water_contaminated: bool,
                                    soil_erosion_severity: str, wildlife_affected: int) -> Dict:
        severity_map = {"none": 0, "minor": 20, "moderate": 50, "severe": 80, "extreme": 100}
        erosion_score = severity_map.get(soil_erosion_severity, 50)
        score = (min(100, area_burned_sq_km * 10) * 0.3 + min(100, trees_destroyed / 100) * 0.2 +
                 (100 if water_contaminated else 0) * 0.3 + erosion_score * 0.1 +
                 min(100, wildlife_affected * 5) * 0.1)
        score = min(100, score)
        details = {
            "area_burned_sq_km": area_burned_sq_km,
            "trees_destroyed": trees_destroyed,
            "water_contaminated": water_contaminated,
            "soil_erosion_severity": soil_erosion_severity,
            "wildlife_affected": wildlife_affected
        }
        self._update_assessment(report_id, "environmental", score, details)
        return {"success": True, "category": "environmental", "score": score, "details": details}

    def assess_economic_damage(self, report_id: str, property_damage_usd: float,
                               crop_damage_usd: float, business_loss_usd: float,
                               infrastructure_cost_usd: float) -> Dict:
        total = property_damage_usd + crop_damage_usd + business_loss_usd + infrastructure_cost_usd
        score = min(100, total / 100000)
        details = {
            "property_damage_usd": property_damage_usd,
            "crop_damage_usd": crop_damage_usd,
            "business_loss_usd": business_loss_usd,
            "infrastructure_cost_usd": infrastructure_cost_usd,
            "total_economic_impact_usd": total
        }
        self._update_assessment(report_id, "economic", score, details)
        return {"success": True, "category": "economic", "score": score, "details": details}

    def assess_social_impact(self, report_id: str, displaced_population: int,
                             casualties: int, injured: int, affected_population: int,
                             total_population: int) -> Dict:
        if total_population == 0:
            return {"error": "No population data"}
        score = ((displaced_population * 30 + casualties * 100 + injured * 50) / total_population)
        score = min(100, score)
        details = {
            "displaced_population": displaced_population,
            "casualties": casualties,
            "injured": injured,
            "affected_population": affected_population,
            "displacement_rate": round(displaced_population / total_population * 100, 1)
        }
        self._update_assessment(report_id, "social", score, details)
        return {"success": True, "category": "social", "score": score, "details": details}

    def _update_assessment(self, report_id: str, category: str, score: float, details: Dict):
        for r in self.reports:
            if r["id"] == report_id:
                r["assessments"][category] = {"score": round(score, 1), "details": details}
                r["composite_score"] = self._compute_composite(report_id)
                r["status"] = "assessed"
                r["severity"] = self._classify_severity(r["composite_score"])
                self._save_report(r)
                break

    def _compute_composite(self, report_id: str) -> float:
        for r in self.reports:
            if r["id"] == report_id:
                if not r["assessments"]:
                    return 0
                total = 0
                for cat, info in self.DAMAGE_CATEGORIES.items():
                    if cat in r["assessments"]:
                        total += r["assessments"][cat]["score"] * info["weight"]
                return round(total, 1)
        return 0

    def _classify_severity(self, score: float) -> str:
        if score is None:
            return "unknown"
        if score >= 75:
            return "critical"
        if score >= 50:
            return "severe"
        if score >= 25:
            return "moderate"
        return "minor"

    def _save_report(self, report: Dict):
        path = os.path.join(self.data_dir, f"{report['id']}.json")
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)

    def get_report(self, report_id: str) -> Optional[Dict]:
        for r in self.reports:
            if r["id"] == report_id:
                return r
        path = os.path.join(self.data_dir, f"{report_id}.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None

    def generate_summary(self, report_id: str) -> Optional[Dict]:
        report = self.get_report(report_id)
        if not report:
            return None

        assessments = report.get("assessments", {})
        worst_category = max(assessments.items(), key=lambda x: x[1]["score"]) if assessments else ("none", {"score": 0})

        return {
            "report_id": report_id,
            "disaster_id": report["disaster_id"],
            "composite_score": report["composite_score"],
            "severity": report["severity"],
            "worst_category": {"category": worst_category[0], "score": worst_category[1]["score"]},
            "categories_assessed": list(assessments.keys()),
            "location": report["location"],
            "affected_area_sq_km": report["affected_area_sq_km"],
            "recommendation": "Full evacuation" if report["composite_score"] and report["composite_score"] >= 75 else
                              "Partial evacuation" if report["composite_score"] and report["composite_score"] >= 50 else
                              "Prepare for evacuation" if report["composite_score"] and report["composite_score"] >= 25 else
                              "Monitor situation"
        }

    def list_reports(self, status: str = None) -> List[Dict]:
        results = self.reports
        if status:
            results = [r for r in results if r["status"] == status]
        return [{"id": r["id"], "disaster_id": r["disaster_id"], "severity": r["severity"],
                 "composite_score": r["composite_score"], "timestamp": r["timestamp"]} for r in results]

# 2026-01-19 11:33:30 weather data integration

// 2026-02-11 16:33:01 UI component update

// 2026-05-09 15:51:02 UI component update

# 2026-05-23 09:32:09 weather data integration
