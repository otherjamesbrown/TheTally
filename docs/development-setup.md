# Development Setup

## Prerequisites

### Required Software
- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18+**: [Download Node.js](https://nodejs.org/)
- **Docker & Docker Compose**: [Download Docker](https://www.docker.com/get-started)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **PostgreSQL 15+**: [Download PostgreSQL](https://www.postgresql.org/download/)

### Recommended Tools
- **VS Code**: [Download VS Code](https://code.visualstudio.com/)
- **Postman**: [Download Postman](https://www.postman.com/downloads/)
- **DBeaver**: [Download DBeaver](https://dbeaver.io/download/)

## Project Structure

```
TheTally/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routers
│   │   ├── core/           # Configuration and security
│   │   ├── db/             # Database models and session
│   │   ├── schemas/        # Pydantic models
│   │   └── services/       # Business logic
│   ├── tests/              # Test files
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   ├── package.json        # Node dependencies
│   └── Dockerfile
├── docs/                   # Documentation
├── docker-compose.yml      # Local development
└── README.md
```

## Backend Setup

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create `.env` file in the backend directory:
```bash
# Database
DATABASE_URL=postgresql://thetally:password@localhost:5432/thetally_dev
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=thetally_dev
DATABASE_USER=thetally
DATABASE_PASSWORD=password

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 2FA
OTP_ISSUER=TheTally
OTP_SECRET_LENGTH=32

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=csv,ofx,qif

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_CREDENTIALS=true

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=json
```

### 4. Database Setup
```bash
# Create database
createdb thetally_dev

# Run migrations
alembic upgrade head

# Create initial data (optional)
python scripts/create_initial_data.py
```

### 5. Start Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Environment Configuration
Create `.env.local` file in the frontend directory:
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_STAGING_URL=http://localhost:8000

# Authentication
REACT_APP_JWT_STORAGE_KEY=thetally_token
REACT_APP_REFRESH_TOKEN_KEY=thetally_refresh_token

# Feature Flags
REACT_APP_ENABLE_2FA=true
REACT_APP_ENABLE_FILE_UPLOAD=true
REACT_APP_ENABLE_ANALYTICS=false

# Environment
REACT_APP_ENVIRONMENT=development
REACT_APP_VERSION=1.0.0
```

### 3. Start Frontend Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Docker Development

### 1. Start All Services
```bash
# From project root
docker-compose up -d
```

### 2. View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. Stop Services
```bash
docker-compose down
```

## Database Management

### 1. Access Database
```bash
# Using psql
psql -h localhost -U thetally -d thetally_dev

# Using Docker
docker-compose exec db psql -U thetally -d thetally_dev
```

### 2. Run Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### 3. Reset Database
```bash
# Drop and recreate database
docker-compose exec db psql -U thetally -c "DROP DATABASE IF EXISTS thetally_dev;"
docker-compose exec db psql -U thetally -c "CREATE DATABASE thetally_dev;"
alembic upgrade head
```

## Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Frontend Tests
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- --testPathPattern=LoginForm.test.tsx

# Run in watch mode
npm test -- --watch
```

### E2E Tests
```bash
# Install Playwright
npx playwright install

# Run E2E tests
npx playwright test

# Run specific test
npx playwright test tests/login.spec.ts

# Run with UI
npx playwright test --ui
```

## Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# ... code changes ...

# Run tests
npm test
pytest

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push branch
git push origin feature/new-feature
```

### 2. Code Quality
```bash
# Backend linting
cd backend
black .  # Code formatting
isort .  # Import sorting
flake8 . # Linting

# Frontend linting
cd frontend
npm run lint        # ESLint
npm run format      # Prettier
npm run type-check  # TypeScript checking
```

### 3. Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Dependency Management

### Version Stability Guidelines

**CRITICAL**: Always use stable, production-ready versions of dependencies to avoid rendering issues.

#### React Ecosystem Stability
- **React**: Use LTS versions (currently 18.x) - avoid pre-release versions
- **Material-UI**: Use stable v5.x - avoid v6+ until fully released
- **React Router**: Use stable v6.x - avoid pre-release versions
- **ESLint**: Use stable v8.x - avoid v9+ until ecosystem catches up

#### Dependency Update Process
1. **Check Release Status**: Verify all dependencies are stable releases
2. **Test Incrementally**: Update one major dependency at a time
3. **Run Full Test Suite**: Ensure all E2E tests pass after updates
4. **Verify Rendering**: Confirm UI renders correctly in all browsers

#### Prohibited Practices
- ❌ **Never use pre-release versions** in production or development
- ❌ **Never update multiple major versions** simultaneously
- ❌ **Never skip testing** after dependency updates
- ❌ **Never ignore peer dependency warnings**

#### Safe Update Commands
```bash
# Check for outdated packages
npm outdated

# Update to latest stable versions only
npm update

# Check for security vulnerabilities
npm audit

# Fix vulnerabilities (avoid breaking changes)
npm audit fix
```

#### Version Lock Strategy
```json
{
  "dependencies": {
    "react": "^18.2.0",           // Lock to stable LTS
    "react-dom": "^18.2.0",       // Match React version
    "@mui/material": "^5.15.20",  // Stable Material-UI v5
    "react-router-dom": "^6.28.0" // Stable React Router v6
  },
  "devDependencies": {
    "eslint": "^8.57.0"           // Stable ESLint v8
  }
}
```

## Troubleshooting

### Common Issues

#### Backend Issues
```bash
# Port already in use
lsof -ti:8000 | xargs kill -9

# Database connection error
# Check if PostgreSQL is running
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux

# Import errors
# Make sure virtual environment is activated
source venv/bin/activate
```

#### Frontend Issues
```bash
# Port already in use
lsof -ti:3000 | xargs kill -9

# Node modules issues
rm -rf node_modules package-lock.json
npm install

# Build issues
npm run build
```

#### Frontend Rendering Issues
```bash
# Blank white screen - check for JavaScript errors
# 1. Open browser DevTools (F12)
# 2. Check Console tab for errors
# 3. Check Network tab for failed requests

# Common causes and fixes:
# - React version incompatibility
npm install react@^18.2.0 react-dom@^18.2.0

# - Material-UI version issues
npm install @mui/material@^5.15.20 @mui/icons-material@^5.15.20

# - ESLint configuration issues
npm install eslint@^8.57.0

# - Clear browser cache completely
# Chrome: Ctrl+Shift+Delete, select "All time"
# Or use incognito mode

# - Check for peer dependency conflicts
npm ls --depth=0

# - Verify all imports are correct
# Check for missing imports in console errors
```

#### Dependency Conflict Resolution
```bash
# Check for version conflicts
npm ls

# Force resolution of peer dependencies
npm install --legacy-peer-deps

# Or use exact versions to avoid conflicts
npm install --save-exact react@18.2.0

# Clean install after fixing conflicts
rm -rf node_modules package-lock.json
npm install
```

#### Docker Issues
```bash
# Clean up Docker
docker-compose down -v
docker system prune -a

# Rebuild containers
docker-compose up --build
```

### Debugging

#### Backend Debugging
```bash
# Run with debug logging
LOG_LEVEL=DEBUG uvicorn app.main:app --reload

# Use debugger
python -m pdb -m uvicorn app.main:app --reload
```

#### Frontend Debugging
```bash
# Run with debug logging
REACT_APP_LOG_LEVEL=debug npm start

# Use React DevTools
# Install browser extension
```

## IDE Configuration

### VS Code Extensions
- **Python**: Python extension pack
- **React**: ES7+ React/Redux/React-Native snippets
- **Docker**: Docker extension
- **Git**: GitLens
- **Database**: PostgreSQL extension

### VS Code Settings
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## Getting Help

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://reactjs.org/docs
- **Material-UI**: https://mui.com/
- **PostgreSQL**: https://www.postgresql.org/docs/

### Community
- **GitHub Issues**: Report bugs and feature requests
- **Discord**: Join our development community
- **Stack Overflow**: Tag questions with `thetally`

---

*This setup guide will be updated as the development environment evolves.*
