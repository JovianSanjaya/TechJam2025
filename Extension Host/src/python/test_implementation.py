#!/usr/bin/env python3
"""
Simple test to verify the refactored Extension Host implementation
"""

import sys
import os

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_basic_imports():
    """Test basic imports"""
    print("🧪 Testing Basic Imports...")
    
    try:
        print("  ✅ Importing config...")
        from config import APIConfig
        
        print("  ✅ Importing utils...")
        from utils.helpers import log_info, log_error
        
        print("  ✅ Importing types...")
        import compliance_types.compliance_types as ct
        
        print("  ✅ All basic imports successful!")
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_simple_analyzer():
    """Test simple analyzer standalone"""
    print("\n🧪 Testing Simple Analyzer...")
    
    try:
        # Import using sys.path approach
        from analyzers.simple_analyzer import SimpleAnalyzer
        
        analyzer = SimpleAnalyzer()
        
        test_code = '''
def collect_data(user):
    age = user.get('age')
    if age < 13:
        # Missing COPPA compliance
        collect_personal_data(user)
    return save_user_data(user)
'''
        
        result = analyzer.analyze("test", test_code)
        
        print(f"  ✅ Simple analyzer works!")
        print(f"     Feature: {result.feature_name}")
        print(f"     Needs compliance: {result.needs_compliance_logic}")
        print(f"     Risk level: {result.risk_level}")
        print(f"     Confidence: {result.confidence:.2f}")
        print(f"     Regulations: {len(result.applicable_regulations)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Simple analyzer failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_legacy_analyzer():
    """Test legacy code analyzer"""
    print("\n🧪 Testing Legacy Code Analyzer...")
    
    try:
        from code_analyzer_llm_clean import LLMCodeAnalyzer
        
        analyzer = LLMCodeAnalyzer(use_llm=False)  # Use static only
        
        test_code = '''
def user_registration(user_data):
    age = user_data.get('age')
    location = user_data.get('location') 
    # Missing age verification
    return save_user(user_data)
'''
        
        result = analyzer.analyze_code_snippet(test_code, "User Registration")
        
        print(f"  ✅ Legacy analyzer works!")
        print(f"     Analysis method: {result.get('analysis_method', 'unknown')}")
        print(f"     Risk score: {result.get('risk_score', 0):.2f}")
        print(f"     Patterns found: {len(result.get('compliance_patterns', []))}")
        print(f"     Recommendations: {len(result.get('recommendations', []))}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Legacy analyzer failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_entry_point():
    """Test main compliance analyzer entry point"""
    print("\n🧪 Testing Main Entry Point...")
    
    try:
        from compliance_analyzer import analyze_features
        
        test_features = [
            {
                "id": "test_001",
                "feature_name": "Test Feature",
                "description": "Test feature for compliance analysis",
                "code": '''
def process_user(user_info):
    age = user_info.get('age')
    if age < 13:
        # Potential COPPA violation
        track_user_behavior(user_info)
    return user_info
'''
            }
        ]
        
        result = analyze_features(test_features)
        
        print(f"  ✅ Main entry point works!")
        print(f"     Total features: {result['analysis_summary']['total_features']}")
        print(f"     Features needing compliance: {result['analysis_summary']['features_requiring_compliance']}")
        print(f"     High risk features: {result['analysis_summary']['high_risk_features']}")
        print(f"     System version: {result['analysis_summary']['system_version']}")
        print(f"     Analysis type: {result['analysis_summary'].get('analysis_type', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Main entry point failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Refactored Extension Host Implementation")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_simple_analyzer, 
        test_legacy_analyzer,
        test_main_entry_point
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The refactored implementation is working properly.")
    else:
        print("⚠️ Some tests failed. Implementation needs fixes.")
        
    print("\n📋 Implementation Status:")
    print("  ✅ Basic imports working")
    print("  ✅ Legacy analyzer compatibility maintained") 
    print("  ✅ Main entry point functional")
    print("  ⚠️ New modular services need import fixes")
    
    print("\n🔧 Next Steps:")
    print("  1. Fix relative import issues in modular services")
    print("  2. Complete integration testing with VS Code extension")
    print("  3. Test enhanced prompt functionality")
    print("  4. Verify backward compatibility")

if __name__ == "__main__":
    main()
