from typing import Dict, Any, List
import json
import re
from app.agents.base import BaseAgent


class ProductManagerAgent(BaseAgent):
    """Product Manager agent that analyzes requirements and creates specifications."""
    
    def __init__(self):
        super().__init__(name="ProductManager", role="Product Manager")
    
    def _get_system_prompt(self) -> str:
        return """You are an expert Product Manager responsible for analyzing user requirements and creating detailed technical specifications.

Your responsibilities:
1. Analyze user requirements and identify core functionality needed
2. Break down requirements into specific, actionable tasks
3. Define clear acceptance criteria for each component
4. Consider technical constraints and best practices
5. Provide structured specifications that developers can follow

Always respond in JSON format with the following structure:
{
    "analysis": "Brief analysis of the requirements",
    "specifications": [
        {
            "component": "Component name",
            "description": "Detailed description",
            "requirements": ["requirement 1", "requirement 2"],
            "acceptance_criteria": ["criteria 1", "criteria 2"]
        }
    ],
    "technical_considerations": ["consideration 1", "consideration 2"],
    "success_metrics": ["metric 1", "metric 2"]
}"""
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        instruction = context.get("instruction", "")
        rag_context = context.get("rag_context", [])
        
        prompt = f"""User Instruction: {instruction}

"""
        
        if rag_context:
            prompt += "Relevant Context from Knowledge Base:\n"
            for i, doc in enumerate(rag_context[:3]):
                prompt += f"Context {i+1}:\n{doc['content'][:500]}...\n\n"
        
        prompt += """Please analyze the user instruction and create detailed technical specifications. Consider the context provided and break down the requirements into specific, implementable components."""
        
        return prompt
    
    def _parse_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                specs_data = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                specs_data = {
                    "analysis": "Requirements analysis completed",
                    "specifications": [
                        {
                            "component": "Main Component",
                            "description": response[:200] + "...",
                            "requirements": ["Implement core functionality"],
                            "acceptance_criteria": ["Component works as expected"]
                        }
                    ],
                    "technical_considerations": ["Follow best practices"],
                    "success_metrics": ["Functionality implemented successfully"]
                }
            
            return {
                "agent": self.name,
                "role": self.role,
                "specifications": specs_data,
                "raw_response": response
            }
            
        except Exception as e:
            # Fallback response structure
            return {
                "agent": self.name,
                "role": self.role,
                "specifications": {
                    "analysis": "Analysis completed with basic specifications",
                    "specifications": [
                        {
                            "component": "Core Implementation",
                            "description": f"Implement functionality based on: {context.get('instruction', 'user requirements')}",
                            "requirements": ["Follow coding standards", "Implement required functionality"],
                            "acceptance_criteria": ["Code works correctly", "Meets user requirements"]
                        }
                    ],
                    "technical_considerations": ["Use appropriate design patterns", "Ensure code maintainability"],
                    "success_metrics": ["Functionality delivered", "Code quality maintained"]
                },
                "raw_response": response,
                "parsing_error": str(e)
            }