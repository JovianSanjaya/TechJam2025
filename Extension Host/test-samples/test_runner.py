#!/usr/bin/env python3
"""
Test Runner for TikTok Compliance Analyzer
This script tests the compliance analyzer with sample violation files.
"""

import os
import sys
import json

# Add the src/python directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python'))

try:
    from compliance_analyzer import analyze_features
    print("✅ Successfully imported compliance_analyzer")
except ImportError as e:
    print(f"❌ Error importing compliance_analyzer: {e}")
    print("Make sure the compliance_analyzer.py file exists in ../src/python/")
    sys.exit(1)

def test_compliance_analyzer():
    """Test the compliance analyzer with sample files"""

    test_files = [
        'privacy_violations.py',
        'api_violations.py',
        'tracking_violations.js',
        'typescript_violations.ts',
        'react_violations.tsx'
    ]

    print("🧪 Testing TikTok Compliance Analyzer")
    print("=" * 50)

    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📁 Testing: {test_file}")
            print("-" * 30)

            try:
                # Read the test file
                with open(test_file, 'r', encoding='utf-8') as f:
                    code_content = f.read()

                # Create test feature
                test_feature = {
                    'id': f'test_{os.path.splitext(test_file)[0]}',
                    'feature_name': test_file,
                    'description': f'Testing compliance analysis of {test_file}',
                    'code': code_content[:5000]  # Limit code length for testing
                }

                # Analyze the feature
                results = analyze_features([test_feature])

                # Display results
                summary = results['analysis_summary']
                print(f"✅ Analysis completed successfully")
                print(f"📊 Total features: {summary['total_features']}")
                print(f"⚖️  Features requiring compliance: {summary['features_requiring_compliance']}")
                print(f"🚨 High risk features: {summary['high_risk_features']}")
                print(f"👥 Human review needed: {summary['human_review_needed']}")

                if results['detailed_results']:
                    result = results['detailed_results'][0]
                    print(f"🎯 Risk Level: {result['risk_level']}")
                    print(f"📈 Confidence: {result['confidence']:.1%}")
                    print(f"📋 Applicable Regulations: {len(result['applicable_regulations'])}")
                    print(f"💡 Implementation Notes: {len(result['implementation_notes'])}")

                    if result['applicable_regulations']:
                        print("   Regulations:")
                        for reg in result['applicable_regulations'][:3]:  # Show first 3
                            print(f"   • {reg['name']}: {reg['description']}")

                if results['recommendations']:
                    print("💡 Top Recommendations:")
                    for i, rec in enumerate(results['recommendations'][:3], 1):
                        print(f"   {i}. {rec}")

            except Exception as e:
                print(f"❌ Error testing {test_file}: {str(e)}")
        else:
            print(f"⚠️  Test file not found: {test_file}")

    print("\n" + "=" * 50)
    print("🎉 Testing completed!")

def test_individual_violations():
    """Test specific types of violations"""

    print("\n🔍 Testing Individual Violation Types")
    print("=" * 50)

    test_cases = [
        {
            'name': 'Personal Data Collection',
            'code': '''
def collect_user_data():
    user_data = get_user_profile()
    store_data(user_data)  # No consent
    return user_data
'''
        },
        {
            'name': 'Location Tracking',
            'code': '''
def track_location():
    location = get_current_location()  # No consent
    share_with_partners(location)
    return location
'''
        },
        {
            'name': 'Age Verification',
            'code': '''
def process_user(user):
    if user.age < 13:
        collect_child_data(user)  # COPPA violation
    return user
'''
        },
        {
            'name': 'Behavioral Tracking',
            'code': '''
def track_behavior():
    actions = monitor_user_actions()  # No consent
    create_advertising_profile(actions)
    return actions
'''
        }
    ]

    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print("-" * 30)

        try:
            test_feature = {
                'id': f'test_{test_case["name"].lower().replace(" ", "_")}',
                'feature_name': test_case['name'],
                'description': f'Testing {test_case["name"]} violation',
                'code': test_case['code']
            }

            results = analyze_features([test_feature])
            result = results['detailed_results'][0]

            print(f"🎯 Risk Level: {result['risk_level']}")
            print(f"📈 Confidence: {result['confidence']:.1%}")
            print(f"⚖️  Needs Compliance: {result['needs_compliance_logic']}")

            if result['implementation_notes']:
                print("💡 Notes:")
                for note in result['implementation_notes'][:2]:
                    print(f"   • {note}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Change to the test-samples directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    test_compliance_analyzer()
    test_individual_violations()
