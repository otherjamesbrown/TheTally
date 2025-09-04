# Manual Issue Creation Guide

Since GitHub CLI is not installed, here are the exact issue contents to create manually in GitHub.

## How to Create Issues

1. Go to: https://github.com/otherjamesbrown/TheTally/issues
2. Click "New issue"
3. Choose "Task" template (or create custom)
4. Copy and paste the content below
5. Add the "project-setup" label
6. Assign to appropriate milestone

## Phase 0: Foundation & DevOps Issues

### Issue 1: Create service layer architecture

**Title:** `[Phase 0] Create service layer architecture`

**Labels:** `project-setup`, `backend`, `architecture`, `priority:high`, `effort:medium`

**Milestone:** `Phase 0: Foundation & DevOps`

**Body:**
```markdown
## Description
Implement services/, models/, and utils/ directories with proper structure for AI-friendly development.

## What Needs to Be Done
- Create services/ directory with proper __init__.py and documentation
- Create models/ directory with proper __init__.py and documentation  
- Create utils/ directory with proper __init__.py and documentation
- Add comprehensive docstrings to each module explaining their purpose
- Update project documentation to reflect the new structure
- Ensure all modules follow Python packaging best practices

## Acceptance Criteria
- [ ] **Directory Structure**: All three directories (services/, models/, utils/) exist in backend/app/
- [ ] **Package Files**: Each directory has proper __init__.py files with docstrings
- [ ] **Documentation**: Each __init__.py file contains module purpose and usage examples
- [ ] **Import Tests**: All modules can be imported without errors
- [ ] **Linting**: All files pass flake8 and mypy checks
- [ ] **Documentation**: README.md updated to reflect new structure
- [ ] **AI Context**: AI-CONTEXT.md updated with new architecture

## Test Commands
```bash
# Test directory structure
ls -la backend/app/services/ backend/app/models/ backend/app/utils/

# Test imports
python -c "from backend.app.services import *; from backend.app.models import *; from backend.app.utils import *"

# Test linting
flake8 backend/app/services/ backend/app/models/ backend/app/utils/
mypy backend/app/services/ backend/app/models/ backend/app/utils/
```

## Priority
High - Foundation for all future development

## Effort
Medium (half day)
```

---

### Issue 2: Implement user registration and login API

**Title:** `[Phase 0] Implement user registration and login API with JWTs and 2FA`

**Labels:** `project-setup`, `backend`, `security`, `priority:critical`, `effort:large`

**Milestone:** `Phase 0: Foundation & DevOps`

**Body:**
```markdown
## Description
Implement secure user authentication system with JWT tokens and 2FA support.

## What Needs to Be Done
- Create user registration endpoint with validation
- Create user login endpoint with JWT token generation
- Implement JWT refresh token mechanism
- Add 2FA setup and verification endpoints
- Implement password hashing with bcrypt
- Add input validation and sanitization
- Create comprehensive unit tests
- Add API documentation

## Acceptance Criteria
- [ ] **Registration Endpoint**: POST /api/v1/auth/register creates new users
- [ ] **Login Endpoint**: POST /api/v1/auth/login returns JWT tokens
- [ ] **JWT Tokens**: Access tokens (30min) and refresh tokens (7 days)
- [ ] **2FA Setup**: POST /api/v1/auth/2fa/setup generates TOTP secret
- [ ] **2FA Verify**: POST /api/v1/auth/2fa/verify validates TOTP codes
- [ ] **Password Security**: Passwords hashed with bcrypt (12 rounds)
- [ ] **Input Validation**: All inputs validated with Pydantic schemas
- [ ] **Error Handling**: Proper HTTP status codes and error messages
- [ ] **Unit Tests**: 100% test coverage for auth endpoints
- [ ] **API Docs**: Endpoints documented in FastAPI auto-docs

## Test Commands
```bash
# Test registration
curl -X POST http://localhost:8000/api/v1/auth/register -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"testpass123"}'

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"testpass123"}'

# Test 2FA setup
curl -X POST http://localhost:8000/api/v1/auth/2fa/setup -H "Authorization: Bearer <token>"

# Run tests
pytest backend/tests/test_auth.py -v
```

## Priority
Critical - Core security requirement

## Effort
Large (1-2 days)
```

---

### Issue 3: Set up PostgreSQL database on GCP

**Title:** `[Phase 0] Set up PostgreSQL database on GCP`

**Labels:** `project-setup`, `devops`, `database`, `priority:high`, `effort:medium`

**Milestone:** `Phase 0: Foundation & DevOps`

**Body:**
```markdown
## Description
Set up PostgreSQL database on Google Cloud Platform with proper configuration and security.

## What Needs to Be Done
- Create GCP PostgreSQL instance (Cloud SQL)
- Configure database connection with SSL
- Set up Alembic migrations
- Create initial database schema
- Configure connection pooling
- Set up database backups
- Document connection setup
- Add environment configuration

## Acceptance Criteria
- [ ] **GCP Instance**: PostgreSQL 15+ instance running on GCP
- [ ] **SSL Connection**: Database requires SSL connections
- [ ] **Alembic Setup**: Migration system configured and working
- [ ] **Initial Schema**: Basic tables created (users, tenants, etc.)
- [ ] **Connection Pool**: SQLAlchemy connection pooling configured
- [ ] **Backups**: Automated daily backups enabled
- [ ] **Environment Config**: Database URL in environment variables
- [ ] **Documentation**: Setup guide in docs/database-setup.md
- [ ] **Health Check**: Database health endpoint working
- [ ] **Security**: Database access restricted to application

## Test Commands
```bash
# Test database connection
python -c "from backend.app.db.session import engine; print(engine.execute('SELECT 1').scalar())"

# Test migrations
alembic current
alembic upgrade head

# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test SSL connection
psql "$DATABASE_URL" -c "SELECT version();"
```

## Priority
High - Required for data persistence

## Effort
Medium (half day)
```

---

### Issue 4: Dockerize applications

**Title:** `[Phase 0] Dockerize frontend and backend applications`

**Labels:** `project-setup`, `devops`, `docker`, `priority:medium`, `effort:medium`

**Milestone:** `Phase 0: Foundation & DevOps`

**Body:**
```markdown
## Description
Create Docker containers for both frontend and backend applications with optimized builds.

## What Needs to Be Done
- Create optimized backend Dockerfile
- Create optimized frontend Dockerfile
- Create docker-compose.yml for development
- Create docker-compose.yml for production
- Set up multi-stage builds
- Configure health checks
- Add proper networking
- Document Docker usage

## Acceptance Criteria
- [ ] **Backend Dockerfile**: Python 3.11+ with FastAPI, optimized for size
- [ ] **Frontend Dockerfile**: Node.js 18+ with React, optimized build
- [ ] **Development Compose**: docker-compose.dev.yml for local development
- [ ] **Production Compose**: docker-compose.yml for production
- [ ] **Multi-stage Builds**: Separate build and runtime stages
- [ ] **Health Checks**: Container health checks configured
- [ ] **Networking**: Proper container networking setup
- [ ] **Environment Variables**: All config via environment variables
- [ ] **Documentation**: Docker setup guide created
- [ ] **Size Optimization**: Images under 500MB each

## Test Commands
```bash
# Build images
docker build -t thetally-backend ./backend
docker build -t thetally-frontend ./frontend

# Test development setup
docker-compose -f docker-compose.dev.yml up -d

# Test production setup
docker-compose up -d

# Test health checks
docker ps
curl http://localhost:8000/health
curl http://localhost:3000

# Check image sizes
docker images | grep thetally
```

## Priority
Medium - Required for deployment

## Effort
Medium (half day)
```

---

### Issue 5: Create GitHub Actions CI/CD pipeline

**Title:** `[Phase 0] Create GitHub Actions CI/CD pipeline`

**Labels:** `project-setup`, `devops`, `ci-cd`, `priority:high`, `effort:large`

**Milestone:** `Phase 0: Foundation & DevOps`

**Body:**
```markdown
## Description
Set up automated CI/CD pipeline with GitHub Actions for testing, building, and deployment.

## What Needs to Be Done
- Create workflow for running tests on PRs
- Set up Docker image building
- Configure deployment to GCP staging
- Set up production deployment with manual approval
- Add security scanning
- Configure code quality checks
- Set up notifications
- Document CI/CD process

## Acceptance Criteria
- [ ] **Test Workflow**: Tests run on every PR and push
- [ ] **Docker Build**: Images built and pushed to registry
- [ ] **Staging Deploy**: Automatic deployment to staging on main branch
- [ ] **Production Deploy**: Manual approval required for production
- [ ] **Security Scan**: Vulnerability scanning on every build
- [ ] **Code Quality**: Linting and type checking
- [ ] **Notifications**: Slack/email notifications for failures
- [ ] **Documentation**: CI/CD guide in docs/
- [ ] **Secrets**: All secrets properly configured
- [ ] **Rollback**: Ability to rollback deployments

## Test Commands
```bash
# Test workflow locally
act push

# Check workflow status
gh run list

# Test deployment
gh workflow run deploy-staging

# Check secrets
gh secret list
```

## Priority
High - Required for automated deployment

## Effort
Large (1-2 days)
```

---

### Issue 6: Implement E2E tests for login flow

**Title:** `[Phase 0] Implement E2E tests for login flow`

**Labels:** `project-setup`, `testing`, `e2e`, `priority:medium`, `effort:medium`

**Milestone:** `Phase 0: Foundation & DevOps`

**Body:**
```markdown
## Description
Create end-to-end tests for the user authentication flow using Playwright.

## What Needs to Be Done
- Set up Playwright testing framework
- Create E2E tests for user registration
- Create E2E tests for user login
- Create E2E tests for 2FA setup
- Create E2E tests for 2FA verification
- Set up test data and fixtures
- Configure CI/CD integration
- Document testing process

## Acceptance Criteria
- [ ] **Playwright Setup**: Playwright configured and working
- [ ] **Registration Test**: E2E test for user registration flow
- [ ] **Login Test**: E2E test for user login flow
- [ ] **2FA Setup Test**: E2E test for 2FA setup process
- [ ] **2FA Verify Test**: E2E test for 2FA verification
- [ ] **Test Data**: Proper test fixtures and cleanup
- [ ] **CI Integration**: Tests run in GitHub Actions
- [ ] **Documentation**: E2E testing guide created
- [ ] **Coverage**: All auth flows covered by E2E tests
- [ ] **Reliability**: Tests are stable and reliable

## Test Commands
```bash
# Install Playwright
npm install -D @playwright/test
npx playwright install

# Run E2E tests
npx playwright test

# Run specific test
npx playwright test tests/auth.spec.ts

# Run in headed mode
npx playwright test --headed

# Generate test report
npx playwright show-report
```

## Priority
Medium - Quality assurance

## Effort
Medium (half day)
```

## Phase 1: Core Functionality Issues

### Issue 7: Create database models for accounts and transactions

**Title:** `[Phase 1] Create database models for accounts and transactions`

**Labels:** `project-setup`, `backend`, `database`, `priority:critical`, `effort:large`

**Milestone:** `Phase 1: Core Functionality (MVP)`

**Body:**
```markdown
## Description
Design and implement SQLAlchemy models for financial accounts and transactions with multi-tenant support.

## What Needs to Be Done
- Create User model with multi-tenant support
- Create Account model (Current Account, Savings, etc.)
- Create Transaction model with proper relationships
- Create Category model for transaction categorization
- Create CategorizationRule model
- Add proper indexes and constraints
- Create Alembic migration scripts
- Add model validation and methods

## Acceptance Criteria
- [ ] **User Model**: User model with tenant_id and proper relationships
- [ ] **Account Model**: Account model with type, balance, and tenant isolation
- [ ] **Transaction Model**: Transaction model with amount, date, description
- [ ] **Category Model**: Category model for transaction categorization
- [ ] **Rule Model**: CategorizationRule model for auto-categorization
- [ ] **Relationships**: Proper foreign key relationships between models
- [ ] **Indexes**: Performance indexes on frequently queried fields
- [ ] **Constraints**: Database constraints for data integrity
- [ ] **Migrations**: Alembic migrations for all models
- [ ] **Tests**: Unit tests for all model methods

## Test Commands
```bash
# Test model creation
python -c "from backend.app.models import User, Account, Transaction; print('Models imported successfully')"

# Test database operations
python -c "from backend.app.db.session import SessionLocal; from backend.app.models import User; db = SessionLocal(); user = User(email='test@example.com', tenant_id='test'); db.add(user); db.commit(); print('User created successfully')"

# Test migrations
alembic upgrade head
alembic downgrade -1
alembic upgrade head

# Run model tests
pytest backend/tests/test_models.py -v
```

## Priority
Critical - Core data models

## Effort
Large (1-2 days)
```

---

### Issue 8: Implement core service layer

**Title:** `[Phase 1] Implement core service layer`

**Labels:** `project-setup`, `backend`, `services`, `priority:high`, `effort:large`

**Milestone:** `Phase 1: Core Functionality (MVP)`

**Body:**
```markdown
## Description
Create business logic services for user management, transaction processing, and categorization.

## What Needs to Be Done
- Create UserService for user management
- Create AccountService for account operations
- Create TransactionService for transaction processing
- Create CategoryService for categorization
- Create CategorizationService for auto-categorization
- Add proper error handling and logging
- Create service interfaces and contracts
- Add comprehensive unit tests

## Acceptance Criteria
- [ ] **UserService**: Complete user management operations
- [ ] **AccountService**: Account CRUD operations with tenant isolation
- [ ] **TransactionService**: Transaction processing and queries
- [ ] **CategoryService**: Category management operations
- [ ] **CategorizationService**: Auto-categorization logic
- [ ] **Error Handling**: Proper exception handling and logging
- [ ] **Type Hints**: Complete type annotations for all methods
- [ ] **Documentation**: Comprehensive docstrings for all services
- [ ] **Tests**: Unit tests for all service methods
- [ ] **Logging**: Structured logging for all operations

## Test Commands
```bash
# Test service imports
python -c "from backend.app.services import UserService, AccountService, TransactionService; print('Services imported successfully')"

# Test service operations
python -c "from backend.app.services import UserService; service = UserService(); print('Service instantiated successfully')"

# Run service tests
pytest backend/tests/test_services.py -v

# Test service integration
pytest backend/tests/test_service_integration.py -v
```

## Priority
High - Core business logic

## Effort
Large (1-2 days)
```

---

### Issue 9: Build file import component

**Title:** `[Phase 1] Build file import component for CSV, OFX, and QIF files`

**Labels:** `project-setup`, `frontend`, `backend`, `priority:high`, `effort:large`

**Milestone:** `Phase 1: Core Functionality (MVP)`

**Body:**
```markdown
## Description
Create frontend component and backend logic to import financial data from various file formats.

## What Needs to Be Done
- Create file upload component in React
- Implement CSV parser in backend
- Implement OFX parser in backend
- Implement QIF parser in backend
- Add file validation and error handling
- Create progress indicators
- Add batch processing support
- Create comprehensive tests

## Acceptance Criteria
- [ ] **Upload Component**: React component for file upload
- [ ] **CSV Parser**: Backend parser for CSV files
- [ ] **OFX Parser**: Backend parser for OFX files
- [ ] **QIF Parser**: Backend parser for QIF files
- [ ] **File Validation**: Proper file type and size validation
- [ ] **Error Handling**: User-friendly error messages
- [ ] **Progress UI**: Upload progress indicators
- [ ] **Batch Processing**: Support for multiple files
- [ ] **Tests**: Unit and integration tests
- [ ] **Documentation**: Usage guide for file formats

## Test Commands
```bash
# Test file upload
curl -X POST http://localhost:8000/api/v1/import/csv -F "file=@test.csv"

# Test CSV parsing
python -c "from backend.app.services import ImportService; service = ImportService(); result = service.parse_csv('test.csv'); print(f'Parsed {len(result)} transactions')"

# Test frontend component
npm test -- --testPathPattern=FileUpload

# Test file validation
python -c "from backend.app.utils import validate_file; print(validate_file('test.csv', 'csv'))"
```

## Priority
High - Core functionality

## Effort
Large (1-2 days)
```

---

### Issue 10: Develop categorization engine

**Title:** `[Phase 1] Develop rules-based categorization engine`

**Labels:** `project-setup`, `backend`, `frontend`, `priority:high`, `effort:large`

**Milestone:** `Phase 1: Core Functionality (MVP)`

**Body:**
```markdown
## Description
Create an intelligent system to automatically categorize transactions based on user-defined rules.

## What Needs to Be Done
- Create rule definition system
- Implement pattern matching engine
- Add rule priority system
- Create rule testing interface
- Add performance optimization
- Implement rule management API
- Create frontend rule management UI
- Add comprehensive testing

## Acceptance Criteria
- [ ] **Rule Engine**: Pattern matching and categorization logic
- [ ] **Rule Management**: CRUD operations for categorization rules
- [ ] **Priority System**: Rule priority and conflict resolution
- [ ] **Pattern Matching**: Regex and keyword matching
- [ ] **Rule Testing**: Test rules against sample transactions
- [ ] **Performance**: Efficient rule processing
- [ ] **API Endpoints**: REST API for rule management
- [ ] **Frontend UI**: React component for rule management
- [ ] **Tests**: Unit and integration tests
- [ ] **Documentation**: Rule creation guide

## Test Commands
```bash
# Test rule creation
curl -X POST http://localhost:8000/api/v1/rules -H "Content-Type: application/json" -d '{"pattern":"Tesco","category":"Groceries","priority":1}'

# Test categorization
python -c "from backend.app.services import CategorizationService; service = CategorizationService(); result = service.categorize_transaction('Tesco Express', []); print(f'Category: {result}')"

# Test rule performance
python -c "from backend.app.services import CategorizationService; import time; service = CategorizationService(); start = time.time(); service.categorize_batch([{'description': 'Tesco'} for _ in range(1000)]); print(f'Processed 1000 transactions in {time.time() - start:.2f}s')"

# Run categorization tests
pytest backend/tests/test_categorization.py -v
```

## Priority
High - Core functionality

## Effort
Large (1-2 days)
```

---

### Issue 11: Create transaction table view

**Title:** `[Phase 1] Build simple transaction table view in the UI`

**Labels:** `project-setup`, `frontend`, `ui`, `priority:medium`, `effort:medium`

**Milestone:** `Phase 1: Core Functionality (MVP)`

**Body:**
```markdown
## Description
Create a React component to display transactions in a table format with filtering and sorting.

## What Needs to Be Done
- Create TransactionTable React component
- Implement data fetching from API
- Add filtering and sorting functionality
- Create pagination controls
- Add search functionality
- Implement responsive design
- Add loading and error states
- Create comprehensive tests

## Acceptance Criteria
- [ ] **Table Component**: React component displaying transactions
- [ ] **Data Fetching**: API integration for transaction data
- [ ] **Filtering**: Filter by date, category, amount
- [ ] **Sorting**: Sort by any column
- [ ] **Pagination**: Page through large datasets
- [ ] **Search**: Search transaction descriptions
- [ ] **Responsive**: Mobile-friendly design
- [ ] **Loading States**: Loading and error indicators
- [ ] **Tests**: Component and integration tests
- [ ] **Performance**: Efficient rendering of large datasets

## Test Commands
```bash
# Test API endpoint
curl http://localhost:8000/api/v1/transactions

# Test filtering
curl "http://localhost:8000/api/v1/transactions?category=Groceries&start_date=2024-01-01"

# Test frontend component
npm test -- --testPathPattern=TransactionTable

# Test responsive design
npm run test:e2e -- --grep "Transaction table"

# Test performance
npm run test:performance -- --component=TransactionTable
```

## Priority
Medium - User interface

## Effort
Medium (half day)
```

## Quick Creation Steps

1. **Go to Issues**: https://github.com/otherjamesbrown/TheTally/issues
2. **Click "New issue"**
3. **Copy each issue above** (title, labels, milestone, body)
4. **Create all 11 issues**
5. **Add "project-setup" label** to each
6. **Assign to appropriate milestone**

## After Creating Issues

1. **Set up Project Board**: Go to Projects tab and create boards
2. **Add Issues to Board**: Move issues to appropriate columns
3. **Start Working**: Begin with Phase 0 issues
4. **Track Progress**: Move issues through board columns as you work
