# AI Assistant Context for TheTally

This file provides essential context for AI coding assistants working on TheTally.

## 🎯 Project Overview

**TheTally** is a multi-tenant financial tracking application built with modern technologies and optimized for AI-assisted development.

## 🏗️ Technology Stack

- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React 18+ with TypeScript
- **Database**: PostgreSQL with SQLAlchemy ORM
- **UI**: Material-UI (MUI) with Emotion styling
- **Deployment**: Docker containers on Google Cloud Platform
- **AI Integration**: Google Code Assist for PR reviews

## 📁 Project Structure

```
TheTally/
├── backend/app/
│   ├── api/routers/     # API endpoints (FastAPI routers)
│   ├── services/        # Business logic layer
│   ├── models/          # Database models (SQLAlchemy)
│   ├── schemas/         # Data validation (Pydantic)
│   ├── core/           # Configuration and security
│   └── utils/          # Shared utilities
├── frontend/src/
│   ├── components/      # React components
│   ├── pages/          # Page components
│   └── services/       # API service calls
└── docs/               # Comprehensive documentation
```

## 🔒 Security Requirements

**CRITICAL**: Never commit secrets, API keys, or sensitive data to the repository.

- Use environment variables for all sensitive configuration
- All API endpoints must be protected by default
- Implement JWT authentication with refresh tokens
- Add 2FA using TOTP
- Use prepared statements (SQLAlchemy ORM) to prevent SQL injection
- Validate and sanitize all user inputs
- Multi-tenant architecture requires `tenant_id` in all database operations

## 🎨 Code Quality Standards

### Python (Backend)
- Follow PEP 8 standards
- Use complete type hints for all functions
- Implement comprehensive error handling
- Use service layer pattern for business logic
- Add docstrings for all functions and classes

### TypeScript (Frontend)
- Use functional components with React Hooks only
- Implement strict TypeScript typing
- Use Material-UI components with Emotion styling
- Follow React best practices

### General
- Use descriptive, clear naming conventions
- Implement single responsibility principle
- Add comprehensive tests (unit, integration, E2E)
- Use structured logging with three types: audit, functional, debug

## 🏢 Architecture Patterns

### Multi-Tenant Design
- Shared database with `tenant_id` isolation
- Every table must have `tenant_id` column
- All queries must filter by `tenant_id`
- User authentication maps to tenant

### Service Layer Pattern
- API routes → Services → Models → Database
- Business logic goes in `services/` directory
- API routes should be thin and delegate to services
- Services handle data validation and business rules

### Error Handling
- Use specific exception types
- Implement proper HTTP status codes
- Log errors with structured logging
- Return user-friendly error messages

## 🧪 Testing Requirements

- **Unit Tests**: Every function must have unit tests
- **Integration Tests**: Test API endpoints end-to-end
- **E2E Tests**: Use Playwright for user journey tests
- **Test Coverage**: Aim for high test coverage
- **Mock Data**: Use mock data, never real user data

## 📊 Database Design

### Core Tables
- `users` - User accounts and authentication
- `tenants` - Multi-tenant organization
- `accounts` - Financial accounts (Current Account, Savings, etc.)
- `transactions` - Individual financial transactions
- `categories` - Transaction categories
- `categorization_rules` - User-defined auto-categorization rules

### Key Relationships
- Users belong to tenants (1:1 initially)
- Accounts belong to tenants
- Transactions belong to accounts
- Transactions can have categories
- Rules apply to transactions for auto-categorization

## 🔧 Development Workflow

### Branch Protection
- All changes must go through pull requests
- Google Code Assist reviews every PR
- Tests must pass before merging
- At least 1 approval required

### AI Development Guidelines
1. **Small Functions**: Keep functions under 200 lines
2. **Clear Context**: Use descriptive names and comments
3. **Type Safety**: Complete type annotations
4. **Error Handling**: Explicit error handling patterns
5. **Documentation**: Comprehensive docstrings

## 📝 Key Files to Reference

- `ai-rules.md` - Detailed AI development guidelines
- `SECURITY.md` - Security best practices
- `docs/architecture.md` - System architecture details
- `docs/api-specification.md` - API endpoint documentation
- `config.yaml` - Google Code Assist configuration
- `.env.example` - Environment variable template

## 🚨 Common Pitfalls to Avoid

1. **Never hardcode secrets** - Use environment variables
2. **Don't skip tenant_id** - Required for multi-tenant queries
3. **Avoid raw SQL** - Use SQLAlchemy ORM
4. **Don't forget error handling** - Implement comprehensive error handling
5. **Don't skip tests** - Every feature needs tests
6. **Don't commit .env files** - Use .env.example template

## 🎯 Current Development Focus

### Phase 0: Foundation & DevOps
- [x] Project setup and architecture
- [x] Security configuration
- [ ] User authentication implementation
- [ ] Database setup and models

### Phase 1: Core Functionality (MVP)
- [ ] Financial data import (CSV, OFX, QIF)
- [ ] Transaction categorization engine
- [ ] Basic UI components
- [ ] User management

## 🤖 AI Assistant Tips

- Always check the `ai-rules.md` file for detailed guidelines
- Use the service layer pattern for business logic
- Implement proper error handling and logging
- Add comprehensive type hints and docstrings
- Follow the multi-tenant architecture patterns
- Ensure all security requirements are met
- Write tests for all new functionality

---

**Remember**: This is a production-ready, security-focused application. Always prioritize security, maintainability, and code quality.
