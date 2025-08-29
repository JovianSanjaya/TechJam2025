#!/usr/bin/env python3
"""Quick test to verify Python path resolution works"""

import sys
import os

extension_python_dir = os.path.join(os.path.dirname(__file__), 'extension', 'src', 'python')
sys.path.insert(0, extension_python_dir)

print("🧪 Testing Python Path Resolution")
print("=" * 50)

# Test if we can import our modules
try:
    from compliance_analyzer import analyze_code_for_compliance_llm
    from code_analyzer_llm_clean import LLMCodeAnalyzer
    from vector_store import get_vector_store
    
    print("✅ All modules imported successfully")
    print("✅ Python path resolution working")
    
    # Quick test of the system
    vector_store = get_vector_store()
    analyzer = LLMCodeAnalyzer(use_llm=True, force_llm=True, vector_store=vector_store)
    
    print("✅ LLM Analyzer initialized")
    print(f"✅ RAG Enabled: {'Yes' if vector_store else 'No'}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)
