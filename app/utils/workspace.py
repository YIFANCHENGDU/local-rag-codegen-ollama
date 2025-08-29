import os
from pathlib import Path
from typing import List, Dict, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def is_safe_path(path: str) -> bool:
    """Check if the path is safe to write to (within workspace directory)."""
    try:
        # Resolve path and check if it's within workspace
        resolved_path = Path(settings.workspace_dir).resolve() / Path(path).name
        workspace_path = Path(settings.workspace_dir).resolve()
        
        # Check if resolved path starts with workspace path
        return str(resolved_path).startswith(str(workspace_path))
    except Exception as e:
        logger.warning(f"Path safety check failed for {path}: {e}")
        return False


def write_files_to_workspace(files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Write files to workspace directory safely."""
    written_files = []
    
    for file_info in files:
        try:
            file_path = file_info["path"]
            content = file_info["content"]
            
            # Ensure path is safe
            if not is_safe_path(file_path):
                logger.warning(f"Unsafe path detected, skipping: {file_path}")
                continue
            
            # Create full path within workspace
            full_path = Path(settings.workspace_dir) / Path(file_path)
            
            # Create directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Get file size
            file_size = os.path.getsize(full_path)
            
            written_files.append({
                "path": str(full_path),
                "bytes": file_size,
                "source": file_info.get("source", "unknown"),
                "description": file_info.get("description", "")
            })
            
            logger.info(f"Successfully wrote {file_path} ({file_size} bytes)")
            
        except Exception as e:
            logger.error(f"Failed to write file {file_info.get('path', 'unknown')}: {e}")
    
    return written_files


def get_workspace_info() -> Dict[str, Any]:
    """Get information about the workspace directory."""
    try:
        workspace_path = Path(settings.workspace_dir)
        if not workspace_path.exists():
            return {"exists": False, "files": [], "total_size": 0}
        
        files = []
        total_size = 0
        
        for file_path in workspace_path.rglob("*"):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                relative_path = file_path.relative_to(workspace_path)
                files.append({
                    "path": str(relative_path),
                    "size": file_size,
                    "modified": file_path.stat().st_mtime
                })
                total_size += file_size
        
        return {
            "exists": True,
            "files": files,
            "total_files": len(files),
            "total_size": total_size,
            "workspace_path": str(workspace_path.resolve())
        }
        
    except Exception as e:
        logger.error(f"Error getting workspace info: {e}")
        return {"exists": False, "error": str(e)}