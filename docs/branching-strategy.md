# Branching Strategy for TheTally

## 🌳 Branch Structure

### Main Branches

- **`main`**: Production-ready code
  - Always deployable
  - Protected by security gates
  - Requires PR approval
  - Triggers production security scans

- **`develop`**: Integration branch
  - Latest development changes
  - Pre-production testing
  - Integration testing
  - Staging deployments

### Feature Branches

- **`feature/*`**: New features
  - `feature/user-authentication`
  - `feature/dashboard-ui`
  - `feature/database-health-check`
  - Merged into `develop` when complete

- **`hotfix/*`**: Emergency fixes
  - `hotfix/security-patch`
  - `hotfix/critical-bug-fix`
  - Merged directly to `main`

## 🔄 Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/new-feature
# Make changes
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
# Create PR to develop
```

### 2. Integration Testing
```bash
# Merge feature to develop
git checkout develop
git merge feature/new-feature
git push origin develop
# Deploy to staging for testing
```

### 3. Production Release
```bash
# Create PR from develop to main
# Security scans run automatically
# After approval, merge to main
# Deploy to production
```

## 🛡️ Security Integration

### Feature Branches
- **Light security scanning**
- Only blocks on HIGH severity issues
- Development-friendly configurations
- Quick feedback for developers

### Develop Branch
- **Medium security scanning**
- Blocks on HIGH + some MEDIUM issues
- Staging environment validation
- Integration testing

### Main Branch
- **Rigorous security scanning**
- Blocks on HIGH + high confidence MEDIUM
- Production configuration validation
- All security gates must pass

## 📋 Branch Protection Rules

### Main Branch Protection
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- Restrict pushes to main
- Require security scans to pass

### Develop Branch Protection
- Require pull request reviews
- Require status checks to pass
- Allow force pushes (for integration)

## 🚀 Deployment Strategy

### Staging (develop branch)
- Automatic deployment on merge
- Light security scanning
- Integration testing
- User acceptance testing

### Production (main branch)
- Manual deployment trigger
- Rigorous security scanning
- Production validation
- Security gates must pass

## 🔧 GitHub Actions Integration

### Feature Branch Workflows
- Run on: `feature/*` branches
- Security: Development mode
- Testing: Unit + integration tests
- Deployment: None

### Develop Branch Workflows
- Run on: `develop` branch
- Security: Medium mode
- Testing: Full test suite
- Deployment: Staging environment

### Main Branch Workflows
- Run on: `main` branch
- Security: Production mode
- Testing: Full test suite + E2E
- Deployment: Production environment

## 📚 Best Practices

### 1. Branch Naming
- `feature/description-of-feature`
- `hotfix/description-of-fix`
- `chore/description-of-task`

### 2. Commit Messages
- Use conventional commits
- `feat:`, `fix:`, `docs:`, `chore:`
- Include issue numbers

### 3. Pull Requests
- Clear description of changes
- Link to related issues
- Request appropriate reviewers
- Ensure all checks pass

### 4. Security
- Never commit secrets
- Use environment variables
- Run security scans locally
- Address security issues promptly

## 🎯 Benefits

### For Development
- Parallel development
- Isolated feature work
- Easy rollback
- Clear history

### For Security
- Layered security scanning
- Production protection
- Gradual security validation
- Risk mitigation

### For Operations
- Controlled deployments
- Clear release process
- Easy troubleshooting
- Rollback capability

## 🚨 Emergency Procedures

### Hotfix Process
1. Create `hotfix/` branch from `main`
2. Make minimal fix
3. Run security scans
4. Create PR to `main`
5. Deploy immediately after merge
6. Merge back to `develop`

### Rollback Process
1. Identify last known good commit
2. Create rollback branch
3. Revert problematic changes
4. Deploy rollback
5. Investigate root cause
