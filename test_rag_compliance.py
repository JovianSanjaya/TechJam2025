#!/usr/bin/env python3
"""Test RAG-enabled compliance analyzer directly"""

import sys
import os

# Add the extension Python source directory to path
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
        store_child_preferences(user_data)
    
    return user_data
'''

print("🧪 Testing RAG-Enabled Compliance Analyzer")
print("=" * 60)

try:
    from compliance_analyzer import analyze_code_for_compliance_llm
    from code_analyzer_llm_clean import LLMCodeAnalyzer
    from vector_store import get_vector_store
    import json
    
    print("✅ Successfully imported compliance modules")
    
    # Initialize RAG system
    print("🔧 Initializing RAG system...")
    vector_store = get_vector_store()
    
    # Load legal documents for RAG
    try:
        with open('extension/src/python/legal_documents.json', 'r', encoding='utf-8') as f:
            legal_data = json.load(f)
        
        if isinstance(legal_data, dict) and 'documents' in legal_data:
            legal_docs = legal_data['documents']
        else:
            legal_docs = legal_data if isinstance(legal_data, list) else [legal_data]
        
        vector_store.add_documents(legal_docs)
        print(f"✅ RAG initialized with {len(legal_docs)} legal documents")
    except Exception as e:
        print(f"⚠️  RAG document loading failed: {e}")
    
    # Create analyzer with RAG enabled
    analyzer = LLMCodeAnalyzer(use_llm=True, force_llm=True, vector_store=vector_store)
    print("✅ LLM Analyzer with RAG created")
    
    # Test with the enhanced analyzer with RAG enabled
    result = analyze_code_for_compliance_llm(test_code, "test_file.py", analyzer)
    
    if result:
        print("✅ Analysis completed successfully!")
        
        print(f"\n📊 Analysis Results:")
        print(f"   Features: {len(result.get('features', []))}")
        print(f"   Recommendations: {len(result.get('recommendations', []))}")
        print(f"   Code Issues: {len(result.get('code_issues', []))}")
        print(f"   RAG Enabled: {result.get('rag_enabled', False)}")
        print(f"   Analysis Type: {result.get('analysis_type', 'unknown')}")
        
        # Show enhanced code issues (the main enhancement)
        if result.get('code_issues'):
            print(f"\n🎯 ENHANCED CODE ISSUES ({len(result['code_issues'])} found):")
            print("-" * 50)
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
        
        # Show enhanced recommendations  
        if result.get('recommendations'):
            print(f"\n💡 AI RECOMMENDATIONS ({len(result['recommendations'])} found):")
            print("-" * 50)
            for i, rec in enumerate(result['recommendations'][:5], 1):
                print(f"{i}. {rec}")
            if len(result['recommendations']) > 5:
                print(f"   ... and {len(result['recommendations']) - 5} more")
        
        print(f"\n✅ RAG-enabled compliance analysis test completed!")
        
    else:
        print("❌ Analysis failed - no result returned")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
