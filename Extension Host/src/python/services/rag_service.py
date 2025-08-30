"""
RAG (Retrieval-Augmented Generation) Service
"""

import json
from typing import List, Dict, Optional
from pathlib import Path

from ..utils.helpers import log_error, log_info


class RAGService:
    """Service for RAG operations"""
    
    def __init__(self, vector_store=None, legal_documents_path: str = None):
        self.vector_store = vector_store
        self.legal_documents_path = legal_documents_path or str(Path(__file__).parent.parent / "legal_documents.json")
        self.legal_documents = self._load_legal_documents()
        
    def _load_legal_documents(self) -> List[Dict]:
        """Load legal documents from JSON file"""
        try:
            with open(self.legal_documents_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
                log_info(f"📚 Loaded {len(documents)} legal documents")
                return documents
        except FileNotFoundError:
            log_error(f"Legal documents file not found: {self.legal_documents_path}")
            return []
        except json.JSONDecodeError as e:
            log_error(f"Failed to parse legal documents JSON: {e}")
            return []
    
    def retrieve_relevant_context(self, query: str, max_docs: int = 5) -> str:
        """Retrieve relevant legal context for the query"""
        if self.vector_store:
            return self._retrieve_with_vector_store(query, max_docs)
        else:
            return self._retrieve_with_keyword_search(query, max_docs)
    
    def _retrieve_with_vector_store(self, query: str, max_docs: int) -> str:
        """Retrieve using vector store (if available)"""
        try:
            results = self.vector_store.similarity_search(query, k=max_docs)
            contexts = []
            
            for result in results:
                contexts.append(result.page_content)
            
            combined_context = "\n\n---\n\n".join(contexts)
            log_info(f"📊 RAG retrieved {len(results)} documents via vector search")
            return combined_context
            
        except Exception as e:
            log_error(f"Vector store retrieval failed: {e}")
            return self._retrieve_with_keyword_search(query, max_docs)
    
    def _retrieve_with_keyword_search(self, query: str, max_docs: int) -> str:
        """Fallback keyword-based retrieval"""
        if not self.legal_documents:
            return "No legal documents available."
        
        query_lower = query.lower()
        keywords = query_lower.split()
        
        # Score documents based on keyword matches
        scored_docs = []
        for doc in self.legal_documents:
            score = 0
            content = (doc.get('content', '') + ' ' + doc.get('title', '')).lower()
            
            for keyword in keywords:
                score += content.count(keyword)
            
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and take top documents
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_docs = scored_docs[:max_docs]
        
        contexts = []
        for _, doc in top_docs:
            title = doc.get('title', 'Untitled')
            content = doc.get('content', '')
            contexts.append(f"{title}\n{content}")
        
        combined_context = "\n\n---\n\n".join(contexts)
        log_info(f"📊 RAG retrieved {len(top_docs)} documents via keyword search")
        return combined_context
    
    def is_available(self) -> bool:
        """Check if RAG service is available"""
        return len(self.legal_documents) > 0 or self.vector_store is not None
