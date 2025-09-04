# Project Roadmap

## Phase 0: Foundation & DevOps ("Hello, World!") 🏗️

- [x] Set up GitHub repository with backend (FastAPI) and frontend (React) folder structure.
- [x] Create basic "Hello World" endpoints and UI pages.
- [ ] **Create service layer architecture** - Implement services/, models/, and utils/ directories with proper structure for AI-friendly development.
- [ ] Implement user registration and login API with JWTs and 2FA.
- [ ] Set up PostgreSQL database on GCP.
- [ ] Dockerize the frontend and backend applications.
- [ ] Create a GitHub Actions CI/CD pipeline that:
  - Runs unit and integration tests on every PR.
  - Builds Docker images.
  - Deploys to a GCP staging environment automatically.
  - Requires manual approval for production deployment.
- [ ] Implement E2E tests for the login flow.

## Phase 1: Core Functionality (MVP) 📊

- [ ] Create API endpoints and database models for accounts (e.g., 'Current Account') and transactions.
- [ ] **Implement core service layer** - Create business logic services for user management, transaction processing, and categorization.
- [ ] Build the file import component in the frontend for CSV, OFX, and QIF files.
- [ ] Implement the backend logic to parse these files and store transactions.
- [ ] Develop the rules-based categorization engine.
- [ ] Create UI for users to manage their categorization rules (e.g., "Tesco" -> "Groceries").
- [ ] Build a simple transaction table view in the UI.

## Phase 2: Financial Modelling & Visualization 📈

- [ ] Create database models for investment pots (Pensions, ISAs).
- [ ] Build the simple retirement projection calculator.
- [ ] Use Recharts to display the projection as a line graph.
- [ ] Create a dashboard page to visualize spending by category using a pie chart or bar chart.

## Phase 3 & Beyond: Future Enhancements 🚀

- [ ] Implement transaction splitting.
- [ ] Integrate with an Open Banking API (e.g., TrueLayer) for direct bank connections.
- [ ] Evolve the categorization engine using a simple ML model.
- [ ] Add budgeting features and goal setting.
