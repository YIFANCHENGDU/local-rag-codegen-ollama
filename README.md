# Local RAG + Codegen (Ollama + Python)

一个运行在本地的 RAG 系统，使用 Ollama 提供模型推理和向量化（embeddings），支持从你的知识库检索并“自动生成代码”，可选择把生成的文件写入工作目录。

## 功能
- 文档目录一键入库（txt、md、pdf）
- 基于 Chroma 的向量检索
- 使用 Ollama 的本地大模型进行回答（默认 qwen2.5-coder）
- 自动代码生成（根据检索到的上下文 + 指令），并可写入 `workspace/` 目录

## 快速开始

### 1) 依赖
- Python 3.10+
- [Ollama](https://ollama.com/download)

```bash
# 模型（推荐，可替换）
ollama pull qwen2.5-coder
ollama pull nomic-embed-text

# Python 依赖
pip install -r requirements.txt
```

### 2) 配置环境（可选）
复制 `.env.example` 为 `.env` 并按需修改：
```
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=qwen2.5-coder
EMBEDDING_MODEL=nomic-embed-text
CHROMA_DIR=.chroma
WORKSPACE_DIR=workspace
COLLECTION_NAME=local_rag
```

### 3) 运行服务
```bash
uvicorn app.server:app --reload --port 8000
```

### 4) 导入文档
将你的资料放到如 `./docs` 目录（支持 txt、md、pdf），然后：
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{"path":"./docs"}'
```

### 5) 提问
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"请根据知识库说明我项目如何启动？"}'
```

### 6) 自动生成代码
- 仅预览（不落盘）：
```bash
curl -X POST "http://localhost:8000/generate_code" \
  -H "Content-Type: application/json" \
  -d '{"instruction":"生成一个FastAPI的健康检查接口示例，并提供启动脚本","apply":false}'
```

- 生成并写入 `workspace/`：
```bash
curl -X POST "http://localhost:8000/generate_code" \
  -H "Content-Type: application/json" \
  -d '{"instruction":"生成一个FastAPI的健康检查接口示例，并提供启动脚本","apply":true}'
```

返回示例（节选）：
```json
{
  "applied": true,
  "files": [
    {"path":"workspace/app/main.py","bytes": 345},
    {"path":"workspace/run.sh","bytes": 87}
  ],
  "commands": ["pip install fastapi uvicorn", "bash workspace/run.sh"],
  "notes": "..."
}
```

## 设计要点
- 完全本地化：向量化与推理均通过 Ollama 完成
- 简洁可读：不依赖 LangChain/LlamaIndex，便于定制
- 安全写盘：只允许写入 `WORKSPACE_DIR` 下的文件，防止路径穿越
- 可扩展：你可以把 `/generate_code` 的策略改成 function-calling 风格或增加执行器

## 常见问题
- Embedding 模型维度应一致：索引与查询都使用同一个 `EMBEDDING_MODEL`
- PDF 解析质量：本示例用 `pypdf`，如需要更高质量可替换为 `unstructured` 等
- 模型选择：代码生成建议 coder 类模型（qwen2.5-coder, deepseek-coder 等）

## 许可
MIT