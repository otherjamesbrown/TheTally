# Project Roadmap

## Phase 0: Foundation & DevOps ("Hello, World!") 🏗️

- [x] Set up GitHub repository with backend (FastAPI) and frontend (React) folder structure.
- [x] Create basic "Hello World" endpoints and UI pages.
- [ ] [**Create service layer architecture**](https://github.com/otherjamesbrown/TheTally/issues/1) - Implement services/, models/, and utils/ directories with proper structure for AI-friendly development.
- [ ] [**Implement user registration and login API**](https://github.com/otherjamesbrown/TheTally/issues/2) - JWTs and 2FA support.
- [ ] [**Set up PostgreSQL database on GCP**](https://github.com/otherjamesbrown/TheTally/issues/4) - Database infrastructure.
- [ ] [**Dockerize frontend and backend applications**](https://github.com/otherjamesbrown/TheTally/issues/5) - Containerization.
- [ ] [**Create GitHub Actions CI/CD pipeline**](https://github.com/otherjamesbrown/TheTally/issues/6) that:
  - Runs unit and integration tests on every PR.
  - Builds Docker images.
  - Deploys to a GCP staging environment automatically.
  - Requires manual approval for production deployment.
- [ ] [**Implement E2E tests for the login flow**](https://github.com/otherjamesbrown/TheTally/issues/7) - Quality assurance.

## Phase 1: Core Functionality (MVP) 📊

- [ ] [**Create database models for accounts and transactions**](https://github.com/otherjamesbrown/TheTally/issues/3) - Data models for financial accounts.
- [ ] [**Implement core service layer**](https://github.com/otherjamesbrown/TheTally/issues/8) - Business logic services for user management, transaction processing, and categorization.
- [ ] [**Build file import component**](https://github.com/otherjamesbrown/TheTally/issues/9) - Frontend component for CSV, OFX, and QIF files.
- [ ] [**Implement backend file parsing logic**](https://github.com/otherjamesbrown/TheTally/issues/10) - Backend logic to parse files and store transactions.
- [ ] [**Develop rules-based categorization engine**](https://github.com/otherjamesbrown/TheTally/issues/11) - Auto-categorization system.
- [ ] [**Create UI for managing categorization rules**](https://github.com/otherjamesbrown/TheTally/issues/12) - User interface for rule management (e.g., "Tesco" -> "Groceries").
- [ ] [**Build transaction table view**](https://github.com/otherjamesbrown/TheTally/issues/13) - Simple transaction table in the UI.

## Phase 2: Financial Modelling & Visualization 📈

- [ ] [**Create database models for investment pots**](https://github.com/otherjamesbrown/TheTally/issues/14) - Investment tracking (Pensions, ISAs).
- [ ] [**Build retirement projection calculator**](https://github.com/otherjamesbrown/TheTally/issues/15) - Financial modeling tool.
- [ ] Use Recharts to display the projection as a line graph.
- [ ] [**Create dashboard with spending visualization**](https://github.com/otherjamesbrown/TheTally/issues/16) - Dashboard page to visualize spending by category using pie charts or bar charts.

## Phase 3 & Beyond: Future Enhancements 🚀

- [ ] Implement transaction splitting.
- [ ] Integrate with an Open Banking API (e.g., TrueLayer) for direct bank connections.
- [ ] Evolve the categorization engine using a simple ML model.
- [ ] Add budgeting features and goal setting.

---

**📋 View all issues:** [GitHub Issues](https://github.com/otherjamesbrown/TheTally/issues) | **🎯 Project Board:** [Project Board](https://github.com/otherjamesbrown/TheTally/projects) | **📖 Main README:** [README.md](../README.md)
