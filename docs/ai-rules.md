# AI Assistant Instructions

You are an expert full-stack developer. Adhere to the following rules for all generated code and explanations:

## 1. Technology Stack

* **Backend:** Python 3.11+ with the FastAPI framework.
* **Database:** PostgreSQL. Use SQLAlchemy with Alembic for ORM and migrations.
* **Frontend:** React 18+ with TypeScript, using Vite for the build tool.
* **UI Components:** Use the MUI (Material-UI) library.
* **Styling:** Use Emotion, as it's the default styling engine for MUI.
* **Deployment:** The application will be containerized with Docker and run on Google Cloud Platform (GCP).

## 2. Code Quality & Style

* Generate clean, modular, and well-documented code.
* Follow Python PEP 8 standards for the backend.
* Use functional components with React Hooks. Avoid class components.
* All code must be strongly typed (Python type hints, TypeScript for React).

## 3. Security First

* **NEVER commit secrets, API keys, or sensitive data to the repository.**
* Use environment variables for all sensitive configuration.
* Implement user authentication with JWTs, including refresh tokens.
* All API endpoints must be protected by default unless explicitly public (e.g., login/register).
* Use prepared statements (via the ORM) to prevent SQL injection.
* Validate and sanitize all user inputs on both the frontend and backend.
* Implement 2FA using a TOTP (Time-based One-Time Password) library.
* All secrets must be stored in environment variables or secure secret management systems.
* Never hardcode passwords, API keys, database credentials, or JWT secrets in code.

## 4. Testing is Mandatory

* **Unit Tests:** Every function or logical unit must have a corresponding unit test. Use `pytest` for the backend and `Vitest` with React Testing Library for the frontend.
* **Integration Tests:** Write integration tests for API endpoints to test the full request/response cycle.
* **End-to-End (E2E) Tests:** E2E tests will be written using `Playwright` to simulate user journeys.

## 5. Database

* The architecture is multi-tenant using a shared database model (tables must have a `tenant_id` which maps to a `user_id`).
* Generate Alembic migration scripts for any database schema changes.

6.  **Logging & Observability:**
    * Implement structured logging using `structlog` for all application components.
    * Use Grafana Loki for log aggregation and Prometheus for metrics collection.
    * Include three types of logs: Audit (security/compliance), Functional (business analytics), and Debug (development/AI context).
    * All logs must be in JSON format with consistent field names and timestamps.
    * Include AI assistant context in debug logs (reasoning steps, token usage, decision points).
    * Make log retention configurable per log type (audit: 7 years, functional: 1 year, debug: 30 days).

7.  **Issue Completion Workflow:**
    * **MANDATORY**: When completing any GitHub issue, ALWAYS:
      1. Commit all changes with descriptive commit message including "✅ Complete Issue #[number]"
      2. Include "Resolves #[number]" in commit message to auto-close issue
      3. Push changes to the repository
      4. Update README.md roadmap to mark issue as completed
      5. Update any relevant documentation files
    * Use conventional commit format: `✅ Complete Issue #[number]: [Brief description]`
    * Include detailed description of what was implemented
    * Reference the issue number in both commit message and code comments
    * Ensure all acceptance criteria from the issue are met before marking complete
