# Python Code Quality Guidelines

## Code Style
Follow PEP 8 standards for Python code:
- Use 4 spaces for indentation
- Maximum line length of 79 characters
- Use descriptive variable and function names
- Add docstrings to all functions and classes

## Documentation
```python
def calculate_total(items: List[Item]) -> float:
    """Calculate the total price of items.
    
    Args:
        items: List of Item objects with price attributes
        
    Returns:
        The total price as a float
        
    Raises:
        ValueError: If any item has invalid price
    """
    return sum(item.price for item in items)
```

## Type Hints
Always use type hints for better code maintainability:

```python
from typing import List, Optional, Dict, Any

def process_data(data: Dict[str, Any]) -> Optional[List[str]]:
    if not data:
        return None
    return [str(value) for value in data.values()]
```

## Error Handling
Implement proper exception handling:

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise RuntimeError("Operation failed") from e
```