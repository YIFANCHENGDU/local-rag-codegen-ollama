# FastAPI Best Practices

## Project Structure
A well-organized FastAPI project should follow these patterns:

```
app/
├── __init__.py
├── main.py          # FastAPI app entry point
├── config.py        # Configuration settings
├── models/          # Pydantic models
├── routers/         # API route handlers  
├── services/        # Business logic
└── utils/           # Utility functions
```

## API Design
- Use descriptive endpoint names
- Follow RESTful conventions
- Include proper HTTP status codes
- Provide clear error messages
- Use Pydantic models for request/response validation

## Error Handling
```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    try:
        # Your logic here
        return {"item_id": item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Testing
Use pytest for testing FastAPI applications:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
```