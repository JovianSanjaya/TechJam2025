#!/usr/bin/env python3
"""Direct test of enhanced analysis"""

import sys
import os

# Add the Python source directory to path
extension_python_dir = os.path.join(os.path.dirname(__file__), 'extension', 'src', 'python')
sys.path.insert(0, extension_python_dir)

# Test code with compliance issues
test_code = '''
def collect_user_data(user_id, age, location, email):
    user_data = {'user_id': user_id, 'age': age, 'location': location, 'email': email}
    
    # GDPR violation - no consent for marketing
    send_to_marketing(email, location)
    
    # COPPA violation - storing child data without parental consent
    if age < 13:
        store_child_preferences(user)
    
    return user_data
'''

print("🧪 Enhanced Analysis Test")
print("=" * 50)

try:
    from code_analyzer_llm_clean import LLMCodeAnalyzer
    
    print("✅ Successfully imported LLMCodeAnalyzer")
    
    # Force use of SimpleFallbackStore to bypass ChromaDB issues
    vector_store = None
    try:
        from vector_store import SimpleFallbackStore
        import json
        
        # Load legal documents for RAG
        with open('extension/src/python/legal_documents.json', 'r') as f:
            legal_docs = json.load(f)
        
        # Initialize fallback store (no vectorization needed)
        vector_store = SimpleFallbackStore()
        vector_store.add_documents(legal_docs)
        
        print(f"✅ SimpleFallbackStore initialized - RAG enabled with {len(legal_docs)} documents")
    except Exception as e:
        print(f"⚠️  Fallback store failed: {e} - RAG disabled")
    
    # Test with the enhanced analyzer (with RAG enabled via fallback store)
    analyzer = LLMCodeAnalyzer(vector_store=vector_store)
    print("✅ Analyzer initialized")
    
    result = analyzer.analyze_code_snippet(test_code, "test_file.py")
    print("✅ Analysis completed")
    
    print(f"\n📊 Analysis Results:")
    print(f"   Features: {len(result.get('features', []))}")
    print(f"   Recommendations: {len(result.get('recommendations', []))}")
    print(f"   Code Issues: {len(result.get('code_issues', []))}")
    
    # Show the enhanced code issues (our main enhancement)
    if result.get('code_issues'):
        print(f"\n🎯 ENHANCED CODE ISSUES ({len(result['code_issues'])} found):")
        print("-" * 40)
        for i, issue in enumerate(result['code_issues'], 1):
            print(f"\n{i}. {issue.get('severity', 'UNKNOWN').upper()} - {issue.get('violation_type', 'Unknown Violation')}")
            if issue.get('problematic_code'):
                print(f"   🚨 Code: `{issue['problematic_code']}`")
            if issue.get('regulation_violated'):
                print(f"   📋 Regulation: {issue['regulation_violated']}")
            if issue.get('fix_description'):
                print(f"   💡 Fix: {issue['fix_description']}")
            if issue.get('suggested_replacement'):
                print(f"   🔧 Replacement: `{issue['suggested_replacement']}`")
    else:
        print("ℹ️  No specific code issues detected (this means the enhanced feature needs debugging)")
    
    # Show enhanced recommendations  
    if result.get('recommendations'):
        print(f"\n💡 AI RECOMMENDATIONS ({len(result['recommendations'])} found):")
        print("-" * 40)
        for i, rec in enumerate(result['recommendations'][:3], 1):  # Show first 3
            print(f"{i}. {rec}")
        if len(result['recommendations']) > 3:
            print(f"   ... and {len(result['recommendations']) - 3} more")
    
    print(f"\n✅ Enhanced analysis test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)
