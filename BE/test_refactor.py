#!/usr/bin/env python3
"""
Test script to verify the refactored backend works
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.compliance_service import ComplianceService

async def test_compliance_service():
    """Test the compliance service"""
    print("🧪 Testing Refactored Compliance Service")
    print("=" * 50)
    
    try:
        # Initialize service
        service = ComplianceService()
        print("✅ Service initialized successfully")
        
        # Test data
        test_data = {
            "featureName": "Age Verification System",
            "description": "ASL verification system for users under 16 with PF restrictions"
        }
        
        print(f"📝 Testing with: {test_data}")
        
        # Run analysis
        result = await service.analyze_feature(test_data)
        
        print("✅ Analysis completed successfully!")
        print(f"📊 Result keys: {list(result.keys())}")
        print(f"🎯 Feature: {result.get('feature_name', 'Unknown')}")
        print(f"⚠️ Risk Level: {result.get('risk_level', 'Unknown')}")
        print(f"🔍 Confidence: {result.get('confidence', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting Backend Refactor Test")
    
    # Run async test
    success = asyncio.run(test_compliance_service())
    
    if success:
        print("\n🎉 All tests passed! Refactor successful!")
        return 0
    else:
        print("\n💥 Tests failed! Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
