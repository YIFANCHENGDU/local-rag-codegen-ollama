import ollama
from typing import List, Dict, Any, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama models."""
    
    def __init__(self):
        self.client = ollama.Client(host=settings.ollama_host)
        self.llm_model = settings.llm_model
        self.embedding_model = settings.embedding_model
    
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response using the LLM model."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat(
                model=self.llm_model,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text using the embedding model."""
        try:
            response = self.client.embeddings(
                model=self.embedding_model,
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise


# Global client instance
ollama_client = OllamaClient()