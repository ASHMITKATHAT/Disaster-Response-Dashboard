import logging
from flask import Blueprint, request, jsonify
from datetime import datetime

from relief_coordination import ReliefCoordinator
from resource_management import ResourceManager
from damage_assessment import DamageAssessment
from emergency_contacts import EmergencyContactManager
from evacuation_routes import EvacuationRouter

logger = logging.getLogger(__name__)

relief_bp = Blueprint('relief', __name__, url_prefix='/api/relief')
rc = ReliefCoordinator()
rm = ResourceManager()
da = DamageAssessment()
ecm = EmergencyContactManager()
evac = EvacuationRouter()

@relief_bp.route('/operations', methods=['GET'])
def list_operations():
    status = request.args.get('status')
    ops = rc.get_active_operations() if not status else [o for o in rc.operations if o.get('status') == status]
    return jsonify({"success": True, "count": len(ops), "operations": ops})

@relief_bp.route('/operations', methods=['POST'])
def create_operation():
    data = request.get_json()
    op = rc.create_operation(
        data.get('disaster_id', 'DISASTER001'),
        data.get('type', 'general'),
        data.get('location', {"lat": 26.0, "lon": 74.0}),
        data.get('severity', 'moderate')
    )
    return jsonify({"success": True, "operation": op})

@relief_bp.route('/operations/<op_id>/phase', methods=['PUT'])
def update_phase(op_id):
    data = request.get_json()
    result = rc.update_operation_phase(op_id, data.get('phase', 'response'))
    return jsonify(result)

@relief_bp.route('/volunteers', methods=['GET'])
def find_volunteers():
    lat = request.args.get('lat', 26.0, type=float)
    lon = request.args.get('lon', 74.0, type=float)
    skill = request.args.get('skill')
    volunteers = rc.find_nearest_volunteers(lat, lon, skill)
    return jsonify({"success": True, "count": len(volunteers), "volunteers": volunteers})

@relief_bp.route('/resources', methods=['GET'])
def get_resources():
    summary = rm.get_inventory_summary()
    depots = rm.get_depot_status()
    return jsonify({"success": True, "inventory": summary, "depots": depots})

@relief_bp.route('/resources/allocate', methods=['POST'])
def allocate_resource():
    data = request.get_json()
    result = rm.allocate_resources(
        data.get('disaster_id', 'DISASTER001'),
        data.get('resource_type', 'food'),
        data.get('quantity', 100),
        data.get('location', {"lat": 26.0, "lon": 74.0})
    )
    return jsonify(result)

@relief_bp.route('/damage', methods=['POST'])
def create_damage_report():
    data = request.get_json()
    report = da.create_report(
        data.get('disaster_id', 'DISASTER001'),
        data.get('location', {"lat": 26.0, "lon": 74.0}),
        data.get('area_sq_km', 10)
    )
    return jsonify({"success": True, "report": report})

@relief_bp.route('/damage/<report_id>/assess', methods=['POST'])
def assess_damage(report_id):
    data = request.get_json()
    category = data.get('category', 'structural')
    if category == 'structural':
        result = da.assess_structural_damage(report_id, data.get('buildings_inspected', 100), data.get('collapsed', 5), data.get('partial_damage', 15), data.get('minor_damage', 30))
    elif category == 'infrastructure':
        result = da.assess_infrastructure_damage(report_id, data.get('roads_affected', 10), data.get('bridges_damaged', 2), data.get('power_lines_down', 20), data.get('water_systems_affected', 3), data.get('total_roads', 50))
    elif category == 'environmental':
        result = da.assess_environmental_damage(report_id, data.get('area_burned', 0), data.get('trees_destroyed', 0), data.get('water_contaminated', False), data.get('soil_erosion', 'none'), data.get('wildlife_affected', 0))
    elif category == 'economic':
        result = da.assess_economic_damage(report_id, data.get('property_damage', 0), data.get('crop_damage', 0), data.get('business_loss', 0), data.get('infrastructure_cost', 0))
    elif category == 'social':
        result = da.assess_social_impact(report_id, data.get('displaced', 100), data.get('casualties', 0), data.get('injured', 10), data.get('affected', 500), data.get('total_population', 10000))
    else:
        return jsonify({"success": False, "error": "Invalid category"}), 400
    return jsonify({"success": True, "assessment": result})

@relief_bp.route('/damage/<report_id>/summary', methods=['GET'])
def get_damage_summary(report_id):
    summary = da.generate_summary(report_id)
    if summary:
        return jsonify({"success": True, "summary": summary})
    return jsonify({"success": False, "error": "Report not found"}), 404

@relief_bp.route('/contacts', methods=['GET'])
def get_contacts():
    contact_type = request.args.get('type')
    area = request.args.get('area')
    if contact_type:
        contacts = ecm.get_contacts_by_type(contact_type)
    elif area:
        contacts = ecm.get_contacts_by_service_area(area)
    else:
        contacts = ecm.contacts
    return jsonify({"success": True, "count": len(contacts), "contacts": contacts})

@relief_bp.route('/contacts/nearby', methods=['GET'])
def get_nearby_contacts():
    lat = request.args.get('lat', 26.0, type=float)
    lon = request.args.get('lon', 74.0, type=float)
    types = request.args.get('types', '').split(',') if request.args.get('types') else None
    contacts = ecm.get_nearest_contacts(lat, lon, top_k=10, contact_types=types)
    return jsonify({"success": True, "count": len(contacts), "contacts": contacts})

@relief_bp.route('/contacts/hotlines', methods=['GET'])
def get_hotlines():
    contact_type = request.args.get('type')
    hotlines = ecm.get_emergency_hotline(contact_type)
    return jsonify({"success": True, "hotlines": hotlines})

@relief_bp.route('/evacuation/plan', methods=['POST'])
def plan_evacuation():
    data = request.get_json()
    result = evac.plan_evacuation(
        data.get('lat', 26.0), data.get('lon', 74.0),
        data.get('population', 100),
        data.get('blocked_edges')
    )
    return jsonify(result)

@relief_bp.route('/evacuation/shelters', methods=['GET'])
def get_shelters():
    shelters = evac.get_shelter_status()
    return jsonify({"success": True, "shelters": shelters})

@relief_bp.route('/summary', methods=['GET'])
def get_relief_summary():
    operations_summary = rc.get_operations_summary()
    inventory = rm.get_inventory_summary()
    contacts_summary = ecm.get_contacts_summary()
    return jsonify({
        "success": True,
        "data": {
            "operations": operations_summary,
            "inventory": inventory,
            "contacts": contacts_summary
        }
    })

# 2026-01-08 19:53:50 weather data integration

// 2026-02-04 16:14:04 UI component update
