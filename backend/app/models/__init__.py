"""
Models module for TheTally backend.

This module contains SQLAlchemy database models that represent the application's data structure.
Models are responsible for:
- Database table definitions
- Relationships between entities
- Database-level constraints and validations
- ORM mappings

## Architecture

The models layer follows these principles:
- Multi-tenant architecture with tenant_id isolation
- Clear separation between core entities and relationships
- Comprehensive validation and constraints
- Audit fields (created_at, updated_at) on all models
- Soft delete support where appropriate

## Module Structure

```
models/
├── __init__.py          # This file - module documentation and exports
├── base.py             # Base model class with common functionality
├── user.py             # User and authentication models
├── financial.py        # Financial data models (accounts, transactions)
├── categorization.py   # Categorization and rules models
└── audit.py            # Audit and logging models
```

## Multi-Tenant Design

All models include tenant_id for data isolation:
- Users belong to tenants (organizations)
- All financial data is scoped to tenants
- Queries automatically filter by tenant_id
- Prevents cross-tenant data access

## Usage Examples

```python
from backend.app.models import User, Account, Transaction
from backend.app.models.base import BaseModel

# Create a new user
user = User(
    email="user@example.com",
    tenant_id="tenant_123",
    is_active=True
)

# Create an account
account = Account(
    name="Current Account",
    account_type="checking",
    tenant_id="tenant_123",
    user_id=user.id
)

# Create a transaction
transaction = Transaction(
    description="Grocery shopping at Tesco",
    amount=-45.67,
    account_id=account.id,
    tenant_id="tenant_123"
)
```

## AI-Friendly Development

This module is designed to be AI-friendly with:
- Clear model relationships and constraints
- Comprehensive docstrings and type hints
- Consistent naming conventions
- Well-defined validation rules
- Extensive examples and usage patterns
"""

# Import base model for common functionality
from .base import BaseModel
from .user import User
from .tenant import Tenant
from .account import Account
from .transaction import Transaction
from .category import Category
from .categorization_rule import CategorizationRule

# Re-export commonly used models
__all__ = [
    "BaseModel",
    "User",
    "Tenant",
    "Account",
    "Transaction",
    "Category",
    "CategorizationRule",
]
