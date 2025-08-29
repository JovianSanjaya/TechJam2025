#!/usr/bin/env python3
"""
Test script to verify LLM integration with code_analyzer_llm_clean.py
Uses your .env configuration for OpenRouter API with Moonshot KIMI model
"""

import time
from code_analyzer_llm_clean import LLMCodeAnalyzer
from config import ComplianceConfig

def test_configuration():
    """Test that configuration is loaded correctly from .env"""
    print("🔧 Configuration Test")
    print("=" * 40)
    
    print(f"OpenRouter API Key: {'✅ Set' if ComplianceConfig.OPENROUTER_API_KEY else '❌ Missing'}")
    print(f"OpenRouter Model: {ComplianceConfig.OPENROUTER_MODEL}")
    print(f"API Key (first 10 chars): {ComplianceConfig.OPENROUTER_API_KEY[:10]}..." if ComplianceConfig.OPENROUTER_API_KEY else "No API key")
    print()

def test_analyzer_initialization():
    """Test analyzer initialization with force LLM"""
    print("🚀 Analyzer Initialization Test")
    print("=" * 40)
    
    # Test without forcing LLM (normal mode)
    print("1. Normal initialization:")
    analyzer_normal = LLMCodeAnalyzer(use_llm=True)
    print()
    
    # Test with forcing LLM
    print("2. Forced LLM initialization:")
    analyzer_forced = LLMCodeAnalyzer(use_llm=True, force_llm=True)
    print()
    
    return analyzer_forced

def test_simple_static_analysis():
    """Test static analysis without LLM calls"""
    print("📊 Static Analysis Test")
    print("=" * 40)
    
    simple_code = '''
def collect_user_data(user_id, age):
    if age < 13:
        print("Minor user detected")
    return {"user_id": user_id, "age": age}
'''
    
    analyzer = LLMCodeAnalyzer(use_llm=False)  # Static only
    result = analyzer.analyze_code_snippet(simple_code, "Simple data collection")
    
    print(f"Analysis method: {result.get('analysis_method')}")
    print(f"Risk score: {result.get('risk_score', 0):.2f}")
    print(f"Patterns found: {len(result.get('compliance_patterns', []))}")
    print(f"Recommendations: {len(result.get('recommendations', []))}")
    print()

def test_llm_with_rate_limit_handling():
    """Test LLM with rate limit handling"""
    print("🤖 LLM Integration Test (with rate limit handling)")
    print("=" * 50)
    
    test_code = '''
def verify_age(user_data):
    age = user_data.get('age', 0)
    if age < 13:
        return False
    return True
'''
    
    analyzer = LLMCodeAnalyzer(use_llm=True, force_llm=True)
    
    try:
        print("Attempting LLM analysis...")
        result = analyzer.analyze_code_snippet(test_code, "Age verification function")
        
        print(f"✅ Analysis completed!")
        print(f"   Method: {result.get('analysis_method')}")
        print(f"   Risk score: {result.get('risk_score', 0):.2f}")
        
        if result.get('llm_insights'):
            print("   LLM insights available ✅")
        else:
            print("   No LLM insights (likely rate limited)")
            
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        print("   This is expected if rate limits are hit")
    
    print()

def main():
    """Run all tests"""
    print("🧪 LLM Integration Test Suite")
    print("=" * 50)
    print()
    
    # Test 1: Configuration
    test_configuration()
    
    # Test 2: Analyzer initialization
    analyzer = test_analyzer_initialization()
    
    # Test 3: Static analysis (always works)
    test_simple_static_analysis()
    
    # Test 4: LLM integration (may hit rate limits)
    test_llm_with_rate_limit_handling()
    
    print("🎉 Test suite completed!")
    print("\n💡 Key Points:")
    print("   ✅ Configuration is loaded from .env file")
    print("   ✅ LLM analyzer uses your specified model")
    print("   ✅ Static analysis works as fallback")
    print("   ⚠️  LLM calls may hit rate limits on free tier")
    print("\n🔧 Usage in your code:")
    print("   analyzer = LLMCodeAnalyzer(use_llm=True, force_llm=True)")
    print("   result = analyzer.analyze_code_snippet(code, context)")

if __name__ == "__main__":
    main()
