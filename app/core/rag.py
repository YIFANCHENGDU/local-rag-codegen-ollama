import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import os
import logging
from pathlib import Path
import pypdf
from app.config import settings
from app.core.ollama_client import ollama_client

logger = logging.getLogger(__name__)


class RAGSystem:
    """RAG system using ChromaDB for document storage and retrieval."""
    
    def __init__(self):
        # Initialize ChromaDB
        chroma_settings = ChromaSettings(
            persist_directory=settings.chroma_dir,
            anonymized_telemetry=False
        )
        self.client = chromadb.PersistentClient(settings=chroma_settings)
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    async def ingest_documents(self, path: str) -> Dict[str, Any]:
        """Ingest documents from a directory path."""
        try:
            documents = []
            metadatas = []
            ids = []
            
            path_obj = Path(path)
            if not path_obj.exists():
                raise ValueError(f"Path does not exist: {path}")
            
            # Process files
            files_processed = 0
            for file_path in path_obj.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.md', '.pdf']:
                    content = await self._extract_content(file_path)
                    if content.strip():
                        documents.append(content)
                        metadatas.append({
                            "source": str(file_path),
                            "type": file_path.suffix.lower()
                        })
                        ids.append(f"doc_{len(documents)}")
                        files_processed += 1
            
            if not documents:
                return {"message": "No documents found to process", "files_processed": 0}
            
            # Generate embeddings
            embeddings = []
            for doc in documents:
                embedding = await ollama_client.generate_embedding(doc)
                embeddings.append(embedding)
            
            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            return {
                "message": f"Successfully ingested {files_processed} documents",
                "files_processed": files_processed
            }
            
        except Exception as e:
            logger.error(f"Error ingesting documents: {e}")
            raise
    
    async def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query."""
        try:
            # Generate query embedding
            query_embedding = await ollama_client.generate_embedding(query)
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    async def _extract_content(self, file_path: Path) -> str:
        """Extract content from different file types."""
        try:
            if file_path.suffix.lower() == '.pdf':
                return await self._extract_pdf_content(file_path)
            else:
                # Handle txt and md files
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Could not extract content from {file_path}: {e}")
            return ""
    
    async def _extract_pdf_content(self, file_path: Path) -> str:
        """Extract content from PDF file."""
        try:
            reader = pypdf.PdfReader(str(file_path))
            content = ""
            for page in reader.pages:
                content += page.extract_text() + "\n"
            return content
        except Exception as e:
            logger.warning(f"Could not extract PDF content from {file_path}: {e}")
            return ""


# Global RAG system instance
rag_system = RAGSystem()