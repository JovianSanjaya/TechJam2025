"""
RAG (Retrieval-Augmented Generation) Service.

This module provides retrieval capabilities for legal documents and context
to augment compliance analysis with relevant regulatory information.
"""

import json
import sys
import os
from typing import List, Dict, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import log_error, log_info


class RAGService:
    """
    Service for Retrieval-Augmented Generation operations.
    
    Handles loading and retrieval of legal documents to provide relevant
    regulatory context for compliance analysis.
    """
    
    def __init__(self, vector_store=None, legal_documents_path: str = None):
        """
        Initialize the RAG service.
        
        Args:
            vector_store: Optional vector store for semantic search
            legal_documents_path: Path to legal documents JSON file
        """
        self.vector_store = vector_store
        self.legal_documents_path = legal_documents_path or str(Path(__file__).parent.parent / "legal_documents.json")
        self.legal_documents = self._load_legal_documents()
        
    def _load_legal_documents(self) -> List[Dict]:
        """
        Load legal documents from JSON file.
        
        Returns:
            List of legal document dictionaries
        """
        try:
            with open(self.legal_documents_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle different JSON structures
                if isinstance(data, list):
                    documents = data
                elif isinstance(data, dict):
                    # Check if documents are nested under a key
                    if 'documents' in data:
                        documents = data['documents']
                    elif 'data' in data:
                        documents = data['data']
                    else:
                        # Treat the whole dict as a single document
                        documents = [data]
                else:
                    log_error("Unexpected JSON structure in legal documents")
                    return []
                
                log_info(f"Loaded {len(documents)} legal documents")
                return documents
        except FileNotFoundError:
            log_error(f"Legal documents file not found: {self.legal_documents_path}")
            return []
        except json.JSONDecodeError as e:
            log_error(f"Failed to parse legal documents JSON: {e}")
            return []
    
    def retrieve_relevant_context(self, query: str, max_docs: int = 5) -> str:
        """
        Retrieve relevant legal context for the given query.
        
        Args:
            query: Search query for document retrieval
            max_docs: Maximum number of documents to retrieve
            
        Returns:
            Combined context string from relevant documents
        """
        if self.vector_store:
            return self._retrieve_with_vector_store(query, max_docs)
        else:
            return self._retrieve_with_keyword_search(query, max_docs)
    
    def is_available(self) -> bool:
        """
        Check if RAG service is available.
        
        Returns:
            True if legal documents are loaded, False otherwise
        """
        return len(self.legal_documents) > 0
    
    def _retrieve_with_vector_store(self, query: str, max_docs: int) -> str:
        """
        Retrieve using vector store (if available).
        
        Args:
            query: Search query
            max_docs: Maximum documents to retrieve
            
        Returns:
            Combined context from vector search results
        """
        try:
            results = self.vector_store.similarity_search(query, k=max_docs)
            contexts = []
            
            for result in results:
                contexts.append(result.page_content)
            
            combined_context = "\n\n---\n\n".join(contexts)
            log_info(f"RAG retrieved {len(results)} documents via vector search")
            return combined_context
            
        except Exception as e:
            log_error(f"Vector store retrieval failed: {e}")
            return self._retrieve_with_keyword_search(query, max_docs)
    
    def _retrieve_with_keyword_search(self, query: str, max_docs: int) -> str:
        """
        Fallback keyword-based retrieval.
        
        Args:
            query: Search query
            max_docs: Maximum documents to retrieve
            
        Returns:
            Combined context from keyword search results
        """
        if not self.legal_documents:
            return "No legal documents available."
        
        query_lower = query.lower()
        keywords = query_lower.split()
        
        # Score documents based on keyword matches
        scored_docs = []
        for doc in self.legal_documents:
            if not isinstance(doc, dict):
                continue  # Skip non-dictionary items
                
            score = 0
            # Handle different document structures
            title = doc.get('title', '')
            content = doc.get('content', '')
            
            # If content is empty, check for sections
            if not content and 'sections' in doc:
                sections = doc.get('sections', [])
                content_parts = []
                for section in sections:
                    if isinstance(section, dict):
                        section_content = section.get('content', '')
                        section_title = section.get('title', '')
                        content_parts.append(f"{section_title} {section_content}")
                content = ' '.join(content_parts)
            
            combined_text = (content + ' ' + title).lower()
            
            for keyword in keywords:
                score += combined_text.count(keyword)
            
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and take top documents
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_docs = scored_docs[:max_docs]
        
        contexts = []
        for _, doc in top_docs:
            title = doc.get('title', 'Untitled')
            content = doc.get('content', '')
            
            # If no direct content, extract from sections
            if not content and 'sections' in doc:
                sections = doc.get('sections', [])
                content_parts = []
                for section in sections:
                    if isinstance(section, dict):
                        section_content = section.get('content', '')
                        section_title = section.get('title', '')
                        if section_content:
                            content_parts.append(f"## {section_title}\n{section_content}")
                content = '\n\n'.join(content_parts)
            
            if content:
                contexts.append(f"# {title}\n{content}")
        
        combined_context = "\n\n---\n\n".join(contexts)
        log_info(f"RAG retrieved {len(top_docs)} documents via keyword search")
        return combined_context
    
    def is_available(self) -> bool:
        """Check if RAG service is available"""
        return len(self.legal_documents) > 0 or self.vector_store is not None
