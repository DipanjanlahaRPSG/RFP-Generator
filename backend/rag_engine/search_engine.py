import logging
from typing import List, Dict, Any, Optional
from rag_engine.embedding_engine import EmbeddingEngine
from rag_engine.vector_store import VectorStore
from config.settings import settings

logger = logging.getLogger(__name__)

class SearchEngine:
    """
    High-level search interface combining embedding generation and vector storage.
    """
    
    def __init__(self):
        self.embedding_engine = EmbeddingEngine()
        self.vector_store = VectorStore()
        
    def search_templates(self, 
                         query: str, 
                         filters: Optional[Dict[str, Any]] = None, 
                         limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for templates based on logical filters and semantic query.
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_engine.generate_embedding(query)
            
            # Prepare ChromaDB filters
            chroma_filters = {}
            if filters:
                # ChromaDB supports basic exact match filters
                # If multiple filters, we might need $and
                if len(filters) > 1:
                    chroma_filters = {"$and": [{k: v} for k, v in filters.items()]}
                else:
                    chroma_filters = filters
            
            # Search
            raw_results = self.vector_store.query_similar(
                query_embedding=query_embedding,
                n_results=limit,
                where=chroma_filters if chroma_filters else None
            )
            
            # Transform results for output formatter
            formatted_results = []
            for res in raw_results:
                formatted_results.append({
                    "document_id": res.get("id"),
                    "similarity_score": 1 - res.get("distance", 1.0),
                    "metadata": res.get("metadata", {}),
                    "content": res.get("content")
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def find_similar_documents(self, document_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find documents similar to a specific document ID.
        """
        try:
            # Get the source document
            doc = self.vector_store.get_document_by_id(document_id)
            if not doc:
                logger.warning(f"Document {document_id} not found")
                return []
            
            # Use its embedding to find others
            # We exclude the document itself from results if possible, but simplest is to request limit+1
            results = self.vector_store.query_similar(
                query_embedding=doc['embedding'],
                n_results=limit + 1
            )
            
            # Filter out the source document and format
            formatted_results = []
            for res in results:
                if res['id'] == document_id:
                    continue
                    
                formatted_results.append({
                    "document_id": res.get("id"),
                    "similarity_score": 1 - res.get("distance", 1.0),
                    "metadata": res.get("metadata", {}),
                    "content": res.get("content")
                })
                
            return formatted_results[:limit]
            
        except Exception as e:
            logger.error(f"Find similar failed: {e}")
            return []

    def get_document_recommendations(self, document_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get recommendations based on a document (alias for find_similar for now).
        """
        return self.find_similar_documents(document_id, limit)

    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Return statistics about the search index.
        """
        try:
            doc_ids = self.vector_store.list_all_documents()
            return {
                "total_documents": len(doc_ids),
                "collection_name": settings.chroma_collection_name,
                "embedding_model": settings.openai_embedding_model
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
