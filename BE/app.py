from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
import traceback

from feature_compliance_analyzer import FeatureComplianceAnalyzer

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"], supports_credentials=True)

# Global sophisticated analyzer instance
compliance_analyzer = FeatureComplianceAnalyzer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "TikTok Compliance Analysis API"
    })

@app.route('/analyze', methods=['POST'])
def analyze_features():
    """
    Analyze features for compliance
    
    Expected JSON format (new):
    {
        "featureName": "Feature Name",
        "description": "Feature description", 
        "code": "optional code snippet",
        "featureType": "feature type"
    }
    
    Or legacy format:
    {
        "features": [{
            "id": "feat_001",
            "feature_name": "Feature Name",
            "description": "Feature description",
            "code": "optional code snippet"
        }],
        "include_code_analysis": true,
        "export_formats": ["json"]
    }
    """
    try:

        print(f"Request: {request}")

        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON",
                "status": "error"
            }), 400
        
        data = request.get_json()

        
        # Use sophisticated analyzer for LLM/ML-powered analysis
        print(f"📥 Received data: {data}")
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(compliance_analyzer.analyze_json_input(data))
            print(f"📤 Analysis result: {result}")
            return jsonify(result)
        finally:
            loop.close()
    
    except Exception as e:
        # Log the full error for debugging
        error_details = {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"❌ Analysis error: {error_details}")
        
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__,
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/analyze/sample', methods=['GET'])
def analyze_sample():
    """
    Analyze sample features for testing
    """
    try:
        # Sample features
        sample_features = [
            {
                "id": "feat_001",
                "feature_name": "Age Verification Gate",
                "description": "ASL verification system for users under 16 with PF restrictions",
                "code": '''
def verify_user_age(user_data):
    age = user_data.get('age')
    if age < 13:
        require_parental_consent()
    elif age < 16:
        apply_privacy_restrictions()
    return age >= 13
'''
            },
            {
                "id": "feat_002", 
                "feature_name": "Geolocation Service",
                "description": "GH-based location tracking for content localization with NR compliance",
                "code": '''
import geoip
def get_user_location(ip_address):
    location = geoip.get_location(ip_address)
    track_user(location, "geolocation")
    return location
'''
            }
        ]
        
        # Run analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            system = loop.run_until_complete(initialize_system())
            results = loop.run_until_complete(
                system.analyze_feature_list(sample_features, include_code_analysis=True)
            )
            
            response = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "analysis_results": results,
                "note": "This is a sample analysis with predefined features"
            }
            
            return jsonify(response)
            
        finally:
            loop.close()
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__,
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "service": "TikTok Compliance Analysis API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "GET /health - Health check",
            "analyze": "POST /analyze - Analyze features for compliance",
            "sample": "GET /analyze/sample - Run sample analysis"
        },
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    import os
    
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    print("🚀 Starting TikTok Compliance Analysis API...")
    print(f"📡 Port: {port}")
    print("📡 Available endpoints:")
    print("   GET  / - API information")
    print("   GET  /health - Health check")
    print("   POST /analyze - Analyze features")
    print("   GET  /analyze/sample - Sample analysis")
    print()
    
    app.run(host='0.0.0.0', port=port, debug=False)
