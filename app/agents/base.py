from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from app.core.ollama_client import ollama_client
from app.core.rag import rag_system

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system."""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.system_prompt = self._get_system_prompt()
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result."""
        try:
            prompt = self._build_prompt(context)
            response = await ollama_client.generate_response(
                prompt=prompt,
                system_prompt=self.system_prompt
            )
            return self._parse_response(response, context)
        except Exception as e:
            logger.error(f"Error in {self.name} processing: {e}")
            raise
    
    @abstractmethod
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Build the prompt for this agent based on context."""
        pass
    
    @abstractmethod
    def _parse_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the agent's response and return structured output."""
        pass