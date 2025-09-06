# Contributing to TheTally

Thank you for your interest in contributing to TheTally! This document provides guidelines and information for contributors.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/TheTally.git`
3. Follow the [Development Setup Guide](docs/development-setup.md)
4. Create a feature branch from `develop`: `git checkout develop && git checkout -b feature/your-feature-name`

### Branching Strategy
We use a feature branch workflow with integrated security scanning:
- **`main`**: Production-ready code, highly protected
- **`develop`**: Integration branch for staging/testing  
- **`feature/*`**: Development branches for new features
- **`hotfix/*`**: Emergency fixes for production

See [Branching Strategy](docs/branching-strategy.md) for detailed workflow.

## Development Process

### 1. Choose an Issue
- **Browse all issues:** [GitHub Issues](https://github.com/otherjamesbrown/TheTally/issues)
- **View roadmap with issue links:** [Project Roadmap](docs/project-roadmap.md)
- **Check issue labels:** Look for `good first issue`, `priority:high`, `effort:small` for beginners
- **Comment on the issue** to indicate you're working on it

### 2. Development Workflow
```bash
# Start from develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... code changes ...

# Run tests
npm test
pytest

# Run linting
npm run lint
black .
isort .
flake8 .

# Commit changes
git add .
git commit -m "feat: add your feature"

# Push branch
git push origin feature/your-feature-name
```

### 3. Pull Request Process
1. Create a pull request from your feature branch to `develop`
2. Fill out the pull request template
3. Ensure all checks pass (tests, linting, security scans)
4. Request review from maintainers
5. Address feedback and make requested changes
6. Once approved, maintainers will merge your PR to `develop`
7. For production releases, create a PR from `develop` to `main`

## Coding Standards

### Python (Backend)
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all functions and classes
- Use meaningful variable and function names
- Keep functions small and focused

```python
def calculate_transaction_total(transactions: List[Transaction]) -> Decimal:
    """
    Calculate the total amount for a list of transactions.
    
    Args:
        transactions: List of transaction objects
        
    Returns:
        Total amount as Decimal
    """
    return sum(t.amount for t in transactions)
```

### TypeScript (Frontend)
- Use TypeScript for all new code
- Follow React best practices with functional components
- Use meaningful component and variable names
- Keep components small and focused
- Use proper error handling

```typescript
interface TransactionProps {
  transaction: Transaction;
  onEdit: (id: string) => void;
}

const TransactionItem: React.FC<TransactionProps> = ({ transaction, onEdit }) => {
  return (
    <div>
      {/* Component implementation */}
    </div>
  );
};
```

### Database
- Use Alembic for all database changes
- Write migration scripts for schema changes
- Include rollback instructions in migrations
- Test migrations on sample data

## Testing Requirements

### Unit Tests
- Write unit tests for all new functions and methods
- Aim for 90%+ code coverage
- Use descriptive test names
- Test both success and error cases

```python
def test_calculate_transaction_total():
    """Test transaction total calculation."""
    transactions = [
        Transaction(amount=Decimal('10.50')),
        Transaction(amount=Decimal('25.00')),
    ]
    result = calculate_transaction_total(transactions)
    assert result == Decimal('35.50')
```

### Integration Tests
- Write integration tests for API endpoints
- Test database operations
- Test file upload functionality
- Test authentication flows

### E2E Tests
- Write E2E tests for critical user journeys
- Test cross-browser compatibility
- Test responsive design
- Test accessibility

## Documentation

### Code Documentation
- Write clear docstrings for all functions
- Add comments for complex logic
- Update README files when adding new features
- Keep API documentation up to date

### Pull Request Documentation
- Provide clear description of changes
- Include screenshots for UI changes
- Link to related issues
- Document any breaking changes

## Security Considerations

### Data Protection
- Never commit sensitive data (passwords, API keys, etc.)
- Use environment variables for configuration
- Validate all user inputs
- Use parameterized queries for database operations

### Authentication
- Implement proper authentication checks
- Use JWT tokens securely
- Implement rate limiting
- Log security events

## Performance Considerations

### Backend
- Use database indexes appropriately
- Implement pagination for large datasets
- Use async/await for I/O operations
- Monitor memory usage

### Frontend
- Optimize bundle size
- Use lazy loading for routes
- Implement proper caching
- Monitor Core Web Vitals

## Review Process

### Pull Request Review
1. **Automated Checks**: All PRs must pass automated tests and linting
2. **Code Review**: At least one maintainer must review the code
3. **Testing**: All new code must have appropriate tests
4. **Documentation**: Documentation must be updated for new features

### Review Guidelines
- Be constructive and respectful
- Focus on code quality and maintainability
- Ask questions if something is unclear
- Suggest improvements rather than just pointing out problems

## Release Process

### Versioning
- We use semantic versioning (MAJOR.MINOR.PATCH)
- Major versions for breaking changes
- Minor versions for new features
- Patch versions for bug fixes

### Release Notes
- Document all changes in release notes
- Highlight new features and improvements
- Note any breaking changes
- Include migration instructions if needed

## Getting Help

### Questions and Support
- **GitHub Issues**: Use issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Discord**: Join our Discord server for real-time chat
- **Email**: Contact maintainers directly for sensitive issues

### Resources
- [Development Setup Guide](docs/development-setup.md)
- [API Documentation](docs/api-specification.md)
- [Architecture Overview](docs/architecture.md)
- [Testing Strategy](docs/testing-strategy.md)

## Recognition

### Contributors
- All contributors are recognized in the project README
- Significant contributors may be invited to join the maintainer team
- Contributors are acknowledged in release notes

### Contribution Types
- Code contributions
- Documentation improvements
- Bug reports
- Feature suggestions
- Testing and quality assurance
- Community support

## License

By contributing to TheTally, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Thank You

Thank you for contributing to TheTally! Your contributions help make this project better for everyone.

---

*This contributing guide will be updated as the project evolves and new guidelines are established.*
