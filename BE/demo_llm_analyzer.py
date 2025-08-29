"""
🚀 LLM-Enhanced Code Analyzer Demo

This script demonstrates how to use the upgraded code analyzer with LLM capabilities.
Follow these steps to enable LLM analysis:

1. Get a free API key from OpenRouter (https://openrouter.ai/)
2. Set your API key in the environment variable or config
3. Run analysis on your code

Features:
✅ Static analysis (always works)
✅ LLM-enhanced analysis (requires API key)
✅ Hybrid analysis combining both approaches
✅ Free models available (deepseek/deepseek-chat)
"""

from code_analyzer_llm_clean import LLMCodeAnalyzer
import os

def demo_static_analysis():
    """Demo static analysis (no API key needed)"""
    print("🔍 STATIC ANALYSIS DEMO")
    print("=" * 40)
    
    test_code = '''
def verify_user_age(user_data):
    age = user_data.get('age')
    if age < 13:
        require_parental_consent()
        track_user(user_data, "minor_user")
    elif age < 16:
        apply_privacy_restrictions()
    return age >= 13

def collect_user_location():
    import geoip
    location = geoip.get_location_by_ip()
    store_data(location, user_id)
    return location
'''
    
    # Static analysis only
    analyzer = LLMCodeAnalyzer(use_llm=False)
    result = analyzer.analyze_code_snippet(
        test_code, 
        context="TikTok age verification and location tracking feature"
    )
    
    print(f"Analysis Method: {result['analysis_method']}")
    print(f"Risk Score: {result['risk_score']:.2f}")
    print(f"Total Patterns: {len(result['compliance_patterns'])}")
    
    print("\n📊 Categories Found:")
    for category in ['age_verification', 'privacy_concerns', 'data_collection', 'geolocation']:
        count = len(result.get(category, []))
        if count > 0:
            print(f"  • {category.replace('_', ' ').title()}: {count}")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(result['recommendations'][:3], 1):
        print(f"  {i}. {rec}")
    
    return result

def demo_llm_analysis():
    """Demo LLM analysis (requires API key)"""
    print("\n🤖 LLM-ENHANCED ANALYSIS DEMO")
    print("=" * 40)
    
    # Check if API key is available
    if not os.getenv("OPENROUTER_API_KEY"):
        print("ℹ️  To enable LLM analysis:")
        print("   1. Get free API key: https://openrouter.ai/")
        print("   2. Set environment variable: OPENROUTER_API_KEY=your_key")
        print("   3. Re-run this demo")
        return None
    
    test_code = '''
class UserAgeGate:
    def __init__(self):
        self.minimum_age = 13
        
    def verify_age(self, birth_date, user_data):
        age = calculate_age(birth_date)
        if age < self.minimum_age:
            self.request_parental_consent(user_data)
            self.apply_child_protections(user_data)
            return False
        elif age < 16:
            self.limit_data_collection(user_data)
            self.restrict_targeted_ads(user_data)
        
        self.track_verification_event(user_data, age)
        return True
'''
    
    # LLM-enhanced analysis
    analyzer = LLMCodeAnalyzer(use_llm=True)
    result = analyzer.analyze_code_snippet(
        test_code,
        context="TikTok COPPA compliance age gate implementation"
    )
    
    print(f"Analysis Method: {result['analysis_method']}")
    print(f"Risk Score: {result['risk_score']:.2f}")
    
    if result.get('llm_insights'):
        insights = result['llm_insights']
        print(f"\n🎯 LLM Assessment: {insights.get('overall_assessment', 'N/A')}")
        print(f"🚨 Key Risks: {', '.join(insights.get('key_risks', []))}")
    
    print(f"\n📝 Enhanced Recommendations:")
    for i, rec in enumerate(result['recommendations'][:5], 1):
        print(f"  {i}. {rec}")
    
    return result

def setup_instructions():
    """Show setup instructions"""
    print("🔧 SETUP INSTRUCTIONS")
    print("=" * 40)
    print("1. Install dependencies:")
    print("   pip install requests")
    print("   (ast, re, json are built-in)")
    
    print("\n2. For LLM features (optional):")
    print("   • Visit: https://openrouter.ai/")
    print("   • Sign up for free account") 
    print("   • Get API key")
    print("   • Set environment variable:")
    print("     export OPENROUTER_API_KEY='your_key_here'")
    
    print("\n3. Free models available:")
    print("   • deepseek/deepseek-chat (default)")
    print("   • meta-llama/llama-3.2-3b-instruct:free")
    print("   • microsoft/phi-3-mini-128k-instruct:free")

if __name__ == "__main__":
    print("🎯 TikTok Compliance Code Analyzer - LLM Enhanced")
    print("=" * 60)
    
    # Show setup instructions
    setup_instructions()
    
    # Demo static analysis (always works)
    demo_static_analysis()
    
    # Demo LLM analysis (requires API key)
    demo_llm_analysis()
    
    print("\n✅ Demo complete!")
    print("💡 Use LLMCodeAnalyzer in your projects for enhanced compliance analysis!")
