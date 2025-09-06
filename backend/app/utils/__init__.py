"""
Utils module for TheTally backend.

This module contains utility functions and helper classes that are used across the application.
Utils are responsible for:
- Common helper functions
- Data validation utilities
- Formatting and parsing functions
- Shared business logic helpers
- Security utilities
- Logging utilities
- Testing utilities

## Security & Logging Integration

All utilities follow security-first principles:
- Input validation and sanitization
- Secure password handling
- JWT token utilities
- Audit logging for security events
- Structured logging with security context

## Module Structure

```
utils/
├── __init__.py          # This file - module documentation and exports
├── security.py          # Security utilities (passwords, JWT, validation)
├── logging.py           # Logging utilities and formatters
├── validation.py        # Data validation and sanitization
├── formatting.py        # Data formatting and parsing
├── testing.py           # Testing utilities and fixtures
└── crypto.py            # Cryptographic utilities
```

## Usage Examples

```python
from backend.app.utils import validate_email, hash_password, generate_jwt_token
from backend.app.utils.security import SecurityUtils
from backend.app.utils.logging import get_audit_logger

# Security utilities
hashed_password = hash_password("example_password")
is_valid = validate_email("user@example.com")
token = generate_jwt_token(user_id="123", tenant_id="tenant_456")

# Logging utilities
audit_logger = get_audit_logger()
audit_logger.info("User login attempt", user_id="123", ip_address="192.168.1.1")

# Validation utilities
from backend.app.utils.validation import validate_transaction_data
is_valid = validate_transaction_data({"amount": 100.50, "description": "Test"})
```

## AI-Friendly Development

This module is designed to be AI-friendly with:
- Clear separation of concerns
- Comprehensive docstrings and type hints
- Consistent error handling
- Extensive examples and usage patterns
- Security-first design principles
"""

# Import commonly used utilities
from .security import SecurityUtils
from .logging import LoggingUtils, get_audit_logger, get_functional_logger, get_debug_logger
from .validation import ValidationUtils

# Re-export commonly used utilities
__all__ = [
    "SecurityUtils",
    "LoggingUtils",
    "get_audit_logger",
    "get_functional_logger", 
    "get_debug_logger",
    "ValidationUtils",
    # Add other utility exports as they are implemented
]
