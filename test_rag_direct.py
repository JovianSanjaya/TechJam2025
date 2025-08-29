#!/usr/bin/env python3
"""Test with direct SimpleFallbackStore implementation to bypass ChromaDB"""

import sys
import os
import json

# Add the Python source directory to path
extension_python_dir = os.path.join(os.path.dirname(__file__), 'extension', 'src', 'python')
sys.path.insert(0, extension_python_dir)

# Simple RAG implementation without ChromaDB
class DirectFallbackStore:
    def __init__(self):
        self.documents = []
        print("📚 Using direct fallback document store (no vector search)")
    
    def add_documents(self, documents):
        self.documents = documents
        print(f"✅ Loaded {len(documents)} documents into RAG store")
    
    def search_relevant_statutes(self, feature_description, n_results=5):
        """Simple keyword-based search as fallback"""
        feature_words = set(feature_description.lower().split())
        scored_docs = []
        
        for doc in self.documents:
            content = self._extract_content(doc)
            content_words = set(content.lower().split())
            
            # Simple word overlap scoring
            overlap = len(feature_words & content_words)
            if overlap > 0:
                scored_docs.append((overlap, doc, content))
        
        # Sort by score and return top results
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_docs = scored_docs[:n_results]
        
        return {
            'documents': [[doc[2] for doc in top_docs]],
            'metadatas': [[{
                'title': doc[1].get('title', 'Unknown'),
                'url': doc[1].get('url', ''),
                'doc_type': doc[1].get('content_type', 'legal_document')
            } for doc in top_docs]],
            'distances': [[1.0 / (doc[0] + 1) for doc in top_docs]]
        }
    
    def _extract_content(self, doc):
        """Extract content for search"""
        content_parts = []
        if doc.get('title'):
            content_parts.append(doc['title'])
        if doc.get('description'):
            content_parts.append(doc['description'])
        if 'sections' in doc:
            for section in doc['sections']:
                if section.get('content'):
                    content_parts.append(section['content'][:1000])
        return " ".join(content_parts)
    
    def get_document_count(self):
        return len(self.documents)

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

print("🧪 Enhanced Analysis Test with Direct RAG")
print("=" * 60)

try:
    from code_analyzer_llm_clean import LLMCodeAnalyzer
    
    print("✅ Successfully imported LLMCodeAnalyzer")
    
    # Initialize direct RAG store
    vector_store = DirectFallbackStore()
    
    # Load legal documents
    try:
        with open('extension/src/python/legal_documents.json', 'r', encoding='utf-8') as f:
            legal_data = json.load(f)
        
        # Extract documents array from the JSON structure
        if isinstance(legal_data, dict) and 'documents' in legal_data:
            legal_docs = legal_data['documents']
        else:
            legal_docs = legal_data if isinstance(legal_data, list) else [legal_data]
        
        vector_store.add_documents(legal_docs)
        print(f"✅ RAG initialized with {len(legal_docs)} legal documents")
    except Exception as e:
        print(f"⚠️  Failed to load legal docs: {e}")
        # Try alternative paths
        try:
            with open('legal_documents.json', 'r', encoding='utf-8') as f:
                legal_data = json.load(f)
            
            if isinstance(legal_data, dict) and 'documents' in legal_data:
                legal_docs = legal_data['documents']
            else:
                legal_docs = legal_data if isinstance(legal_data, list) else [legal_data]
            
            vector_store.add_documents(legal_docs)
            print(f"✅ RAG initialized with {len(legal_docs)} legal documents (fallback path)")
        except Exception as e2:
            print(f"⚠️  Also failed fallback path: {e2}")
            vector_store = None
    
    # Test with the enhanced analyzer with RAG
    analyzer = LLMCodeAnalyzer(vector_store=vector_store)
    print("✅ Analyzer initialized")
    
    result = analyzer.analyze_code_snippet(test_code, "test_file.py")
    print("✅ Analysis completed")
    
    print(f"\n📊 Analysis Results:")
    print(f"   Features: {len(result.get('features', []))}")
    print(f"   Recommendations: {len(result.get('recommendations', []))}")
    print(f"   Code Issues: {len(result.get('code_issues', []))}")
    
    # Show the enhanced code issues
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
        for i, rec in enumerate(result['recommendations'][:3], 1):
            print(f"{i}. {rec}")
        if len(result['recommendations']) > 3:
            print(f"   ... and {len(result['recommendations']) - 3} more")
    
    # Test RAG functionality directly
    if vector_store and vector_store.get_document_count() > 0:
        print(f"\n🔍 RAG TEST - Searching for 'child privacy':")
        rag_results = vector_store.search_relevant_statutes("child privacy protection", n_results=2)
        if rag_results['documents'] and rag_results['documents'][0]:
            print(f"   ✅ Found {len(rag_results['documents'][0])} relevant documents")
            for i, metadata in enumerate(rag_results['metadatas'][0][:2]):
                print(f"   📄 {i+1}. {metadata.get('title', 'Unknown Document')}")
        else:
            print(f"   ⚠️  No documents found")
    
    print(f"\n✅ Enhanced analysis with RAG test completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
