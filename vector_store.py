try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("ChromaDB not available. Install with: pip install chromadb")

import hashlib
import json
from typing import List, Dict, Any
from config import ComplianceConfig

class LegalDocumentVectorStore:
    def __init__(self, collection_name="legal_docs"):
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is required but not installed. Run: pip install chromadb")
        
        self.client = chromadb.PersistentClient(path=ComplianceConfig.VECTOR_DB_PATH)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=ComplianceConfig.EMBEDDING_MODEL
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        self.collection_name = collection_name
    
    def _extract_content(self, doc: Dict) -> str:
        """Extract searchable content from document"""
        content_parts = []
        
        # Add title
        if doc.get('title'):
            content_parts.append(doc['title'])
        
        # Add description
        if doc.get('description'):
            content_parts.append(doc['description'])
        
        # Extract content from sections
        if 'sections' in doc:
            for section in doc['sections']:
                if section.get('title'):
                    content_parts.append(section['title'])
                if section.get('content'):
                    # Truncate very long content to prevent embedding issues
                    content = section['content']
                    if len(content) > 5000:
                        content = content[:5000] + "..."
                    content_parts.append(content)
        else:
            # Direct content field
            content = doc.get('content', '')
            if len(content) > 5000:
                content = content[:5000] + "..."
            if content:
                content_parts.append(content)
        
        return " ".join(content_parts)
    
    def _generate_doc_id(self, doc: Dict) -> str:
        """Generate unique ID for document"""
        unique_string = f"{doc.get('title', '')}{doc.get('url', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to vector store with metadata"""
        docs_to_add = []
        metadatas_to_add = []
        ids_to_add = []
        
        for doc in documents:
            doc_id = self._generate_doc_id(doc)
            content = self._extract_content(doc)
            
            if not content.strip():
                continue
            
            # Check if document already exists
            try:
                existing = self.collection.get(ids=[doc_id])
                if existing['ids']:
                    print(f"Document already exists: {doc.get('title', 'Unknown')}")
                    continue
            except:
                pass  # Document doesn't exist, proceed to add
            
            docs_to_add.append(content)
            metadatas_to_add.append({
                "title": doc.get('title', 'Unknown Document'),
                "url": doc.get('url', ''),
                "doc_type": doc.get('content_type', 'legal_document'),
                "doc_id": doc_id
            })
            ids_to_add.append(doc_id)
        
        if docs_to_add:
            try:
                self.collection.add(
                    documents=docs_to_add,
                    metadatas=metadatas_to_add,
                    ids=ids_to_add
                )
                print(f"Added {len(docs_to_add)} documents to vector store")
            except Exception as e:
                print(f"Error adding documents to vector store: {e}")
                # Fallback: add documents one by one
                for i, (doc, metadata, doc_id) in enumerate(zip(docs_to_add, metadatas_to_add, ids_to_add)):
                    try:
                        self.collection.add(
                            documents=[doc],
                            metadatas=[metadata],
                            ids=[doc_id]
                        )
                    except Exception as e2:
                        print(f"Failed to add document {i}: {e2}")
    
    def search_relevant_statutes(self, feature_description: str, n_results=10) -> Dict:
        """Find most relevant statutes for a feature"""
        try:
            results = self.collection.query(
                query_texts=[feature_description],
                n_results=min(n_results, self.collection.count() if self.collection.count() > 0 else 1)
            )
            return results
        except Exception as e:
            print(f"Error querying vector store: {e}")
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    
    def get_document_count(self) -> int:
        """Get number of documents in collection"""
        try:
            return self.collection.count()
        except:
            return 0
    
    def needs_reindexing(self, documents: List[Dict]) -> bool:
        """Check if documents need to be reindexed"""
        current_count = self.get_document_count()
        return current_count == 0 or current_count < len(documents)

# Fallback class when ChromaDB is not available
class SimpleFallbackStore:
    def __init__(self, collection_name="legal_docs"):
        self.documents = []
        print("Using fallback document store (no vector search)")
    
    def add_documents(self, documents: List[Dict]):
        self.documents = documents
        print(f"Loaded {len(documents)} documents into fallback store")
    
    def search_relevant_statutes(self, feature_description: str, n_results=10) -> Dict:
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
            'distances': [[1.0 / (doc[0] + 1) for doc in top_docs]]  # Convert overlap to distance-like score
        }
    
    def _extract_content(self, doc: Dict) -> str:
        """Extract content for fallback search"""
        content_parts = []
        if doc.get('title'):
            content_parts.append(doc['title'])
        if 'sections' in doc:
            for section in doc['sections']:
                if section.get('content'):
                    content_parts.append(section['content'][:1000])  # Limit content
        return " ".join(content_parts)
    
    def get_document_count(self) -> int:
        return len(self.documents)
    
    def needs_reindexing(self, documents: List[Dict]) -> bool:
        return len(self.documents) == 0
