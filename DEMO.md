# Multi-Agent Code Generation Demo

This demo shows how to use the multi-agent RAG code generation system with Product Manager, Developer, and Tester agents.

## Quick Start

1. **Start Ollama and pull models:**
```bash
# Install Ollama first: https://ollama.com/download
ollama pull qwen2.5-coder
ollama pull nomic-embed-text
```

2. **Setup environment:**
```bash
pip install -r requirements.txt
cp .env.example .env  # Modify if needed
```

3. **Start the server:**
```bash
uvicorn app.server:app --reload --port 8000
```

## Multi-Agent Workflow Example

### 1. Ingest Documentation
First, add your knowledge base:
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{"path":"./docs"}'
```

### 2. Generate Code with Multi-Agent System
The system will automatically coordinate between three agents:

**Example Request:**
```bash
curl -X POST "http://localhost:8000/generate_code" \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Create a FastAPI user management system with CRUD operations, input validation, and comprehensive tests",
    "apply": true
  }'
```

**What Happens Behind the Scenes:**

1. **Product Manager Agent** analyzes the requirement:
   - Breaks down "user management system" into specific components
   - Creates detailed specifications with acceptance criteria
   - Considers technical constraints and best practices

2. **Developer Agent** implements the code:
   - Uses PM specifications and RAG context from knowledge base
   - Generates complete, functional code files
   - Includes proper error handling and documentation

3. **Tester Agent** reviews and tests:
   - Reviews generated code for bugs and issues
   - Creates comprehensive test suites
   - Provides quality assessment and recommendations

### 3. Example Response Structure
```json
{
  "instruction": "Create a FastAPI user management system...",
  "applied": true,
  "workflow": "multi-agent",
  "agents_involved": [
    {"name": "ProductManager", "role": "Product Manager"},
    {"name": "Developer", "role": "Developer"},
    {"name": "Tester", "role": "Quality Assurance Tester"}
  ],
  "files": [
    {"path": "workspace/user_management/main.py", "bytes": 1234},
    {"path": "workspace/user_management/models.py", "bytes": 567},
    {"path": "workspace/tests/test_user_management.py", "bytes": 890}
  ],
  "commands": ["pip install fastapi uvicorn pydantic", "python -m pytest"],
  "notes": "PM Analysis: Requirements analyzed for user CRUD operations | Dev Notes: Implemented with proper validation and error handling | QA Review: Code quality score 9/10, comprehensive tests included"
}
```

## Agent Responsibilities

### Product Manager Agent
- **Input**: User instruction + RAG context
- **Process**: Analyzes requirements, identifies components, creates specifications
- **Output**: Structured JSON with components, requirements, acceptance criteria

### Developer Agent  
- **Input**: PM specifications + RAG context with code examples
- **Process**: Implements code based on specs, follows best practices
- **Output**: Complete code files with proper structure and documentation

### Tester Agent
- **Input**: Original instruction + PM specs + Developer code
- **Process**: Reviews code quality, creates test suites, identifies issues
- **Output**: Code review, test files, quality assessment

## API Endpoints

- `GET /` - System information
- `POST /ingest` - Add documents to knowledge base
- `POST /ask` - Ask questions using RAG
- `POST /generate_code` - Multi-agent code generation
- `GET /workspace/info` - Workspace directory information
- `GET /health` - Health check

## Configuration

Environment variables (see `.env.example`):
- `OLLAMA_HOST` - Ollama server URL
- `LLM_MODEL` - Language model for code generation
- `EMBEDDING_MODEL` - Model for text embeddings
- `WORKSPACE_DIR` - Directory for generated files
- `CHROMA_DIR` - ChromaDB storage directory

## Example Use Cases

1. **Web API Development:**
   ```
   "Create a REST API for a book library with authentication, CRUD operations, and rate limiting"
   ```

2. **Data Processing Pipeline:**
   ```
   "Build a data processing pipeline that reads CSV files, validates data, and outputs to database with error handling"
   ```

3. **Microservice Architecture:**
   ```  
   "Design a microservice for order processing with event-driven communication and comprehensive logging"
   ```

## Security Features

- **Path Traversal Protection**: Only allows writing to designated workspace directory
- **Input Validation**: All API inputs validated with Pydantic models
- **Error Handling**: Comprehensive error handling and logging

## Extending the System

### Adding New Agents
1. Create agent class inheriting from `BaseAgent`
2. Implement required methods: `_get_system_prompt()`, `_build_prompt()`, `_parse_response()`
3. Add to `MultiAgentCoordinator`

### Customizing Workflows
- Modify `MultiAgentCoordinator.generate_code()` method
- Add agent-to-agent communication
- Implement iterative refinement loops

## Troubleshooting

1. **Ollama Connection Issues:**
   - Ensure Ollama is running: `ollama serve`
   - Check `OLLAMA_HOST` in environment

2. **Model Not Found:**
   - Pull required models: `ollama pull qwen2.5-coder`

3. **Import Errors:**
   - Install dependencies: `pip install -r requirements.txt`
   - Check Python version (3.10+ required)