# Database Schema

## Overview

TheTally uses PostgreSQL as the primary database with a multi-tenant architecture. All tables include a `tenant_id` column to ensure data isolation between users. The database is self-managed on Google Cloud Compute Engine for maximum portability and cost-effectiveness.

## PostgreSQL Extensions

### Core Extensions
```sql
-- Enable essential extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
```

### Future Extensions for Advanced Features
```sql
-- Vector database capabilities (for ML features)
CREATE EXTENSION IF NOT EXISTS "vector";

-- Time-series data (for analytics)
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Full-text search enhancements
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
```

## Schema Design Principles

- **Multi-tenancy**: Shared database with tenant isolation via `tenant_id`
- **UUID Primary Keys**: All tables use UUID primary keys for security
- **Audit Trail**: Created/updated timestamps on all tables
- **Soft Deletes**: Use `is_active` flags instead of hard deletes where appropriate
- **Normalization**: Properly normalized to avoid data duplication

## Core Tables

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_otp_enabled BOOLEAN DEFAULT false,
    otp_secret VARCHAR(32),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Tenants Table
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Accounts Table
```sql
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- 'current', 'savings', 'credit_card', etc.
    balance DECIMAL(15,2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'GBP',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Categories Table
```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    color VARCHAR(7), -- Hex color code
    icon VARCHAR(50),
    parent_id UUID REFERENCES categories(id), -- For subcategories
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id),
    amount DECIMAL(15,2) NOT NULL,
    description TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    reference VARCHAR(255),
    metadata JSONB, -- For additional transaction data
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Categorization Rules Table
```sql
CREATE TABLE categorization_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    pattern VARCHAR(255) NOT NULL,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 0, -- Higher number = higher priority
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Refresh Tokens Table
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### API Keys Table
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    permissions TEXT[] NOT NULL, -- Array of permission strings
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Indexes

### Performance Indexes
```sql
-- Multi-tenant queries
CREATE INDEX idx_transactions_tenant_id ON transactions(tenant_id);
CREATE INDEX idx_accounts_tenant_id ON accounts(tenant_id);
CREATE INDEX idx_categories_tenant_id ON categories(tenant_id);
CREATE INDEX idx_categorization_rules_tenant_id ON categorization_rules(tenant_id);

-- Transaction queries
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_tenant_date ON transactions(tenant_id, transaction_date);

-- User authentication
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active) WHERE is_active = true;

-- Categorization rules
CREATE INDEX idx_categorization_rules_pattern ON categorization_rules(pattern);
CREATE INDEX idx_categorization_rules_priority ON categorization_rules(priority DESC);
```

## Constraints

### Unique Constraints
```sql
-- Ensure unique email per user
ALTER TABLE users ADD CONSTRAINT uk_users_email UNIQUE (email);

-- Ensure unique tenant per user (1:1 relationship)
ALTER TABLE tenants ADD CONSTRAINT uk_tenants_user_id UNIQUE (user_id);

-- Ensure unique account names per tenant
ALTER TABLE accounts ADD CONSTRAINT uk_accounts_tenant_name UNIQUE (tenant_id, name);

-- Ensure unique category names per tenant
ALTER TABLE categories ADD CONSTRAINT uk_categories_tenant_name UNIQUE (tenant_id, name);

-- Ensure unique API key names per user
ALTER TABLE api_keys ADD CONSTRAINT uk_api_keys_user_name UNIQUE (user_id, name);
```

### Check Constraints
```sql
-- Valid email format
ALTER TABLE users ADD CONSTRAINT ck_users_email_format 
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Valid currency codes
ALTER TABLE accounts ADD CONSTRAINT ck_accounts_currency 
    CHECK (currency IN ('GBP', 'USD', 'EUR', 'CAD', 'AUD'));

-- Valid account types
ALTER TABLE accounts ADD CONSTRAINT ck_accounts_type 
    CHECK (account_type IN ('current', 'savings', 'credit_card', 'investment', 'loan', 'mortgage'));

-- Valid hex color codes
ALTER TABLE categories ADD CONSTRAINT ck_categories_color 
    CHECK (color IS NULL OR color ~* '^#[0-9A-Fa-f]{6}$');
```

## Sample Data

### Default Categories
```sql
-- Insert default categories for new tenants
INSERT INTO categories (tenant_id, name, color, icon) VALUES
    (tenant_id, 'Groceries', '#FF5722', 'shopping_cart'),
    (tenant_id, 'Transport', '#2196F3', 'directions_car'),
    (tenant_id, 'Entertainment', '#9C27B0', 'movie'),
    (tenant_id, 'Utilities', '#FF9800', 'home'),
    (tenant_id, 'Healthcare', '#4CAF50', 'local_hospital'),
    (tenant_id, 'Income', '#4CAF50', 'trending_up'),
    (tenant_id, 'Transfer', '#607D8B', 'swap_horiz');
```

## Migration Strategy

1. **Initial Migration**: Create all tables with proper constraints
2. **Data Migration**: Import existing data if migrating from another system
3. **Index Optimization**: Add indexes based on query patterns
4. **Performance Tuning**: Monitor and optimize based on usage

## Future Considerations

- **Partitioning**: Consider partitioning transactions table by date for large datasets
- **Archiving**: Implement data archiving strategy for old transactions
- **Backup Strategy**: Regular backups to Cloud Storage with point-in-time recovery
- **Monitoring**: Database performance monitoring and alerting
- **Vector Search**: Use pgvector extension for ML-based categorization
- **Time-Series Analytics**: Use TimescaleDB extension for financial analytics
- **Full-Text Search**: Leverage PostgreSQL's built-in full-text search capabilities
- **Connection Pooling**: Implement PgBouncer for connection management

---

*This schema will be refined as we develop the application and understand the data patterns better.*
