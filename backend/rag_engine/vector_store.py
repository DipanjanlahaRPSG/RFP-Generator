import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
from config.settings import settings

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Wrapper around ChromaDB for storing and retrieving document embeddings.
    """
    
    def __init__(self):
        # Ensure persist directory exists
        os.makedirs(settings.chroma_persist_dir, exist_ok=True)
        
        # Initialize client
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
    def add_document(self, 
                     document_id: str, 
                     content: str, 
                     embedding: List[float], 
                     metadata: Dict[str, Any]):
        """
        Add a document to the vector store.
        """
        try:
            # Sanitize metadata for ChromaDB
            sanitized_metadata = {}
            for k, v in metadata.items():
                if v is None:
                    continue
                if isinstance(v, (str, int, float, bool)):
                    sanitized_metadata[k] = v
                elif isinstance(v, list):
                    # Convert list to string as ChromaDB (pre-0.4.15?) had issues with lists or mixed types
                    # Even if supported, comma-join is safer for simple metadata
                    sanitized_metadata[k] = ", ".join(str(item) for item in v)
                else:
                    # Fallback for dicts or other objects
                    sanitized_metadata[k] = str(v)

            self.collection.add(
                ids=[document_id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[sanitized_metadata]
            )
            logger.info(f"Added document {document_id} to vector store")
        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")
            raise

    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document by its ID.
        """
        try:
            result = self.collection.get(
                ids=[document_id],
                include=["documents", "metadatas", "embeddings"]
            )
            
            if result['ids'] is None or len(result['ids']) == 0:
                return None
                
            embedding = None
            if result['embeddings'] is not None and len(result['embeddings']) > 0:
                embedding = result['embeddings'][0]

            return {
                "id": result['ids'][0],
                "content": result['documents'][0],
                "metadata": result['metadatas'][0],
                "embedding": embedding
            }
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            return None

    def list_all_documents(self) -> List[str]:
        """
        List all document IDs in the store.
        """
        try:
            # ChromaDB doesn't have a direct "list all IDs" without fetching data?
            # Actually get() with no args fetches everything, might be heavy.
            # Limiting to IDs only.
            result = self.collection.get(include=[])
            return result['ids']
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []

    def reset_collection(self) -> bool:
        """
        Delete and recreate the collection.
        """
        try:
            self.client.delete_collection(settings.chroma_collection_name)
            self.collection = self.client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False

    def query_similar(self, 
                      query_embedding: List[float], 
                      n_results: int = 5,
                      where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query for similar documents.
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['ids']:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []
