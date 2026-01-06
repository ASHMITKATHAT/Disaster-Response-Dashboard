"""
EQUINOX Flood Prediction System - Main Flask Application
Simplified version with minimal dependencies
"""

import os
import json
import numpy as np
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
from pathlib import Path
from extended_api import register_extended_routes

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register extended API routes (v2)
register_extended_routes(app)

# Configuration
MODELS_DIR = Path("backend/models")
DATA_DIR = Path("backend/data")

# Load ML model on startup (if exists)
ml_model = None
scaler = None
encoder = None

def load_ml_model():
    """Load ML model and preprocessing objects"""
    global ml_model, scaler, encoder
    
    try:
        model_path = MODELS_DIR / "flood_models.pkl"
        if model_path.exists():
            models = joblib.load(model_path)
            ml_model = models.get('rf')  # Use RandomForest by default
            scaler = models.get('scaler')
            encoder = models.get('encoder')
            print(f"✅ Loaded ML model: {type(ml_model).__name__}")
        else:
            print("⚠️  ML model not found. Running in simulation mode.")
    except Exception as e:
        print(f"❌ Error loading ML model: {str(e)}")

# Load model on startup
load_ml_model()

# Helper functions
def get_sample_villages():
    """Get sample village data"""
    return [
        {
            "id": "v001",
            "name": "Khejarla Village",
            "district": "Jodhpur",
            "coordinates": [26.9124, 75.7873],
            "population": 3200,
            "elevation": 250.5,
            "flood_risk": "HIGH"
        },
        {
            "id": "v002",
            "name": "Bilara Village",
            "district": "Jodhpur",
            "coordinates": [26.1808, 73.7052],
            "population": 2800,
            "elevation": 230.2,
            "flood_risk": "MODERATE"
        },
        {
            "id": "v003",
            "name": "Phalodi Village",
            "district": "Jodhpur",
            "coordinates": [27.1322, 72.3680],
            "population": 1800,
            "elevation": 210.8,
            "flood_risk": "LOW"
        }
    ]

def simulate_prediction(rainfall_mm, slope_degrees, soil_type, flow_accumulation):
    """Simulate flood prediction (fallback when ML model not available)"""
    # Simple simulation based on physics
    base_depth = rainfall_mm * 0.02  # 2cm per 1mm rain
    
    # Adjust for slope
    if slope_degrees < 5:
        base_depth *= 1.5  # Flat areas accumulate more water
    elif slope_degrees > 15:
        base_depth *= 0.5  # Steep slopes drain faster
    
    # Adjust for soil type
    soil_factors = {
        'clay': 1.3,
        'sandy': 0.7,
        'loamy': 1.0,
        'rocky': 0.5
    }
    soil_factor = soil_factors.get(soil_type.lower(), 1.0)
    
    # Adjust for flow accumulation
    flow_factor = min(2.0, 1.0 + (flow_accumulation / 1000) * 0.1)
    
    final_depth = base_depth * soil_factor * flow_factor
    
    # Add some randomness for realism
    final_depth *= np.random.uniform(0.8, 1.2)
    
    return max(0, min(5, final_depth))  # Clamp between 0-5 meters

# Routes
@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        "status": "online",
        "service": "EQUINOX Flood Prediction System",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "ml_model_loaded": ml_model is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/villages', methods=['GET'])
def get_villages():
    """Get all villages data"""
    villages = get_sample_villages()
    return jsonify({
        "success": True,
        "count": len(villages),
        "villages": villages,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/villages/<village_id>', methods=['GET'])
def get_village(village_id):
    """Get specific village data"""
    villages = get_sample_villages()
    village = next((v for v in villages if v["id"] == village_id), None)
    
    if village:
        return jsonify({
            "success": True,
            "village": village
        })
    else:
        return jsonify({
            "success": False,
            "error": "Village not found"
        }), 404

@app.route('/api/predict', methods=['POST'])
def predict_flood():
    """Predict flood depth for given parameters"""
    try:
        data = request.get_json()
        
        # Extract parameters
        rainfall_mm = float(data.get('rainfall_mm', 0))
        slope_degrees = float(data.get('slope_degrees', 5))
        soil_type = data.get('soil_type', 'loamy')
        flow_accumulation = float(data.get('flow_accumulation', 1000))
        elevation_m = float(data.get('elevation_m', 250))
        village_id = data.get('village_id')
        village_name = data.get('village_name', 'Unknown')
        
        # Validate input
        if rainfall_mm < 0 or rainfall_mm > 500:
            return jsonify({
                "success": False,
                "error": "Rainfall must be between 0-500 mm"
            }), 400
        
        # Make prediction
        if ml_model and scaler and encoder:
            # Prepare features for ML model
            features = np.array([[
                rainfall_mm,
                slope_degrees,
                flow_accumulation,
                elevation_m
            ]])
            
            # Scale features
            features_scaled = scaler.transform(features)
            
            # Predict
            prediction = ml_model.predict(features_scaled)[0]
            confidence = 0.9  # Simulated confidence
        else:
            # Fallback to simulation
            prediction = simulate_prediction(
                rainfall_mm, slope_degrees, soil_type, flow_accumulation
            )
            confidence = 0.7
        
        # Determine risk category
        if prediction < 0.1:
            risk_category = "MINIMAL"
        elif prediction < 0.5:
            risk_category = "MODERATE"
        elif prediction < 1.0:
            risk_category = "HIGH"
        else:
            risk_category = "EXTREME"
        
        # Calculate warning time (simplified)
        warning_time = max(5, int(60 / (rainfall_mm + 1)))  # Minutes
        
        response = {
            "success": True,
            "prediction": {
                "flood_depth_m": float(prediction),
                "risk_category": risk_category,
                "confidence": float(confidence),
                "warning_time_minutes": warning_time,
                "village_id": village_id,
                "village_name": village_name,
                "timestamp": datetime.now().isoformat()
            },
            "input_parameters": {
                "rainfall_mm": rainfall_mm,
                "slope_degrees": slope_degrees,
                "soil_type": soil_type,
                "flow_accumulation": flow_accumulation,
                "elevation_m": elevation_m
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/predict/batch', methods=['POST'])
def predict_batch():
    """Batch prediction for multiple villages"""
    try:
        data = request.get_json()
        villages = data.get('villages', [])
        
        if not villages:
            return jsonify({
                "success": False,
                "error": "No villages provided"
            }), 400
        
        results = []
        for village in villages:
            # Use single prediction endpoint logic
            rainfall_mm = float(village.get('rainfall_mm', 0))
            slope_degrees = float(village.get('slope_degrees', 5))
            soil_type = village.get('soil_type', 'loamy')
            flow_accumulation = float(village.get('flow_accumulation', 1000))
            
            prediction = simulate_prediction(
                rainfall_mm, slope_degrees, soil_type, flow_accumulation
            )
            
            # Determine risk
            if prediction < 0.1:
                risk = "MINIMAL"
            elif prediction < 0.5:
                risk = "MODERATE"
            elif prediction < 1.0:
                risk = "HIGH"
            else:
                risk = "EXTREME"
            
            results.append({
                "village_id": village.get('id'),
                "village_name": village.get('name'),
                "flood_depth_m": float(prediction),
                "risk_category": risk,
                "confidence": 0.8,
                "warning_time_minutes": 30
            })
        
        return jsonify({
            "success": True,
            "count": len(results),
            "predictions": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    """Create and send an alert"""
    try:
        data = request.get_json()
        
        alert = {
            "id": f"alert_{int(datetime.now().timestamp())}",
            "type": data.get('type', 'flood'),
            "level": data.get('level', 'warning'),
            "title": data.get('title', 'Flood Alert'),
            "message": data.get('message', 'Flood risk detected'),
            "village_id": data.get('village_id'),
            "village_name": data.get('village_name'),
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False
        }
        
        # In production, this would send SMS/email
        print(f"📢 ALERT: {alert['title']} - {alert['message']}")
        
        return jsonify({
            "success": True,
            "alert": alert,
            "message": "Alert created successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    return jsonify({
        "success": True,
        "message": f"Alert {alert_id} acknowledged",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/reports', methods=['POST'])
def submit_report():
    """Submit a flood report from human sensor"""
    try:
        data = request.get_json()
        
        report = {
            "id": f"report_{int(datetime.now().timestamp())}",
            "village_id": data.get('village_id'),
            "village_name": data.get('village_name'),
            "flood_depth": float(data.get('flood_depth', 0)),
            "description": data.get('description', ''),
            "reporter_name": data.get('reporter_name', 'Anonymous'),
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        print(f"📋 REPORT: {report['village_name']} - Depth: {report['flood_depth']}m")
        
        return jsonify({
            "success": True,
            "report": report,
            "message": "Report submitted successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """Get system status and metrics"""
    return jsonify({
        "status": "operational",
        "uptime": "99.8%",
        "ml_model": "loaded" if ml_model else "simulation",
        "api_requests_today": 42,
        "predictions_today": 156,
        "alerts_sent_today": 8,
        "cpu_usage": 34.5,
        "memory_usage": 67.2,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/rainfall/<district>', methods=['GET'])
def get_rainfall(district):
    """Get rainfall data for a district"""
    # Simulated rainfall data
    rainfall_data = {
        "jodhpur": {"current": 52.4, "forecast": [45, 60, 35, 20, 15, 10, 5]},
        "jaipur": {"current": 35.2, "forecast": [30, 40, 25, 15, 10, 5, 0]},
        "udaipur": {"current": 28.7, "forecast": [25, 30, 20, 15, 10, 5, 0]}
    }
    
    district_lower = district.lower()
    if district_lower in rainfall_data:
        return jsonify({
            "success": True,
            "district": district,
            "rainfall_mm": rainfall_data[district_lower],
            "timestamp": datetime.now().isoformat()
        })
    else:
        # Return default data
        return jsonify({
            "success": True,
            "district": district,
            "rainfall_mm": {"current": 25.0, "forecast": [20, 25, 15, 10, 5, 0, 0]},
            "timestamp": datetime.now().isoformat()
        })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

# Run the application
if __name__ == '__main__':
    print("🚀 Starting EQUINOX Flood Prediction System...")
    print(f"📁 Models loaded: {ml_model is not None}")
    print(f"🌐 API running at: http://localhost:5000")
    print("📋 Available endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/villages            - Get all villages")
    print("  POST /api/predict             - Predict flood depth")
    print("  POST /api/alerts              - Create alert")
    print("  GET  /api/system/status       - System metrics")
    print("  GET  /api/v2/health           - V2 Health (seismic, relief, weather, GIS)")
    print("  GET  /api/v2/dashboard        - V2 Dashboard overview")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
// 2026-01-04 12:38:41 UI component update

# 2026-01-06 17:55:05 weather data integration
