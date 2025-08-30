"""
API Routes for Compliance Analysis
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
import traceback

from flask import Blueprint, request, jsonify
from services.compliance_service import ComplianceService

api_bp = Blueprint('api', __name__)

# Initialize service
compliance_service = ComplianceService()

@api_bp.route('/', methods=['GET'])
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

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "TikTok Compliance Analysis API"
    })

@api_bp.route('/analyze', methods=['POST'])
def analyze_features():
    """
    Analyze features for compliance
    
    Expected JSON format:
    {
        "featureName": "Feature Name",
        "description": "Feature description"
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
        print(f"📥 Received data: {data}")
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(compliance_service.analyze_feature(data))
            print(f"📤 Analysis result: {result}")
            
            # Wrap result in expected format for frontend
            response = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "analysis_results": [result]
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

@api_bp.route('/analyze/sample', methods=['GET'])
def analyze_sample():
    """
    Analyze sample features for testing
    """
    try:
        # Sample features
        sample_data = {
            "featureName": "Age Verification Gate",
            "description": "ASL verification system for users under 16 with PF restrictions"
        }
        
        # Run analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(compliance_service.analyze_feature(sample_data))
            
            response = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "analysis_results": [result],
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
