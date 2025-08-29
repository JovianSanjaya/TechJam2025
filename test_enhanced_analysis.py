#!/usr/bin/env python3
"""Test the enhanced analysis capabilities directly"""

# Simple test file with compliance issues
test_code = '''
import requests
import json

def collect_user_data(user_id, age, location, email):
    """Collect user data for processing"""
    user_data = {
        'user_id': user_id,
        'age': age,
        'location': location,
        'email': email,
        'timestamp': '2024-01-01'
    }
    
    # Problematic: Sending data to marketing without consent
    send_to_marketing(email, location)
    
    # Problematic: Storing children's data without parental consent
    if age < 13:
        store_child_preferences(user)
    
    # Problematic: No encryption for sensitive data
    store_in_database(user_data)
    
    return user_data

def send_to_marketing(email, location):
    """Send user data to marketing team"""
    marketing_data = {
        'email': email,
        'location': location,
        'targeting': True
    }
    # This violates GDPR - no consent mechanism
    requests.post('https://marketing.api.com/users', json=marketing_data)

def store_child_preferences(user):
    """Store preferences for children under 13"""
    # This violates COPPA - no parental consent
    preferences = {
        'favorite_content': user.get('preferences', []),
        'viewing_history': user.get('history', [])
    }
    save_to_database(preferences)

def store_in_database(data):
    """Store data in database without encryption"""
    # Security issue - no encryption
    with open('user_data.json', 'w') as f:
        json.dump(data, f)
'''

print("🧪 Testing Enhanced Code Analysis Capabilities")
print("=" * 60)
print(f"📝 Code to analyze ({len(test_code)} characters):")
print("-" * 30)
print(test_code[:200] + "..." if len(test_code) > 200 else test_code)
print("-" * 30)

# Test the LLM analyzer directly
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'extension', 'src', 'python'))
    
    from code_analyzer_llm_clean import analyze_code_compliance_llm
    
    print("\n🔍 Running Enhanced LLM Analysis...")
    result = analyze_code_compliance_llm(test_code, "test_file.py")
    
    if result:
        print("\n✅ Analysis Complete!")
        print(f"📊 Features Found: {len(result.get('features', []))}")
        print(f"🎯 Recommendations: {len(result.get('recommendations', []))}")
        print(f"🚨 Code Issues: {len(result.get('code_issues', []))}")
        
        # Show code issues (the enhanced highlighting feature)
        if result.get('code_issues'):
            print("\n🔍 SPECIFIC CODE ISSUES DETECTED:")
            print("=" * 50)
            for i, issue in enumerate(result['code_issues'], 1):
                print(f"\n{i}. {issue.get('violation_type', 'Unknown')} - {issue.get('severity', 'Unknown')} severity")
                print(f"   📍 Line: {issue.get('line_reference', 'Unknown')}")
                print(f"   🚨 Problematic Code: `{issue.get('problematic_code', 'N/A')}`")
                print(f"   📋 Regulation: {issue.get('regulation_violated', 'N/A')}")
                print(f"   💡 Fix: {issue.get('fix_description', 'N/A')}")
                if issue.get('suggested_replacement'):
                    print(f"   🔧 Suggested Code: `{issue.get('suggested_replacement')}`")
                if issue.get('testing_requirements'):
                    print(f"   🧪 Testing: {issue.get('testing_requirements')}")
        
        # Show enhanced recommendations
        if result.get('recommendations'):
            print("\n💡 AI-GENERATED RECOMMENDATIONS:")
            print("=" * 50)
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"{i}. {rec}")
        
    else:
        print("❌ Analysis failed - no result returned")
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("📋 Required files missing or Python environment issue")
except Exception as e:
    print(f"❌ Analysis Error: {e}")
    print("📋 Check if all dependencies are installed")

print("\n" + "=" * 60)
print("🎯 Enhanced Analysis Test Complete")
