# Services Documentation

This document provides comprehensive documentation for TheTally backend services, including usage examples, API references, and best practices.

## Overview

The services layer in TheTally provides business logic and data operations for the application. All services inherit from `BaseService` and follow consistent patterns for error handling, logging, and database operations.

## Service Architecture

### BaseService

All services inherit from `BaseService`, which provides:
- Database session management
- Structured logging with `structlog`
- Common CRUD operations
- Error handling and transaction management
- Context manager support

### Service Classes

1. **UserService** - User management operations
2. **AccountService** - Financial account management
3. **TransactionService** - Transaction processing
4. **CategoryService** - Category management
5. **CategorizationService** - Automated categorization
6. **AuthService** - Authentication and authorization

## UserService

### Purpose
Manages user accounts, profiles, and user-related operations.

### Key Features
- User CRUD operations
- Profile management
- User search and filtering
- User status management (activate/deactivate)
- Bulk operations
- User statistics

### Usage Examples

```python
from app.services import UserService
from app.schemas.auth import UserRegisterRequest, UserUpdateRequest

# Initialize service
user_service = UserService()

# Create a new user
user_data = UserRegisterRequest(
    email="user@example.com",
    username="johndoe",
    first_name="John",
    last_name="Doe",
    password="securepassword123"
)
user = user_service.create_user(user_data, "tenant_123", "admin_123")

# Get user by ID
user = user_service.get_user_by_id("user_123", "tenant_123")

# Search users
users = user_service.search_users("tenant_123", "john", limit=10)

# Update user
update_data = UserUpdateRequest(first_name="Johnny")
updated_user = user_service.update_user("user_123", "tenant_123", update_data, "admin_123")

# Activate/deactivate user
user_service.activate_user("user_123", "tenant_123", "admin_123")
user_service.deactivate_user("user_123", "tenant_123", "admin_123")

# Get user statistics
stats = user_service.get_user_stats("tenant_123")
print(f"Total users: {stats['total_users']}")
print(f"Active users: {stats['active_users']}")
```

### API Reference

#### Methods

- `create_user(user_data, tenant_id, created_by=None)` - Create new user
- `get_user_by_id(user_id, tenant_id)` - Get user by ID
- `get_user_by_email(email, tenant_id)` - Get user by email
- `get_user_by_username(username, tenant_id)` - Get user by username
- `get_users(tenant_id, limit=None, offset=None, active_only=True)` - Get users
- `search_users(tenant_id, search_term, limit=None)` - Search users
- `update_user(user_id, tenant_id, update_data, updated_by=None)` - Update user
- `activate_user(user_id, tenant_id, updated_by=None)` - Activate user
- `deactivate_user(user_id, tenant_id, updated_by=None)` - Deactivate user
- `delete_user(user_id, tenant_id, deleted_by=None)` - Soft delete user
- `restore_user(user_id, tenant_id, restored_by=None)` - Restore deleted user
- `get_user_stats(tenant_id)` - Get user statistics
- `bulk_update_users(user_ids, tenant_id, update_data, updated_by=None)` - Bulk update

## AccountService

### Purpose
Manages financial accounts, balances, and account-related operations.

### Key Features
- Account CRUD operations
- Balance management and updates
- Account type validation
- Account hierarchy support
- Account archiving
- Account statistics

### Usage Examples

```python
from app.services import AccountService
from decimal import Decimal

# Initialize service
account_service = AccountService()

# Create a new account
account = account_service.create_account(
    name="Main Checking",
    account_type="current",
    user_id="user_123",
    tenant_id="tenant_123",
    institution_name="Bank of Example",
    currency="USD"
)

# Get account by ID
account = account_service.get_account_by_id(1, "tenant_123")

# Get accounts for user
accounts = account_service.get_accounts_by_user("user_123", "tenant_123")

# Update account balance
account_service.update_balance(1, "tenant_123", Decimal('1500.00'), "current", "admin_123")

# Add to balance
account_service.add_to_balance(1, "tenant_123", Decimal('100.00'), "current", "admin_123")

# Archive account
account_service.archive_account(1, "tenant_123", "admin_123")

# Get account statistics
stats = account_service.get_account_stats("tenant_123")
print(f"Total accounts: {stats['total_accounts']}")
print(f"Total balance: {stats['total_balance']}")
```

### API Reference

#### Methods

- `create_account(name, account_type, user_id, tenant_id, **kwargs)` - Create account
- `get_account_by_id(account_id, tenant_id)` - Get account by ID
- `get_accounts_by_user(user_id, tenant_id, active_only=True)` - Get user accounts
- `get_accounts_by_type(account_type, tenant_id, active_only=True)` - Get accounts by type
- `search_accounts(tenant_id, search_term, limit=None)` - Search accounts
- `update_account(account_id, tenant_id, update_data, updated_by=None)` - Update account
- `update_balance(account_id, tenant_id, new_balance, balance_type, updated_by=None)` - Update balance
- `add_to_balance(account_id, tenant_id, amount, balance_type, updated_by=None)` - Add to balance
- `archive_account(account_id, tenant_id, archived_by=None)` - Archive account
- `unarchive_account(account_id, tenant_id, unarchived_by=None)` - Unarchive account
- `delete_account(account_id, tenant_id, deleted_by=None)` - Delete account
- `get_account_balance(account_id, tenant_id)` - Get account balance
- `validate_account_balance(account_id, tenant_id)` - Validate balance consistency
- `get_account_stats(tenant_id)` - Get account statistics

## TransactionService

### Purpose
Manages financial transactions, categorization, and transaction-related operations.

### Key Features
- Transaction CRUD operations
- Transaction queries and filtering
- Balance impact calculations
- Transaction categorization
- Bulk operations
- Transaction statistics

### Usage Examples

```python
from app.services import TransactionService
from decimal import Decimal
from datetime import datetime

# Initialize service
transaction_service = TransactionService()

# Create a new transaction
transaction = transaction_service.create_transaction(
    account_id=1,
    amount=Decimal('50.00'),
    description="Grocery shopping at Tesco",
    transaction_type="debit",
    user_id="user_123",
    tenant_id="tenant_123",
    transaction_date=datetime.utcnow(),
    merchant_name="Tesco"
)

# Get transaction by ID
transaction = transaction_service.get_transaction_by_id(1, "tenant_123")

# Get transactions for account
transactions = transaction_service.get_transactions_by_account(
    account_id=1,
    tenant_id="tenant_123",
    limit=50,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31)
)

# Categorize transaction
transaction_service.categorize_transaction(
    transaction_id=1,
    tenant_id="tenant_123",
    category="Groceries",
    subcategory="Food",
    confidence=0.95,
    rule_id=5,
    updated_by="admin_123"
)

# Reconcile transaction
transaction_service.reconcile_transaction(1, "tenant_123", "admin_123")

# Get transaction statistics
stats = transaction_service.get_transaction_stats("tenant_123", "user_123")
print(f"Total transactions: {stats['total_transactions']}")
print(f"Total amount: {stats['total_amount']}")
```

### API Reference

#### Methods

- `create_transaction(account_id, amount, description, transaction_type, user_id, tenant_id, **kwargs)` - Create transaction
- `get_transaction_by_id(transaction_id, tenant_id)` - Get transaction by ID
- `get_transactions_by_account(account_id, tenant_id, **filters)` - Get account transactions
- `get_transactions_by_user(user_id, tenant_id, **filters)` - Get user transactions
- `search_transactions(tenant_id, search_term, limit=None)` - Search transactions
- `get_transactions_by_category(category, tenant_id, limit=None)` - Get transactions by category
- `update_transaction(transaction_id, tenant_id, update_data, updated_by=None)` - Update transaction
- `categorize_transaction(transaction_id, tenant_id, category, **kwargs)` - Categorize transaction
- `reconcile_transaction(transaction_id, tenant_id, reconciled_by=None)` - Reconcile transaction
- `delete_transaction(transaction_id, tenant_id, deleted_by=None)` - Delete transaction
- `get_transaction_stats(tenant_id, user_id=None, **filters)` - Get transaction statistics

## CategoryService

### Purpose
Manages transaction categories, hierarchies, and category-related operations.

### Key Features
- Category CRUD operations
- Hierarchy management (parent/child relationships)
- Category search and filtering
- Budget management
- Category usage tracking
- Category statistics

### Usage Examples

```python
from app.services import CategoryService
from decimal import Decimal
from datetime import datetime

# Initialize service
category_service = CategoryService()

# Create a new category
category = category_service.create_category(
    name="Groceries",
    category_type="expense",
    tenant_id="tenant_123",
    user_id="user_123",
    color="#FF5733",
    icon="shopping-cart"
)

# Create subcategory
subcategory = category_service.create_category(
    name="Food",
    category_type="expense",
    tenant_id="tenant_123",
    parent_id=category.id,
    user_id="user_123"
)

# Get category by ID
category = category_service.get_category_by_id(1, "tenant_123")

# Get categories by type
expense_categories = category_service.get_categories_by_type("expense", "tenant_123")

# Get root categories
root_categories = category_service.get_root_categories("tenant_123", "expense")

# Get subcategories
subcategories = category_service.get_subcategories(category.id, "tenant_123")

# Set budget for category
category_service.set_budget(
    category_id=1,
    tenant_id="tenant_123",
    amount=Decimal('500.00'),
    period="monthly",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    updated_by="admin_123"
)

# Get category statistics
stats = category_service.get_category_stats("tenant_123")
print(f"Total categories: {stats['total_categories']}")
print(f"Most used: {stats['most_used_categories']}")
```

### API Reference

#### Methods

- `create_category(name, category_type, tenant_id, parent_id=None, user_id=None, **kwargs)` - Create category
- `get_category_by_id(category_id, tenant_id)` - Get category by ID
- `get_category_by_slug(slug, tenant_id)` - Get category by slug
- `get_categories_by_type(category_type, tenant_id, active_only=True)` - Get categories by type
- `get_root_categories(tenant_id, category_type=None, active_only=True)` - Get root categories
- `get_subcategories(parent_id, tenant_id, active_only=True)` - Get subcategories
- `search_categories(tenant_id, search_term, category_type=None, limit=None)` - Search categories
- `update_category(category_id, tenant_id, update_data, updated_by=None)` - Update category
- `increment_usage(category_id, tenant_id)` - Increment usage count
- `set_budget(category_id, tenant_id, amount, period, start_date, end_date, updated_by=None)` - Set budget
- `clear_budget(category_id, tenant_id, updated_by=None)` - Clear budget
- `archive_category(category_id, tenant_id, archived_by=None)` - Archive category
- `delete_category(category_id, tenant_id, deleted_by=None)` - Delete category
- `get_category_stats(tenant_id)` - Get category statistics

## CategorizationService

### Purpose
Manages automated transaction categorization using rules and pattern matching.

### Key Features
- Rule management and CRUD operations
- Pattern matching (regex, keywords, amount ranges)
- Bulk categorization operations
- Rule performance tracking
- Rule testing and validation

### Usage Examples

```python
from app.services import CategorizationService
from decimal import Decimal

# Initialize service
categorization_service = CategorizationService()

# Create a keyword rule
rule = categorization_service.create_rule(
    name="Tesco Groceries",
    pattern="Tesco",
    category_id=1,
    rule_type="keyword",
    tenant_id="tenant_123",
    user_id="user_123",
    is_case_sensitive=False,
    field_to_match="description"
)

# Create a regex rule
regex_rule = categorization_service.create_rule(
    name="Restaurant Pattern",
    pattern=r".*restaurant.*|.*cafe.*|.*diner.*",
    category_id=2,
    rule_type="regex",
    tenant_id="tenant_123",
    user_id="user_123",
    is_regex=True,
    field_to_match="description"
)

# Create an amount-based rule
amount_rule = categorization_service.create_rule(
    name="Large Expenses",
    pattern="",
    category_id=3,
    rule_type="amount",
    tenant_id="tenant_123",
    user_id="user_123",
    amount_min=Decimal('100.00'),
    field_to_match="amount"
)

# Categorize a single transaction
success, rule_used = categorization_service.categorize_transaction(transaction, "tenant_123")

# Bulk categorize transactions
results = categorization_service.bulk_categorize_transactions([1, 2, 3], "tenant_123")
print(f"Categorized: {results['categorized']}")
print(f"Failed: {results['failed']}")

# Categorize all transactions for an account
results = categorization_service.categorize_account_transactions(
    account_id=1,
    tenant_id="tenant_123",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31)
)

# Test a rule
test_results = categorization_service.test_rule(rule.id, "tenant_123")
print(f"Matches: {test_results['matches']}")
print(f"Successes: {test_results['successes']}")

# Get rule statistics
stats = categorization_service.get_rule_stats("tenant_123")
print(f"Total rules: {stats['total_rules']}")
print(f"Most successful: {stats['most_successful_rules']}")
```

### API Reference

#### Methods

- `create_rule(name, pattern, category_id, rule_type, tenant_id, user_id=None, **kwargs)` - Create rule
- `get_rule_by_id(rule_id, tenant_id)` - Get rule by ID
- `get_rules_by_category(category_id, tenant_id, active_only=True)` - Get rules for category
- `get_active_rules(tenant_id, rule_type=None)` - Get active rules
- `categorize_transaction(transaction, tenant_id)` - Categorize single transaction
- `bulk_categorize_transactions(transaction_ids, tenant_id)` - Categorize multiple transactions
- `categorize_account_transactions(account_id, tenant_id, **filters)` - Categorize account transactions
- `test_rule(rule_id, tenant_id, test_transactions=None)` - Test rule
- `update_rule(rule_id, tenant_id, update_data, updated_by=None)` - Update rule
- `archive_rule(rule_id, tenant_id, archived_by=None)` - Archive rule
- `delete_rule(rule_id, tenant_id, deleted_by=None)` - Delete rule
- `get_rule_stats(tenant_id)` - Get rule statistics

## Best Practices

### Error Handling
All services use structured logging and proper exception handling:
- Use `structlog` for consistent logging
- Log errors with context (user_id, tenant_id, etc.)
- Raise appropriate exceptions with descriptive messages
- Use transaction rollback for database errors

### Multi-tenancy
All services respect tenant isolation:
- Always filter by `tenant_id`
- Validate tenant access before operations
- Use tenant-specific queries

### Performance
- Use database indexes effectively
- Implement pagination for large datasets
- Use bulk operations when possible
- Cache frequently accessed data

### Security
- Validate all inputs
- Use parameterized queries
- Implement proper authorization checks
- Log security-relevant operations

### Testing
- Write comprehensive unit tests
- Mock external dependencies
- Test error conditions
- Use fixtures for test data

## Context Manager Usage

All services support context manager usage for automatic resource cleanup:

```python
# Using context manager
with UserService() as user_service:
    user = user_service.get_user_by_id("user_123", "tenant_123")
    # Service automatically closes database session

# Using with existing session
with UserService(db_session=existing_session) as user_service:
    user = user_service.get_user_by_id("user_123", "tenant_123")
    # Service does not close the provided session
```

## Logging

All services use structured logging with consistent fields:

```python
# Example log entries
logger.info("User created successfully", 
           user_id=str(user.id),
           email=user_data.email[:3] + "***",
           tenant_id=tenant_id)

logger.error("Failed to create user", 
            error=str(e),
            email=user_data.email[:3] + "***",
            tenant_id=tenant_id)
```

## Common Patterns

### Service Initialization
```python
# With dependency injection
user_service = UserService(db_session=db)

# With automatic session management
user_service = UserService()
```

### Error Handling
```python
try:
    result = service.operation()
except ValueError as e:
    # Handle validation errors
    logger.error("Validation failed", error=str(e))
    raise
except Exception as e:
    # Handle unexpected errors
    logger.error("Operation failed", error=str(e))
    raise
```

### Transaction Management
```python
with service:
    try:
        result = service.operation()
        service.commit()
    except Exception:
        service.rollback()
        raise
```

This documentation provides a comprehensive guide to using TheTally services effectively. For more specific examples and advanced usage patterns, refer to the individual service test files and the source code.
