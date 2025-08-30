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
    Single feature:
    {
        "featureName": "Feature Name",
        "description": "Feature description"
    }
    
    Batch features:
    {
        "items": [
            {
                "feature_name": "Feature Name 1",
                "description": "Feature description 1",
                "id": "optional_id_1"
            },
            {
                "feature_name": "Feature Name 2", 
                "description": "Feature description 2",
                "id": "optional_id_2"
            }
        ]
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
        
        # Check if it's batch processing or single feature
        if "items" in data and isinstance(data["items"], list):
            # Batch processing
            items = data["items"]
            print(f"📦 Processing {len(items)} items in batch")
            
            # Run async analysis for all items
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                analysis_results = []
                for i, item in enumerate(items):
                    print(f"🔄 Processing item {i+1}/{len(items)}: {item.get('feature_name', 'Unknown')}")
                    
                    # Convert to expected format for service
                    feature_data = {
                        "featureName": item.get("feature_name", ""),
                        "description": item.get("description", "")
                    }
                    
                    result = loop.run_until_complete(compliance_service.analyze_feature(feature_data))
                    
                    # Add the optional ID if provided
                    if "id" in item:
                        result["id"] = item["id"]
                    
                    analysis_results.append(result)
                    print(f"✅ Completed item {i+1}: {result.get('feature_name', 'Unknown')}")
                
                print(f"📤 All {len(analysis_results)} analyses completed")
                
                response = {
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "analysis_results": analysis_results,
                    "total_processed": len(analysis_results)
                }
                
                return jsonify(response)
            finally:
                loop.close()
        else:
            # Single feature processing (backward compatibility)
            print("📋 Processing single feature")
            
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
