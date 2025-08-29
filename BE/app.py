from flask import Flask, request, jsonify
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
import traceback

from enhanced_main import EnhancedComplianceSystem

app = Flask(__name__)

# Global system instance
compliance_system = None

async def initialize_system():
    """Initialize the compliance system"""
    global compliance_system
    if compliance_system is None:
        compliance_system = EnhancedComplianceSystem()
        await compliance_system.initialize()
    return compliance_system

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
    
    Expected JSON format:
    {
        "features": [
            {
                "id": "feat_001",
                "feature_name": "Feature Name",
                "description": "Feature description",
                "code": "optional code snippet"
            }
        ],
        "include_code_analysis": true,
        "export_formats": ["json"]
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON",
                "status": "error"
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'features' not in data:
            return jsonify({
                "error": "Missing 'features' field in request",
                "status": "error"
            }), 400
        
        features = data['features']
        if not isinstance(features, list) or len(features) == 0:
            return jsonify({
                "error": "'features' must be a non-empty list",
                "status": "error"
            }), 400
        
        # Optional parameters
        include_code_analysis = data.get('include_code_analysis', True)
        export_formats = data.get('export_formats', ['json'])
        
        # Validate features structure
        for i, feature in enumerate(features):
            if not isinstance(feature, dict):
                return jsonify({
                    "error": f"Feature at index {i} must be an object",
                    "status": "error"
                }), 400
            
            # Ensure required fields
            if 'feature_name' not in feature:
                feature['feature_name'] = f'Feature_{i+1}'
            if 'id' not in feature:
                feature['id'] = f'feat_{i+1:03d}'
            if 'description' not in feature:
                feature['description'] = 'No description provided'
        
        # Run analysis asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Initialize system if needed
            system = loop.run_until_complete(initialize_system())
            
            # Run analysis
            results = loop.run_until_complete(
                system.analyze_feature_list(features, include_code_analysis=include_code_analysis)
            )
            
            # Export results if requested
            export_files = {}
            if export_formats and len(export_formats) > 0:
                export_files = loop.run_until_complete(
                    system.export_results(results, formats=export_formats)
                )
            
            # Prepare response
            response = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "analysis_results": results,
                "export_files": export_files,
                "request_summary": {
                    "features_analyzed": len(features),
                    "include_code_analysis": include_code_analysis,
                    "export_formats": export_formats
                }
            }
            
            return jsonify(response)
            
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
    print("🚀 Starting TikTok Compliance Analysis API...")
    print("📡 Available endpoints:")
    print("   GET  / - API information")
    print("   GET  /health - Health check")
    print("   POST /analyze - Analyze features")
    print("   GET  /analyze/sample - Sample analysis")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
