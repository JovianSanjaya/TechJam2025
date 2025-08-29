#!/usr/bin/env python3
"""Test the updated vector store with ChromaDB fallback"""

import sys
import os

# Add the Python source directory to path
extension_python_dir = os.path.join(os.path.dirname(__file__), 'extension', 'src', 'python')
sys.path.insert(0, extension_python_dir)
sys.path.insert(0, os.path.dirname(__file__))

print("🧪 Testing Updated Vector Store with ChromaDB Fallback")
print("=" * 60)

try:
    # Test the updated vector store
    from vector_store import get_vector_store
    
    print("✅ Successfully imported get_vector_store")
    
    # Initialize vector store (should try ChromaDB first, then fallback)
    vector_store = get_vector_store()
    print("✅ Vector store initialized")
    
    # Test if we can load documents
    import json
    try:
        with open('legal_documents.json', 'r', encoding='utf-8') as f:
            legal_data = json.load(f)
        
        # Extract documents array from the JSON structure
        if isinstance(legal_data, dict) and 'documents' in legal_data:
            legal_docs = legal_data['documents']
        else:
            legal_docs = legal_data if isinstance(legal_data, list) else [legal_data]
        
        vector_store.add_documents(legal_docs)
        print(f"✅ Successfully loaded {len(legal_docs)} documents")
        
        # Test document count
        doc_count = vector_store.get_document_count()
        print(f"📊 Vector store contains {doc_count} documents")
        
        # Test search functionality
        print(f"\n🔍 Testing search functionality:")
        search_results = vector_store.search_relevant_statutes("child privacy protection", n_results=3)
        
        if search_results['documents'] and search_results['documents'][0]:
            print(f"   ✅ Found {len(search_results['documents'][0])} relevant documents")
            for i, metadata in enumerate(search_results['metadatas'][0][:3]):
                title = metadata.get('title', 'Unknown Document')
                print(f"   📄 {i+1}. {title}")
        else:
            print(f"   ⚠️  No documents found")
        
        print(f"\n✅ Vector store test completed successfully!")
        
    except Exception as e:
        print(f"❌ Document loading error: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Vector store error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
