#!/bin/bash

# Create Initial Issues for TheTally
# This script creates initial issues based on the project roadmap

set -e

echo "🚀 Creating initial issues for TheTally..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository. Please run this from the project root."
    exit 1
fi

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"

# Get repository information
REPO_OWNER=$(gh repo view --json owner -q .owner.login)
REPO_NAME=$(gh repo view --json name -q .name)

echo "📋 Repository: $REPO_OWNER/$REPO_NAME"

# Create milestones
echo "📅 Creating milestones..."

gh api repos/$REPO_OWNER/$REPO_NAME/milestones -X POST -f title="Phase 0: Foundation & DevOps" -f description="Set up project foundation, CI/CD, and basic infrastructure" -f state="open" || echo "Milestone may already exist"

gh api repos/$REPO_OWNER/$REPO_NAME/milestones -X POST -f title="Phase 1: Core Functionality (MVP)" -f description="Implement core financial tracking features" -f state="open" || echo "Milestone may already exist"

gh api repos/$REPO_OWNER/$REPO_NAME/milestones -X POST -f title="Phase 2: Financial Modelling & Visualization" -f description="Add financial modeling and data visualization features" -f state="open" || echo "Milestone may already exist"

gh api repos/$REPO_OWNER/$REPO_NAME/milestones -X POST -f title="Phase 3: Future Enhancements" -f description="Advanced features and integrations" -f state="open" || echo "Milestone may already exist"

echo "✅ Milestones created"

# Create Phase 0 issues
echo "📝 Creating Phase 0 issues..."

# Issue 1: Set up service layer architecture
gh issue create \
  --title "[Task] Create service layer architecture" \
  --body "## Description
Implement services/, models/, and utils/ directories with proper structure for AI-friendly development.

## Acceptance Criteria
- [ ] Create services/ directory with proper __init__.py
- [ ] Create models/ directory with proper __init__.py  
- [ ] Create utils/ directory with proper __init__.py
- [ ] Add comprehensive docstrings to each module
- [ ] Update project documentation

## Technical Details
- Follow the modular architecture patterns
- Ensure proper separation of concerns
- Add type hints and documentation
- Make it AI-assistant friendly

## Priority
High - Foundation for all future development

## Effort
Medium (half day)" \
  --label "task,backend,architecture,priority:high,effort:medium" \
  --milestone "Phase 0: Foundation & DevOps" || echo "Issue may already exist"

# Issue 2: Implement user authentication
gh issue create \
  --title "[Feature] Implement user authentication with JWT and 2FA" \
  --body "## Description
Implement secure user authentication system with JWT tokens and 2FA support.

## Acceptance Criteria
- [ ] User registration endpoint
- [ ] User login endpoint with JWT
- [ ] JWT refresh token mechanism
- [ ] 2FA setup and verification
- [ ] Password hashing with bcrypt
- [ ] Input validation and sanitization
- [ ] Unit tests for all endpoints

## Technical Details
- Use FastAPI with SQLAlchemy
- Implement JWT with proper expiration
- Use TOTP for 2FA
- Follow security best practices
- Multi-tenant support with tenant_id

## Priority
Critical - Core security requirement

## Effort
Large (1-2 days)" \
  --label "enhancement,backend,security,priority:critical,effort:large" \
  --milestone "Phase 0: Foundation & DevOps" || echo "Issue may already exist"

# Issue 3: Set up PostgreSQL database
gh issue create \
  --title "[Task] Set up PostgreSQL database on GCP" \
  --body "## Description
Set up PostgreSQL database on Google Cloud Platform with proper configuration.

## Acceptance Criteria
- [ ] Create GCP PostgreSQL instance
- [ ] Configure database connection
- [ ] Set up Alembic migrations
- [ ] Create initial database schema
- [ ] Configure connection pooling
- [ ] Set up database backups
- [ ] Document connection setup

## Technical Details
- Use Google Cloud SQL
- Configure for multi-tenant architecture
- Set up proper security groups
- Enable SSL connections
- Configure monitoring and alerts

## Priority
High - Required for data persistence

## Effort
Medium (half day)" \
  --label "task,devops,database,priority:high,effort:medium" \
  --milestone "Phase 0: Foundation & DevOps" || echo "Issue may already exist"

# Issue 4: Dockerize applications
gh issue create \
  --title "[Task] Dockerize frontend and backend applications" \
  --body "## Description
Create Docker containers for both frontend and backend applications.

## Acceptance Criteria
- [ ] Create backend Dockerfile
- [ ] Create frontend Dockerfile
- [ ] Create docker-compose.yml for development
- [ ] Create docker-compose.yml for production
- [ ] Optimize Docker images for size
- [ ] Set up multi-stage builds
- [ ] Document Docker usage

## Technical Details
- Use Python 3.11+ for backend
- Use Node.js 18+ for frontend
- Optimize for production deployment
- Include health checks
- Set up proper networking

## Priority
Medium - Required for deployment

## Effort
Medium (half day)" \
  --label "task,devops,docker,priority:medium,effort:medium" \
  --milestone "Phase 0: Foundation & DevOps" || echo "Issue may already exist"

# Issue 5: Create CI/CD pipeline
gh issue create \
  --title "[Task] Create GitHub Actions CI/CD pipeline" \
  --body "## Description
Set up automated CI/CD pipeline with GitHub Actions.

## Acceptance Criteria
- [ ] Run tests on every PR
- [ ] Build Docker images
- [ ] Deploy to staging environment
- [ ] Require manual approval for production
- [ ] Security scanning
- [ ] Code quality checks
- [ ] Performance testing

## Technical Details
- Use GitHub Actions
- Deploy to Google Cloud Run
- Include security scanning
- Set up proper secrets management
- Configure environment-specific deployments

## Priority
High - Required for automated deployment

## Effort
Large (1-2 days)" \
  --label "task,devops,ci-cd,priority:high,effort:large" \
  --milestone "Phase 0: Foundation & DevOps" || echo "Issue may already exist"

# Create Phase 1 issues
echo "📝 Creating Phase 1 issues..."

# Issue 6: Create database models
gh issue create \
  --title "[Feature] Create database models for accounts and transactions" \
  --body "## Description
Design and implement SQLAlchemy models for financial accounts and transactions.

## Acceptance Criteria
- [ ] User model with multi-tenant support
- [ ] Account model (Current Account, Savings, etc.)
- [ ] Transaction model with proper relationships
- [ ] Category model for transaction categorization
- [ ] Categorization rules model
- [ ] Alembic migration scripts
- [ ] Model validation and constraints

## Technical Details
- Use SQLAlchemy ORM
- Implement proper relationships
- Add tenant_id for multi-tenancy
- Include audit fields (created_at, updated_at)
- Add proper indexes for performance

## Priority
Critical - Core data models

## Effort
Large (1-2 days)" \
  --label "enhancement,backend,database,priority:critical,effort:large" \
  --milestone "Phase 1: Core Functionality (MVP)" || echo "Issue may already exist"

# Issue 7: File import functionality
gh issue create \
  --title "[Feature] Build file import component for CSV, OFX, and QIF files" \
  --body "## Description
Create frontend component and backend logic to import financial data from various file formats.

## Acceptance Criteria
- [ ] Frontend file upload component
- [ ] Backend CSV parser
- [ ] Backend OFX parser
- [ ] Backend QIF parser
- [ ] File validation and error handling
- [ ] Progress indicators
- [ ] Batch processing support

## Technical Details
- Use React for frontend component
- Implement proper file validation
- Handle large files efficiently
- Support multiple file formats
- Add proper error messages

## Priority
High - Core functionality

## Effort
Large (1-2 days)" \
  --label "enhancement,frontend,backend,priority:high,effort:large" \
  --milestone "Phase 1: Core Functionality (MVP)" || echo "Issue may already exist"

# Issue 8: Transaction categorization engine
gh issue create \
  --title "[Feature] Develop rules-based categorization engine" \
  --body "## Description
Create an intelligent system to automatically categorize transactions based on user-defined rules.

## Acceptance Criteria
- [ ] Rule creation interface
- [ ] Rule matching engine
- [ ] Automatic categorization
- [ ] Manual override capability
- [ ] Rule testing and validation
- [ ] Performance optimization

## Technical Details
- Use regex patterns for matching
- Implement rule priority system
- Add rule performance metrics
- Support complex rule conditions
- Cache frequently used rules

## Priority
High - Core functionality

## Effort
Large (1-2 days)" \
  --label "enhancement,backend,frontend,priority:high,effort:large" \
  --milestone "Phase 1: Core Functionality (MVP)" || echo "Issue may already exist"

echo "✅ Initial issues created successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Review the created issues in GitHub"
echo "2. Assign issues to team members"
echo "3. Set up project boards for tracking"
echo "4. Start working on Phase 0 issues"
echo ""
echo "🔗 View issues: https://github.com/$REPO_OWNER/$REPO_NAME/issues"
echo "📊 View milestones: https://github.com/$REPO_OWNER/$REPO_NAME/milestones"
