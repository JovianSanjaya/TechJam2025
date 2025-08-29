#!/usr/bin/env python3
"""
Test script for VS Code chat integration with RAG-enabled LLM code analyzer
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from code_analyzer_llm_clean import LLMCodeAnalyzer
    from vector_store import get_vector_store
    from config import ComplianceConfig
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def test_rag_integration():
    """Test RAG-enabled analysis"""
    print("🧪 Testing RAG-Enabled LLM Code Analyzer")
    print("=" * 50)
    
    # Test code snippet
    test_code = '''
def verify_user_age(user_data):
    birth_date = user_data.get('birth_date')
    age = calculate_age(birth_date)
    
    if age < 13:
        # COPPA compliance required
        require_parental_consent(user_data)
        apply_child_protections(user_data)
        log_minor_user_access(user_data)
        return False
    elif age < 16:
        # Additional privacy protections
        limit_data_collection(user_data)
        restrict_targeted_advertising(user_data)
    
    track_verification_event(user_data, age)
    return True

def collect_location_data(user_id, ip_address):
    import geoip2.database
    
    # Get precise location
    location = geoip2.get_city(ip_address)
    
    # Store location data
    store_user_location(user_id, {
        'country': location.country.name,
        'city': location.city.name,
        'coordinates': [location.location.latitude, location.location.longitude],
        'timestamp': datetime.now(),
        'ip_address': ip_address
    })
    
    # Use for content personalization
    personalize_content_by_location(user_id, location)
    
    return location
'''
    
    try:
        # Initialize vector store
        print("🔍 Initializing vector store...")
        vector_store = get_vector_store()
        
        # Initialize analyzer with RAG
        print("🤖 Initializing LLM analyzer with RAG...")
        analyzer = LLMCodeAnalyzer(
            use_llm=True, 
            force_llm=True, 
            vector_store=vector_store
        )
        
        # Run analysis
        print("📊 Running compliance analysis...")
        result = analyzer.analyze_code_snippet(
            test_code,
            context="TikTok age verification and geolocation feature analysis"
        )
        
        # Format output for VS Code chat
        print("\n" + "="*60)
        print("📋 ANALYSIS RESULTS (VS Code Chat Format)")
        print("="*60)
        
        print(f"**Analysis Method:** {result.get('analysis_method', 'unknown')}")
        print(f"**Risk Score:** {(result.get('risk_score', 0) * 100):.1f}%")
        
        if result.get('llm_insights'):
            insights = result['llm_insights']
            print(f"\n**🤖 AI Assessment:** {insights.get('overall_assessment', 'N/A')}")
            
            if insights.get('key_risks'):
                print(f"\n**🚨 Key Risks:**")
                for risk in insights['key_risks']:
                    print(f"- {risk}")
            
            if insights.get('regulatory_gaps'):
                print(f"\n**📋 Regulatory Gaps:**")
                for gap in insights['regulatory_gaps']:
                    print(f"- {gap}")
        
        print(f"\n**💡 Recommendations:**")
        for i, rec in enumerate(result.get('recommendations', []), 1):
            print(f"{i}. {rec}")
        
        if result.get('compliance_patterns'):
            print(f"\n**🔍 Compliance Patterns Found:** {len(result['compliance_patterns'])}")
            for i, pattern in enumerate(result['compliance_patterns'][:3], 1):
                print(f"{i}. {pattern.get('pattern_name', 'Unknown')} ({pattern.get('confidence', 0)*100:.1f}% confidence)")
        
        print(f"\n---")
        print(f"*Analysis completed using RAG-enhanced LLM with legal document retrieval*")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration"""
    print("🔧 Configuration Check")
    print("=" * 30)
    
    print(f"OpenRouter API Key: {'✅ Set' if ComplianceConfig.OPENROUTER_API_KEY else '❌ Missing'}")
    print(f"OpenRouter Model: {ComplianceConfig.OPENROUTER_MODEL}")
    
    if ComplianceConfig.OPENROUTER_API_KEY:
        print(f"API Key Preview: {ComplianceConfig.OPENROUTER_API_KEY[:15]}...")
    
    print()

if __name__ == "__main__":
    print("🚀 VS Code Chat Integration Test")
    print("=" * 50)
    
    # Test configuration
    test_configuration()
    
    # Test RAG integration
    success = test_rag_integration()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("\n💡 VS Code Extension Usage:")
        print("   1. Open VS Code")
        print("   2. Open the chat panel")
        print("   3. Type: @tiktok-compliance /current-file")
        print("   4. Or: @tiktok-compliance /analyze [your code]")
    else:
        print("\n❌ Test failed - check the error messages above")
        sys.exit(1)
