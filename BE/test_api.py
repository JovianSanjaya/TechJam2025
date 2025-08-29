#!/usr/bin/env python3
"""
Test script for the TikTok Compliance Analysis API
"""

import requests
import json
import time

# API base URL (adjust if running on different host/port)
BASE_URL = "http://localhost:5001"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_sample_analysis():
    """Test the sample analysis endpoint"""
    print("\n🔍 Testing sample analysis...")
    try:
        response = requests.get(f"{BASE_URL}/analyze/sample", timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sample analysis successful!")
            print(f"Features analyzed: {result['analysis_results']['analysis_summary']['total_features']}")
            print(f"Compliance required: {result['analysis_results']['analysis_summary']['features_requiring_compliance']}")
            print(f"High risk: {result['analysis_results']['analysis_summary']['high_risk_features']}")
        else:
            print(f"❌ Sample analysis failed: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Sample analysis failed: {e}")
        return False

def test_custom_analysis():
    """Test the custom analysis endpoint with JSON input"""
    print("\n🔍 Testing custom analysis...")
    
    # Custom features to analyze
    test_data = {
        "features": [
            {
                "id": "test_001",
                "feature_name": "User Profile Collection",
                "description": "Collects user personal information for profile creation",
                "code": '''
def create_user_profile(user_data):
    profile = {
        "name": user_data.get("name"),
        "age": user_data.get("age"),
        "email": user_data.get("email"),
        "location": user_data.get("location")
    }
    store_user_data(profile)
    return profile
'''
            },
            {
                "id": "test_002",
                "feature_name": "Content Sharing",
                "description": "Allows users to share content with privacy controls"
            }
        ],
        "include_code_analysis": True,
        "export_formats": ["json"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Custom analysis successful!")
            print(f"Features analyzed: {result['analysis_results']['analysis_summary']['total_features']}")
            print(f"Compliance required: {result['analysis_results']['analysis_summary']['features_requiring_compliance']}")
            print(f"High risk: {result['analysis_results']['analysis_summary']['high_risk_features']}")
            
            # Show detailed results for first feature
            if result['analysis_results']['detailed_results']:
                first_result = result['analysis_results']['detailed_results'][0]
                print(f"\nFirst feature analysis:")
                print(f"  Name: {first_result['feature_name']}")
                print(f"  Risk Level: {first_result['risk_level']}")
                print(f"  Action Required: {first_result['action_required']}")
                print(f"  Confidence: {first_result['confidence']}")
        else:
            print(f"❌ Custom analysis failed: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Custom analysis failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting TikTok Compliance API Tests")
    print(f"📡 Testing API at: {BASE_URL}")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("❌ Health check failed - API may not be running")
        print("💡 Make sure to run: docker-compose up")
        return
    
    # Test sample analysis
    test_sample_analysis()
    
    # Test custom analysis
    test_custom_analysis()
    
    print("\n" + "=" * 50)
    print("🎯 API testing complete!")
    print("\n💡 Usage examples:")
    print("   GET  /health - Check if API is running")
    print("   GET  /analyze/sample - Run sample analysis")
    print("   POST /analyze - Analyze custom features")
    print("\n📖 For POST /analyze, send JSON with this structure:")
    print(json.dumps({
        "features": [
            {
                "id": "feat_001",
                "feature_name": "Feature Name",
                "description": "Feature description",
                "code": "optional code snippet"
            }
        ],
        "include_code_analysis": True,
        "export_formats": ["json"]
    }, indent=2))

if __name__ == "__main__":
    main()
