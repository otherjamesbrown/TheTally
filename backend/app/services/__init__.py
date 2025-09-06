"""
Services module for TheTally backend.

This module contains business logic services that handle core application functionality.
Services are responsible for:
- Business logic implementation
- Data processing and transformation
- Integration with external services
- Complex operations that span multiple models

## Architecture

The services layer follows a clean architecture pattern where:
- Services contain business logic and orchestrate data operations
- Services depend on models for data access but not on API layer
- Services are stateless and can be easily tested
- Services handle transaction boundaries and error handling

## Module Structure

```
services/
├── __init__.py          # This file - module documentation and exports
├── base.py             # Base service class with common functionality
├── auth/               # Authentication related services
│   ├── __init__.py
│   ├── user_service.py
│   └── auth_service.py
├── financial/          # Financial data services
│   ├── __init__.py
│   ├── account_service.py
│   ├── transaction_service.py
│   └── categorization_service.py
└── import/             # Data import services
    ├── __init__.py
    ├── csv_import_service.py
    ├── ofx_import_service.py
    └── qif_import_service.py
```

## Usage Examples

```python
from backend.app.services import UserService, TransactionService
from backend.app.services.auth import AuthService

# Initialize services
user_service = UserService()
auth_service = AuthService()
transaction_service = TransactionService()

# Use services
user = await user_service.create_user(email="user@example.com", password="example_password")  # nosec B105
token = await auth_service.authenticate_user(email="user@example.com", password="example_password")  # nosec B105
transactions = await transaction_service.get_user_transactions(user_id=user.id)
```

## AI-Friendly Development

This module is designed to be AI-friendly with:
- Clear separation of concerns
- Comprehensive docstrings and type hints
- Consistent naming conventions
- Well-defined interfaces and contracts
- Extensive examples and usage patterns
"""

# Import all service classes for easy access
from .base import BaseService

# Re-export commonly used services
__all__ = [
    "BaseService",
    # Add other service exports as they are implemented
]
