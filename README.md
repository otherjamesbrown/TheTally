# TheTally

> A modern, AI-friendly financial tracking application built with FastAPI, React, and PostgreSQL

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18+](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)

## 🎯 Overview

TheTally is a multi-tenant financial tracking application that helps users import, categorize, and visualize their financial data. Built with modern technologies and designed for AI-assisted development, it provides a secure, scalable platform for personal financial management.

### Key Features

- **🔐 Secure Authentication**: JWT with 2FA support
- **📊 Financial Data Import**: CSV, OFX, and QIF file support
- **🤖 AI-Powered Categorization**: Intelligent transaction categorization
- **📈 Data Visualization**: Interactive charts and dashboards
- **🏢 Multi-Tenant Architecture**: Secure data isolation
- **🔒 Security-First Design**: Comprehensive security measures
- **🤖 AI-Friendly Development**: Optimized for AI coding assistants

## 🏗️ Architecture

### Technology Stack

- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React 18+ with TypeScript
- **Database**: PostgreSQL with SQLAlchemy ORM
- **UI**: Material-UI (MUI) with Emotion styling
- **Deployment**: Docker containers on Google Cloud Platform
- **AI Integration**: Google Code Assist for PR reviews

### Project Structure

```
TheTally/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Data validation
│   │   ├── core/           # Configuration
│   │   └── utils/          # Shared utilities
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   └── services/       # API services
│   └── package.json        # Node dependencies
├── docs/                   # Comprehensive documentation
├── .github/                # GitHub workflows and templates
└── config/                 # Configuration files
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/otherjamesbrown/TheTally.git
   cd TheTally
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Setup

See [Development Setup Guide](docs/development-setup.md) for detailed instructions.

## 🔒 Security

TheTally implements comprehensive security measures:

- **Authentication**: JWT with refresh tokens
- **Authorization**: Role-based access control
- **2FA**: TOTP-based two-factor authentication
- **Data Protection**: Multi-tenant data isolation
- **Input Validation**: Comprehensive input sanitization
- **SQL Injection Prevention**: ORM-based queries only
- **Secrets Management**: Environment variables only

See [Security Guidelines](SECURITY.md) for detailed security practices.

## 🤖 AI-Assisted Development

This project is optimized for AI coding assistants:

- **Clear Architecture**: Modular, well-documented code
- **Type Safety**: Complete type hints and TypeScript
- **Consistent Patterns**: Predictable code organization
- **Comprehensive Documentation**: Detailed context for AI assistants
- **Automated Reviews**: Google Code Assist integration
- **Security Scanning**: Automated vulnerability detection

See [AI Rules](docs/ai-rules.md) for development guidelines.

## 📋 Project Roadmap

### Phase 0: Foundation & DevOps 🏗️
- [x] Project setup and architecture
- [x] Security configuration
- [x] [Implement user registration and login API](https://github.com/otherjamesbrown/TheTally/issues/2) - JWTs and 2FA support ✅
- [ ] [Dockerize frontend and backend applications](https://github.com/otherjamesbrown/TheTally/issues/5) - Containerization
- [ ] [Create GitHub Actions CI/CD pipeline](https://github.com/otherjamesbrown/TheTally/issues/6) - Automated deployment
- [ ] [Implement E2E tests for login flow](https://github.com/otherjamesbrown/TheTally/issues/7) - Quality assurance

### Phase 1: Core Functionality (MVP) 📊
- [ ] [Create database models for accounts and transactions](https://github.com/otherjamesbrown/TheTally/issues/3) - Data models
- [ ] [Implement core service layer](https://github.com/otherjamesbrown/TheTally/issues/8) - Business logic services
- [ ] [Build file import component for CSV, OFX, and QIF files](https://github.com/otherjamesbrown/TheTally/issues/9) - Data import
- [ ] [Implement backend file parsing logic](https://github.com/otherjamesbrown/TheTally/issues/10) - File processing
- [ ] [Develop rules-based categorization engine](https://github.com/otherjamesbrown/TheTally/issues/11) - Auto-categorization
- [ ] [Create UI for managing categorization rules](https://github.com/otherjamesbrown/TheTally/issues/12) - Rule management
- [ ] [Build transaction table view in the UI](https://github.com/otherjamesbrown/TheTally/issues/13) - Data visualization

### Phase 2: Financial Modelling & Visualization 📈
- [ ] [Create database models for investment pots](https://github.com/otherjamesbrown/TheTally/issues/14) - Investment tracking
- [ ] [Build retirement projection calculator](https://github.com/otherjamesbrown/TheTally/issues/15) - Financial modeling
- [ ] [Create dashboard with spending visualization](https://github.com/otherjamesbrown/TheTally/issues/16) - Data visualization

### Phase 3: Future Enhancements 🚀
- [ ] Open Banking integration
- [ ] Machine learning categorization
- [ ] Advanced analytics
- [ ] Mobile application

**View all issues:** [GitHub Issues](https://github.com/otherjamesbrown/TheTally/issues) | **Detailed planning:** [Project Roadmap](docs/project-roadmap.md)

## 🛠️ Development

### Code Quality Standards

- **Python**: PEP 8 compliance with type hints
- **TypeScript**: Strict mode with comprehensive typing
- **Testing**: Unit, integration, and E2E tests required
- **Documentation**: Comprehensive docstrings and comments
- **Security**: No hardcoded secrets, input validation
- **Architecture**: Service layer pattern, modular design

### AI Development Guidelines

1. **Naming**: Use descriptive, clear names
2. **Modularity**: Single responsibility principle
3. **Documentation**: Type hints and docstrings
4. **Security**: Environment variables for secrets
5. **Testing**: Comprehensive test coverage

See [AI Rules](docs/ai-rules.md) for detailed guidelines.

## 📚 Documentation

Comprehensive documentation is available in the `/docs` folder:

- [Architecture](docs/architecture.md) - System design and components
- [API Specification](docs/api-specification.md) - API endpoints and schemas
- [Database Schema](docs/database-schema.md) - Data model design
- [Security](docs/security.md) - Security implementation
- [Testing Strategy](docs/testing-strategy.md) - Testing approach
- [Deployment](docs/deployment.md) - Production deployment
- [Issue Management](docs/issue-management.md) - Project management

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Issue Management

- **Bug Reports**: Use the bug report template
- **Feature Requests**: Use the feature request template
- **Questions**: Use the question template
- **Tasks**: Use the task template

See [Issue Management](docs/issue-management.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Repository**: https://github.com/otherjamesbrown/TheTally
- **Documentation**: https://github.com/otherjamesbrown/TheTally/tree/main/docs
- **Issues**: https://github.com/otherjamesbrown/TheTally/issues
- **Discussions**: https://github.com/otherjamesbrown/TheTally/discussions

## 🙏 Acknowledgments

- FastAPI for the excellent Python web framework
- React and Material-UI for the frontend foundation
- PostgreSQL for reliable data storage
- Google Code Assist for AI-powered development
- The open source community for inspiration and tools

---

**Built with ❤️ for modern financial management**