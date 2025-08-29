#!/usr/bin/env python3
"""
Test script to validate the multi-agent system structure and functionality
without requiring Ollama to be running.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🧪 Testing module imports...")
    
    try:
        from app.config import settings
        print("✅ Config module imported")
        
        from app.core.ollama_client import OllamaClient
        print("✅ Ollama client module imported")
        
        from app.core.rag import RAGSystem
        print("✅ RAG system module imported")
        
        from app.agents.base import BaseAgent
        print("✅ Base agent module imported")
        
        from app.agents.product_manager import ProductManagerAgent
        print("✅ Product Manager agent imported")
        
        from app.agents.developer import DeveloperAgent
        print("✅ Developer agent imported")
        
        from app.agents.tester import TesterAgent
        print("✅ Tester agent imported")
        
        from app.agents.coordinator import MultiAgentCoordinator
        print("✅ Multi-agent coordinator imported")
        
        from app.utils.workspace import write_files_to_workspace, is_safe_path
        print("✅ Workspace utilities imported")
        
        from app.server import app
        print("✅ FastAPI server imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_initialization():
    """Test that agents can be initialized properly."""
    print("\n🤖 Testing agent initialization...")
    
    try:
        from app.agents.coordinator import MultiAgentCoordinator
        
        coordinator = MultiAgentCoordinator()
        
        # Check agent properties
        assert coordinator.product_manager.name == "ProductManager"
        assert coordinator.developer.name == "Developer"  
        assert coordinator.tester.name == "Tester"
        
        print("✅ Product Manager agent initialized")
        print("✅ Developer agent initialized")
        print("✅ Tester agent initialized")
        print("✅ Multi-agent coordinator initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False

def test_workspace_utils():
    """Test workspace utility functions."""
    print("\n📁 Testing workspace utilities...")
    
    try:
        from app.utils.workspace import is_safe_path, get_workspace_info
        
        # Test path safety
        assert is_safe_path("test.py") == True
        assert is_safe_path("../../../etc/passwd") == False
        print("✅ Path safety validation works")
        
        # Test workspace info
        info = get_workspace_info()
        assert "exists" in info
        print("✅ Workspace info function works")
        
        return True
        
    except Exception as e:
        print(f"❌ Workspace utilities test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n⚙️  Testing configuration...")
    
    try:
        from app.config import settings
        
        # Check default values
        assert settings.llm_model == "qwen2.5-coder"
        assert settings.embedding_model == "nomic-embed-text"
        assert settings.workspace_dir == "workspace"
        
        print(f"✅ LLM Model: {settings.llm_model}")
        print(f"✅ Embedding Model: {settings.embedding_model}")
        print(f"✅ Workspace Dir: {settings.workspace_dir}")
        print(f"✅ Ollama Host: {settings.ollama_host}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_fastapi_structure():
    """Test FastAPI application structure."""
    print("\n🚀 Testing FastAPI structure...")
    
    try:
        from app.server import app
        
        # Check app properties
        assert app.title == "Local RAG + Multi-Agent Codegen"
        assert app.version == "1.0.0"
        
        # Check routes exist
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/ingest", "/ask", "/generate_code", "/workspace/info", "/health"]
        
        for route in expected_routes:
            assert route in routes, f"Route {route} not found"
        
        print("✅ FastAPI app configured correctly")
        print("✅ All required routes present")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI structure test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Multi-Agent RAG Codegen System Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_agent_initialization, 
        test_workspace_utils,
        test_fastapi_structure
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n📊 Test Results:")
    print("=" * 30)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! The multi-agent system is ready to use.")
        print("\n📝 Next steps:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull models: ollama pull qwen2.5-coder && ollama pull nomic-embed-text")
        print("3. Start server: uvicorn app.server:app --reload --port 8000")
        print("4. Test the API endpoints as shown in DEMO.md")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please fix issues before using the system.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)