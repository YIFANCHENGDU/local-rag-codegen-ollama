from typing import Dict, Any, List
import json
import re
from app.agents.base import BaseAgent


class DeveloperAgent(BaseAgent):
    """Developer agent that generates code based on specifications and context."""
    
    def __init__(self):
        super().__init__(name="Developer", role="Developer")
    
    def _get_system_prompt(self) -> str:
        return """You are an expert Software Developer responsible for implementing code based on product specifications and technical requirements.

Your responsibilities:
1. Write clean, maintainable, and well-documented code
2. Follow coding best practices and design patterns
3. Implement all specified requirements
4. Create proper file structure and organization
5. Include necessary imports and dependencies

When generating code, always respond in JSON format with the following structure:
{
    "implementation_plan": "Brief plan of what you're implementing",
    "files": [
        {
            "path": "relative/path/to/file.py",
            "content": "actual file content",
            "description": "description of what this file does"
        }
    ],
    "dependencies": ["dependency1", "dependency2"],
    "setup_commands": ["command1", "command2"],
    "notes": "Any important notes about the implementation"
}

Always provide complete, functional code that can be executed directly."""
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        instruction = context.get("instruction", "")
        specifications = context.get("specifications", {})
        rag_context = context.get("rag_context", [])
        
        prompt = f"""Original User Instruction: {instruction}

Product Manager Specifications:
{json.dumps(specifications, indent=2)}

"""
        
        if rag_context:
            prompt += "Relevant Code Examples and Documentation from Knowledge Base:\n"
            for i, doc in enumerate(rag_context[:3]):
                prompt += f"Context {i+1} ({doc.get('metadata', {}).get('source', 'unknown')}):\n{doc['content'][:800]}...\n\n"
        
        prompt += """Please implement the code based on the specifications provided. Generate complete, functional files that fulfill all the requirements. Make sure to include proper error handling, documentation, and follow best practices."""
        
        return prompt
    
    def _parse_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                code_data = json.loads(json_match.group())
            else:
                # Fallback: try to extract code blocks
                code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', response, re.DOTALL)
                files = []
                for i, (lang, code) in enumerate(code_blocks):
                    if code.strip():
                        # Try to guess filename from code content or use generic name
                        filename = self._guess_filename(code, lang, i)
                        files.append({
                            "path": filename,
                            "content": code.strip(),
                            "description": f"Generated code file {i+1}"
                        })
                
                code_data = {
                    "implementation_plan": "Code implementation based on specifications",
                    "files": files,
                    "dependencies": [],
                    "setup_commands": [],
                    "notes": "Generated from code blocks in response"
                }
            
            return {
                "agent": self.name,
                "role": self.role,
                "code": code_data,
                "raw_response": response
            }
            
        except Exception as e:
            # Emergency fallback
            return {
                "agent": self.name,
                "role": self.role,
                "code": {
                    "implementation_plan": "Basic implementation created",
                    "files": [
                        {
                            "path": "main.py",
                            "content": f"# Implementation for: {context.get('instruction', 'user request')}\n# {response[:500]}...",
                            "description": "Basic implementation file"
                        }
                    ],
                    "dependencies": [],
                    "setup_commands": [],
                    "notes": "Fallback implementation due to parsing error"
                },
                "raw_response": response,
                "parsing_error": str(e)
            }
    
    def _guess_filename(self, code: str, lang: str, index: int) -> str:
        """Try to guess appropriate filename from code content."""
        code_lower = code.lower()
        
        # Common patterns
        if 'def main(' in code_lower or 'if __name__' in code_lower:
            return f"main.py"
        elif 'class ' in code_lower and 'test' in code_lower:
            return f"test_{index}.py"
        elif 'fastapi' in code_lower or 'app = ' in code_lower:
            return f"app.py"
        elif 'import unittest' in code_lower or 'import pytest' in code_lower:
            return f"test_{index}.py"
        elif lang == 'python' or 'import ' in code_lower:
            return f"module_{index}.py"
        elif lang == 'bash' or 'sh' in lang:
            return f"script_{index}.sh"
        elif lang == 'javascript' or lang == 'js':
            return f"script_{index}.js"
        else:
            ext = {'python': 'py', 'bash': 'sh', 'shell': 'sh', 'javascript': 'js', 'js': 'js'}.get(lang, 'txt')
            return f"file_{index}.{ext}"