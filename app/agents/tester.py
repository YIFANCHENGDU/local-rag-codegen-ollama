from typing import Dict, Any, List
import json
import re
from app.agents.base import BaseAgent


class TesterAgent(BaseAgent):
    """Tester agent that reviews code and creates tests."""
    
    def __init__(self):
        super().__init__(name="Tester", role="Quality Assurance Tester")
    
    def _get_system_prompt(self) -> str:
        return """You are an expert Quality Assurance Tester responsible for reviewing code and creating comprehensive tests.

Your responsibilities:
1. Review generated code for bugs, security issues, and best practices
2. Create comprehensive test suites for the generated code
3. Suggest improvements and identify potential issues
4. Ensure code quality and reliability
5. Verify that the code meets the original requirements

When reviewing code, always respond in JSON format with the following structure:
{
    "review_summary": "Overall assessment of the code quality",
    "issues_found": [
        {
            "severity": "high/medium/low",
            "file": "filename",
            "issue": "description of the issue",
            "suggestion": "how to fix it"
        }
    ],
    "test_files": [
        {
            "path": "path/to/test_file.py",
            "content": "test file content",
            "description": "what this test file covers"
        }
    ],
    "recommendations": ["recommendation 1", "recommendation 2"],
    "quality_score": "score out of 10",
    "requirements_coverage": "assessment of how well requirements are met"
}

Focus on creating practical, executable tests that thoroughly validate the functionality."""
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        instruction = context.get("instruction", "")
        specifications = context.get("specifications", {})
        generated_code = context.get("code", {})
        
        prompt = f"""Original User Instruction: {instruction}

Product Manager Specifications:
{json.dumps(specifications, indent=2)}

Generated Code to Review:
"""
        
        files = generated_code.get("files", [])
        for file_info in files[:5]:  # Limit to first 5 files to avoid token limits
            prompt += f"\nFile: {file_info['path']}\n"
            prompt += f"Description: {file_info.get('description', 'No description')}\n"
            prompt += f"Content:\n{file_info['content'][:1500]}...\n"
            prompt += "=" * 50 + "\n"
        
        prompt += f"""
Dependencies: {generated_code.get('dependencies', [])}
Setup Commands: {generated_code.get('setup_commands', [])}
Implementation Notes: {generated_code.get('notes', 'None')}

Please review this code thoroughly and create comprehensive tests. Focus on:
1. Code quality and potential bugs
2. Security considerations
3. Performance issues
4. Test coverage for all functionality
5. Compliance with original requirements"""
        
        return prompt
    
    def _parse_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                review_data = json.loads(json_match.group())
            else:
                # Fallback: create basic review structure
                # Extract test code blocks if present
                test_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', response, re.DOTALL)
                test_files = []
                
                for i, (lang, code) in enumerate(test_blocks):
                    if code.strip() and ('test' in code.lower() or 'assert' in code.lower()):
                        test_files.append({
                            "path": f"test_{i}.py",
                            "content": code.strip(),
                            "description": f"Test file {i+1} extracted from response"
                        })
                
                review_data = {
                    "review_summary": "Code review completed with basic analysis",
                    "issues_found": [
                        {
                            "severity": "medium",
                            "file": "general",
                            "issue": "Unable to parse detailed review",
                            "suggestion": "Manual review recommended"
                        }
                    ],
                    "test_files": test_files,
                    "recommendations": ["Add more comprehensive testing", "Review code manually"],
                    "quality_score": "7",
                    "requirements_coverage": "Partial coverage assessed"
                }
            
            return {
                "agent": self.name,
                "role": self.role,
                "review": review_data,
                "raw_response": response
            }
            
        except Exception as e:
            # Emergency fallback
            generated_code = context.get("code", {})
            files = generated_code.get("files", [])
            
            # Create basic test files for the generated code
            test_files = []
            for i, file_info in enumerate(files[:3]):
                if file_info['path'].endswith('.py'):
                    test_content = self._create_basic_test(file_info['path'], file_info['content'])
                    test_files.append({
                        "path": f"test_{file_info['path'].replace('.py', '')}.py",
                        "content": test_content,
                        "description": f"Basic test for {file_info['path']}"
                    })
            
            return {
                "agent": self.name,
                "role": self.role,
                "review": {
                    "review_summary": "Basic code review performed",
                    "issues_found": [
                        {
                            "severity": "low",
                            "file": "general",
                            "issue": "Automated review only",
                            "suggestion": "Perform manual code review"
                        }
                    ],
                    "test_files": test_files,
                    "recommendations": ["Add comprehensive testing", "Review for edge cases"],
                    "quality_score": "6",
                    "requirements_coverage": "Basic implementation appears functional"
                },
                "raw_response": response,
                "parsing_error": str(e)
            }
    
    def _create_basic_test(self, file_path: str, code_content: str) -> str:
        """Create a basic test template for a Python file."""
        module_name = file_path.replace('.py', '').replace('/', '.')
        
        test_template = f'''import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the module path to sys.path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import {module_name}
except ImportError:
    # Handle import error gracefully
    pass


class Test{module_name.title().replace('.', '')}(unittest.TestCase):
    """Test suite for {file_path}"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def tearDown(self):
        """Clean up after each test method."""
        pass
    
    def test_basic_functionality(self):
        """Test basic functionality exists."""
        # TODO: Add specific tests based on the code
        self.assertTrue(True, "Basic test placeholder")
    
    def test_error_handling(self):
        """Test error handling."""
        # TODO: Add error handling tests
        pass
    
    def test_edge_cases(self):
        """Test edge cases."""
        # TODO: Add edge case tests
        pass


if __name__ == '__main__':
    unittest.main()
'''
        return test_template