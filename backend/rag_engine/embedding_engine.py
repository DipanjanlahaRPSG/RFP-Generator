import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingEngine:
    """
    Engine for generating embeddings using OpenAI's API.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model
        
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        Truncates text if it exceeds max tokens.
        """
        try:
            # clean text
            text = text.replace("\n", " ")
            
            # Truncate if necessary
            # Simple character truncation as approximation (1 token ~= 4 chars)
            # Safe limit: max_tokens * 3 to be conservative (since some chars are < 1 byte, but many tokens are > 1 char)
            # Ideally use tiktoken, but to avoid extra deps for now, we'll use a safe char limit.
            # settings.max_tokens is usually 8191 for text-embedding-3-small
            max_chars = settings.max_tokens * 3
            if len(text) > max_chars:
                text = text[:max_chars]
                # logging truncation
                # logger.debug(f"Truncated text to {max_chars} chars for embedding")
            
            response = self.client.embeddings.create(
                input=[text],
                model=self.model
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_document_embedding(self, content: str, metadata: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for a document. 
        Currently just embeds the content, but could be enhanced to include metadata.
        """
        # For now, we just embed the content
        # In a more advanced version, we might combine title + summary + content
        return self.generate_embedding(content)
