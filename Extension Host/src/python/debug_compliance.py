#!/usr/bin/env python3
"""
Debug script to find the exact source of the 'str' object error
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.compliance_service import ComplianceService
from analyzers.simple_analyzer import SimpleAnalyzer
import traceback

def debug_compliance_service():
    """Debug the compliance service to find where the error occurs"""
    print("🔍 DEBUGGING COMPLIANCE SERVICE")
    print("=" * 50)
    
    # Test 1: Direct SimpleAnalyzer call
    print("\n1. Testing SimpleAnalyzer directly:")
    sa = SimpleAnalyzer()
    try:
        result = sa.analyze('def test(): pass', 'Test Feature', [])
        print(f"   ✅ Direct call works: {result.risk_level}")
    except Exception as e:
        print(f"   ❌ Direct call failed: {e}")
        traceback.print_exc()
    
    # Test 2: ComplianceService call
    print("\n2. Testing ComplianceService:")
    cs = ComplianceService()
    
    # Let's trace exactly what gets passed to simple analyzer
    original_analyze = sa.analyze
    
    def debug_analyze(code, feature_name, patterns):
        print(f"   📊 SimpleAnalyzer.analyze called with:")
        print(f"      code type: {type(code)}, value: {repr(code[:50])}")
        print(f"      feature_name type: {type(feature_name)}, value: {repr(feature_name)}")
        print(f"      patterns type: {type(patterns)}, value: {repr(patterns)}")
        
        # Check the _analyze_keywords method specifically
        print(f"   🔍 Testing _analyze_keywords:")
        try:
            keyword_scores = sa._analyze_keywords(code)
            print(f"      keyword_scores type: {type(keyword_scores)}")
            print(f"      keyword_scores value: {keyword_scores}")
        except Exception as e:
            print(f"      ❌ _analyze_keywords failed: {e}")
            traceback.print_exc()
        
        return original_analyze(code, feature_name, patterns)
    
    # Monkey patch for debugging
    cs.simple_analyzer.analyze = debug_analyze
    
    try:
        result = cs.analyze_code('def test(): pass', 'Test Feature')
        print(f"   ✅ ComplianceService works: {result.risk_level}")
    except Exception as e:
        print(f"   ❌ ComplianceService failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_compliance_service()
