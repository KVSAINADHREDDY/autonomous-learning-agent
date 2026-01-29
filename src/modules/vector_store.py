"""
Vector Store module using FAISS for efficient similarity search.
Stores study materials and enables quick retrieval for quiz generation.
"""
import os
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Try importing FAISS and sentence transformers
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: FAISS not installed. Run: pip install faiss-cpu")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Run: pip install sentence-transformers")


@dataclass
class VectorDocument:
    """Represents a document stored in the vector database."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


class VectorStore:
    """
    FAISS-based vector store for storing and searching study materials.
    
    Features:
    - Efficient similarity search using FAISS
    - Automatic text embedding using Sentence Transformers
    - Support for metadata filtering
    - Persistent storage (optional)
    """
    
    def __init__(
        self,
        embedding_model: str = None,
        dimension: int = 384  # Default for all-MiniLM-L6-v2
    ):
        """
        Initialize the vector store.
        
        Args:
            embedding_model: Name of the sentence transformer model
            dimension: Embedding dimension (384 for MiniLM, 768 for larger models)
        """
        self.embedding_model_name = embedding_model or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.dimension = dimension
        self.documents: Dict[str, VectorDocument] = {}
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        
        # Initialize embedding model
        self._init_embedding_model()
        
        # Initialize FAISS index
        self._init_faiss_index()
    
    def _init_embedding_model(self):
        """Initialize the sentence transformer embedding model."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                # Update dimension based on actual model
                self.dimension = self.embedding_model.get_sentence_embedding_dimension()
                print(f"✅ Loaded embedding model: {self.embedding_model_name} (dim={self.dimension})")
            except Exception as e:
                print(f"⚠️ Could not load embedding model: {e}")
                self.embedding_model = None
        else:
            self.embedding_model = None
            print("⚠️ Sentence transformers not available. Using fallback embeddings.")
    
    def _init_faiss_index(self):
        """Initialize the FAISS index."""
        if FAISS_AVAILABLE:
            # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
            self.index = faiss.IndexFlatIP(self.dimension)
            print(f"✅ Initialized FAISS index (dimension={self.dimension})")
        else:
            self.index = None
            print("⚠️ FAISS not available. Using fallback similarity search.")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for a text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Normalized embedding vector
        """
        if self.embedding_model:
            embedding = self.embedding_model.encode(text, normalize_embeddings=True)
            return np.array(embedding, dtype=np.float32)
        else:
            # Fallback: simple hash-based embedding (not recommended for production)
            np.random.seed(hash(text) % (2**32))
            embedding = np.random.randn(self.dimension).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            return embedding
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of dicts with 'id', 'content', and optional 'metadata'
            
        Returns:
            List of document IDs added
        """
        added_ids = []
        embeddings_to_add = []
        
        for doc in documents:
            doc_id = doc.get('id', f"doc_{len(self.documents)}")
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            
            if not content:
                continue
            
            # Generate embedding
            embedding = self._get_embedding(content)
            
            # Create document
            vector_doc = VectorDocument(
                id=doc_id,
                content=content,
                metadata=metadata,
                embedding=embedding
            )
            
            # Store document
            self.documents[doc_id] = vector_doc
            current_index = len(self.id_to_index)
            self.id_to_index[doc_id] = current_index
            self.index_to_id[current_index] = doc_id
            
            embeddings_to_add.append(embedding)
            added_ids.append(doc_id)
        
        # Add embeddings to FAISS index
        if embeddings_to_add and self.index is not None:
            embeddings_matrix = np.vstack(embeddings_to_add)
            self.index.add(embeddings_matrix)
        
        print(f"📚 Added {len(added_ids)} documents to vector store")
        return added_ids
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[VectorDocument, float]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of (document, score) tuples
        """
        if not self.documents:
            return []
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        if self.index is not None and FAISS_AVAILABLE:
            # FAISS search
            query_embedding = query_embedding.reshape(1, -1)
            scores, indices = self.index.search(query_embedding, min(k * 2, len(self.documents)))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0:  # Invalid index
                    continue
                doc_id = self.index_to_id.get(idx)
                if doc_id and doc_id in self.documents:
                    doc = self.documents[doc_id]
                    
                    # Apply metadata filter
                    if filter_metadata:
                        match = all(
                            doc.metadata.get(k) == v 
                            for k, v in filter_metadata.items()
                        )
                        if not match:
                            continue
                    
                    results.append((doc, float(score)))
                    if len(results) >= k:
                        break
            
            return results
        else:
            # Fallback: brute force search
            results = []
            for doc in self.documents.values():
                if doc.embedding is not None:
                    score = np.dot(query_embedding, doc.embedding)
                    
                    # Apply metadata filter
                    if filter_metadata:
                        match = all(
                            doc.metadata.get(k) == v 
                            for k, v in filter_metadata.items()
                        )
                        if not match:
                            continue
                    
                    results.append((doc, float(score)))
            
            # Sort by score descending
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:k]
    
    def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Get a document by ID."""
        return self.documents.get(doc_id)
    
    def get_all_documents(self) -> List[VectorDocument]:
        """Get all documents."""
        return list(self.documents.values())
    
    def clear(self):
        """Clear all documents from the store."""
        self.documents.clear()
        self.id_to_index.clear()
        self.index_to_id.clear()
        self._init_faiss_index()
        print("🗑️ Cleared vector store")
    
    def get_context_for_topic(self, topic: str, objectives: List[str], k: int = 5) -> str:
        """
        Get relevant context for a topic and its objectives.
        
        Args:
            topic: The learning topic
            objectives: Learning objectives
            k: Number of documents to retrieve
            
        Returns:
            Combined context string
        """
        # Create a comprehensive query
        query = f"{topic}. " + " ".join(objectives)
        
        # Search for relevant documents
        results = self.search(query, k=k)
        
        if not results:
            return ""
        
        # Combine content from top results
        context_parts = []
        for doc, score in results:
            context_parts.append(f"[Relevance: {score:.2f}]\n{doc.content}")
        
        return "\n\n---\n\n".join(context_parts)


# Global vector store instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def reset_vector_store():
    """Reset the global vector store."""
    global _vector_store
    if _vector_store:
        _vector_store.clear()
    _vector_store = None
