#!/usr/bin/env python3
"""
Example demonstrating the multi-agent workflow with mock data
(doesn't require Ollama to be running)
"""

import sys
import os
import json
import asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def mock_generate_response(prompt: str, system_prompt: str = None) -> str:
    """Mock Ollama response for testing."""
    
    if "product manager" in system_prompt.lower():
        return json.dumps({
            "analysis": "User requests a FastAPI health check endpoint with startup script",
            "specifications": [
                {
                    "component": "Health Check API",
                    "description": "Simple HTTP endpoint that returns system status",
                    "requirements": [
                        "Create GET /health endpoint",
                        "Return JSON response with status",
                        "Include timestamp and basic system info"
                    ],
                    "acceptance_criteria": [
                        "Endpoint responds with 200 status",
                        "Returns valid JSON structure",
                        "Includes status field"
                    ]
                },
                {
                    "component": "Startup Script",
                    "description": "Shell script to launch the application",
                    "requirements": [
                        "Install dependencies",
                        "Start uvicorn server",
                        "Handle basic error cases"
                    ],
                    "acceptance_criteria": [
                        "Script is executable",
                        "Installs required packages",
                        "Starts server on correct port"
                    ]
                }
            ],
            "technical_considerations": [
                "Use FastAPI framework",
                "Include proper error handling",
                "Follow REST conventions"
            ],
            "success_metrics": [
                "Health endpoint responds correctly",
                "Application starts successfully",
                "No runtime errors"
            ]
        })
    
    elif "developer" in system_prompt.lower():
        return json.dumps({
            "implementation_plan": "Creating FastAPI health check endpoint and startup script",
            "files": [
                {
                    "path": "main.py",
                    "content": '''from fastapi import FastAPI
from datetime import datetime
import sys

app = FastAPI(title="Health Check Demo", version="1.0.0")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "python_version": sys.version.split()[0]
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "FastAPI Health Check Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
                    "description": "Main FastAPI application with health check endpoint"
                },
                {
                    "path": "start.sh",
                    "content": '''#!/bin/bash
echo "Starting FastAPI Health Check Service..."

# Install dependencies
pip install fastapi uvicorn

# Start the server
echo "Starting server on port 8000..."
python main.py
''',
                    "description": "Startup script for the application"
                }
            ],
            "dependencies": ["fastapi", "uvicorn"],
            "setup_commands": ["chmod +x start.sh", "bash start.sh"],
            "notes": "Created simple health check endpoint with proper JSON response and startup script"
        })
    
    elif "tester" in system_prompt.lower():
        return json.dumps({
            "review_summary": "Code quality is good with proper structure and error handling",
            "issues_found": [
                {
                    "severity": "low",
                    "file": "main.py",
                    "issue": "Could add more detailed health information",
                    "suggestion": "Consider adding database connectivity check"
                }
            ],
            "test_files": [
                {
                    "path": "test_main.py",
                    "content": '''import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
    assert "python_version" in data

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data

def test_health_response_structure():
    """Test health response has correct structure."""
    response = client.get("/health")
    data = response.json()
    
    required_fields = ["status", "timestamp", "version", "python_version"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
''',
                    "description": "Comprehensive tests for the health check API"
                }
            ],
            "recommendations": [
                "Add integration tests",
                "Consider adding monitoring endpoints",
                "Add request/response logging"
            ],
            "quality_score": "8",
            "requirements_coverage": "Fully covers basic health check requirements with room for enhancement"
        })
    
    return "Mock response generated"

async def mock_generate_embedding(text: str) -> list:
    """Mock embedding generation."""
    # Return a simple mock embedding vector
    return [0.1] * 384  # Typical embedding size

async def demo_multi_agent_workflow():
    """Demonstrate the multi-agent workflow with mock responses."""
    
    print("🚀 Multi-Agent Code Generation Demo")
    print("=" * 50)
    print("This demo shows the workflow without requiring Ollama")
    print()
    
    # Mock the Ollama client
    from app.core.ollama_client import ollama_client
    ollama_client.generate_response = mock_generate_response
    ollama_client.generate_embedding = mock_generate_embedding
    
    # Initialize coordinator  
    from app.agents.coordinator import MultiAgentCoordinator
    coordinator = MultiAgentCoordinator()
    
    # Test instruction
    instruction = "生成一个FastAPI的健康检查接口示例，并提供启动脚本"
    
    print(f"📋 Instruction: {instruction}")
    print("\n🤖 Starting multi-agent workflow...")
    
    try:
        # Execute the workflow
        result = await coordinator.generate_code(instruction)
        
        print(f"\n✅ Workflow completed successfully!")
        print(f"   Agents involved: {len(result['agents_involved'])}")
        
        # Show Product Manager results
        pm_specs = result.get("product_manager", {}).get("specifications", {})
        print(f"\n📊 Product Manager Analysis:")
        print(f"   - Analysis: {pm_specs.get('analysis', 'N/A')}")
        print(f"   - Components: {len(pm_specs.get('specifications', []))}")
        
        # Show Developer results  
        dev_impl = result.get("developer", {}).get("implementation", {})
        files = dev_impl.get("files", [])
        print(f"\n💻 Developer Implementation:")
        print(f"   - Files generated: {len(files)}")
        for file_info in files:
            print(f"     • {file_info['path']} ({len(file_info['content'])} chars)")
        
        # Show Tester results
        test_review = result.get("tester", {}).get("review", {})
        test_files = test_review.get("test_files", [])
        print(f"\n🧪 Tester Review:")
        print(f"   - Quality Score: {test_review.get('quality_score', 'N/A')}/10")
        print(f"   - Issues Found: {len(test_review.get('issues_found', []))}")
        print(f"   - Test Files: {len(test_files)}")
        
        # Extract files for workspace
        files_to_write = await coordinator.get_files_for_workspace(result)
        print(f"\n📁 Files ready for workspace: {len(files_to_write)}")
        
        # Show setup commands
        commands = await coordinator.get_setup_commands(result)
        print(f"\n⚡ Setup commands: {len(commands)}")
        for cmd in commands:
            print(f"   • {cmd}")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"   This workflow would generate {len(files_to_write)} files and {len(commands)} commands")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main demo function."""
    success = await demo_multi_agent_workflow()
    
    if success:
        print("\n📝 To use with real Ollama:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull models: ollama pull qwen2.5-coder")
        print("3. Pull embeddings: ollama pull nomic-embed-text")
        print("4. Start server: uvicorn app.server:app --port 8000")
        print("5. Use curl or web interface to generate code")
        return 0
    else:
        print("\n❌ Demo failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)