from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
from app.core.rag import rag_system
from app.core.ollama_client import ollama_client
from app.agents.coordinator import multi_agent_coordinator
from app.utils.workspace import write_files_to_workspace, get_workspace_info

app = FastAPI(
    title="Local RAG + Multi-Agent Codegen",
    description="RAG-powered multi-agent code generation system using Ollama",
    version="1.0.0"
)

# Request/Response models
class IngestRequest(BaseModel):
    path: str

class QuestionRequest(BaseModel):
    question: str

class GenerateCodeRequest(BaseModel):
    instruction: str
    apply: bool = False

class IngestResponse(BaseModel):
    message: str
    files_processed: int

class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict[str, Any]]

class GenerateCodeResponse(BaseModel):
    instruction: str
    applied: bool
    workflow: str
    agents_involved: List[Dict[str, str]]
    files: List[Dict[str, Any]]
    commands: List[str]
    notes: str
    product_manager_analysis: Optional[Dict[str, Any]] = None
    developer_implementation: Optional[Dict[str, Any]] = None
    tester_review: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "Local RAG + Multi-Agent Codegen System",
        "version": "1.0.0",
        "agents": ["Product Manager", "Developer", "Tester"],
        "endpoints": ["/ingest", "/ask", "/generate_code", "/workspace/info"]
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """Ingest documents from a directory into the RAG system."""
    try:
        result = await rag_system.ingest_documents(request.path)
        return IngestResponse(
            message=result["message"],
            files_processed=result["files_processed"]
        )
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question using the RAG system."""
    try:
        # Search for relevant documents
        relevant_docs = await rag_system.search_documents(request.question, n_results=3)
        
        # Build context from retrieved documents
        context = "\n\n".join([doc["content"][:500] for doc in relevant_docs])
        
        # Generate response
        prompt = f"""Based on the following context from the knowledge base, please answer the user's question.

Context:
{context}

Question: {request.question}

Please provide a helpful and accurate answer based on the context provided."""
        
        answer = await ollama_client.generate_response(prompt)
        
        # Format sources
        sources = [
            {
                "content": doc["content"][:200] + "...",
                "source": doc["metadata"].get("source", "unknown"),
                "distance": doc.get("distance", 0)
            }
            for doc in relevant_docs
        ]
        
        return QuestionResponse(
            question=request.question,
            answer=answer,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Question answering error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_code", response_model=GenerateCodeResponse)
async def generate_code(request: GenerateCodeRequest):
    """Generate code using the multi-agent system."""
    try:
        logger.info(f"Generating code for: {request.instruction}")
        
        # Execute multi-agent workflow
        result = await multi_agent_coordinator.generate_code(request.instruction)
        
        # Extract files for workspace
        files_to_write = await multi_agent_coordinator.get_files_for_workspace(result)
        
        # Extract setup commands
        commands = await multi_agent_coordinator.get_setup_commands(result)
        
        written_files = []
        if request.apply and files_to_write:
            # Write files to workspace
            written_files = write_files_to_workspace(files_to_write)
        else:
            # Just return file information without writing
            written_files = [
                {
                    "path": f"workspace/{file_info['path']}",
                    "bytes": len(file_info["content"].encode('utf-8')),
                    "source": file_info.get("source", "unknown"),
                    "description": file_info.get("description", "")
                }
                for file_info in files_to_write
            ]
        
        # Compile notes
        notes_parts = []
        if result.get("product_manager", {}).get("specifications"):
            specs = result["product_manager"]["specifications"]
            notes_parts.append(f"PM Analysis: {specs.get('analysis', 'Requirements analyzed')}")
        
        if result.get("developer", {}).get("implementation", {}).get("notes"):
            notes_parts.append(f"Dev Notes: {result['developer']['implementation']['notes']}")
        
        if result.get("tester", {}).get("review", {}).get("review_summary"):
            notes_parts.append(f"QA Review: {result['tester']['review']['review_summary']}")
        
        notes = " | ".join(notes_parts) if notes_parts else "Multi-agent code generation completed successfully"
        
        return GenerateCodeResponse(
            instruction=request.instruction,
            applied=request.apply,
            workflow="multi-agent",
            agents_involved=result.get("agents_involved", []),
            files=written_files,
            commands=commands,
            notes=notes,
            product_manager_analysis=result.get("product_manager", {}).get("specifications"),
            developer_implementation=result.get("developer", {}).get("implementation"),
            tester_review=result.get("tester", {}).get("review")
        )
        
    except Exception as e:
        logger.error(f"Code generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workspace/info")
async def workspace_info():
    """Get information about the workspace directory."""
    try:
        info = get_workspace_info()
        return info
    except Exception as e:
        logger.error(f"Workspace info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Basic health check
        return {
            "status": "healthy",
            "agents": ["ProductManager", "Developer", "Tester"],
            "components": ["RAG System", "Ollama Client", "Multi-Agent Coordinator"]
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)