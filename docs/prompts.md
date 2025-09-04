# Development Prompts

## Prompt 1: Backend Project Setup (FastAPI)

"Using the rules defined above, generate the project structure for a Python FastAPI backend. Create a main application file that includes a basic health check endpoint at /health. Set up the folder structure to be modular, with separate directories for api (routers), core (config, security), db (database session, models), and schemas (Pydantic models). Include a requirements.txt file with FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic, and python-jose for JWTs."

## Prompt 2: User Authentication API

"Create the API for user registration and login.

Database Model: Define a User model using SQLAlchemy. It should include id (UUID), email (unique), hashed_password, is_active, and columns for 2FA (otp_secret, is_otp_enabled).

Pydantic Schemas: Create schemas for user creation (UserCreate), user response (User), and token data (Token).

Security: Implement password hashing using passlib. Create utility functions to generate and verify JWT access and refresh tokens.

API Router: Create a router with endpoints for /register, /login, and /users/me (a protected endpoint that returns the current user's details)."

## Prompt 3: Frontend Project Setup (React)

"Set up a new React project using Vite and TypeScript. Install and configure MUI, Emotion, and React Router. Create a simple folder structure with directories for components, pages, and services. Create three basic pages: LoginPage, RegisterPage, and a protected DashboardPage. The dashboard page should only be accessible to logged-in users."

## Prompt 4: Dockerization

"Create a Dockerfile for the FastAPI backend and a multi-stage Dockerfile for the React frontend (using Nginx to serve the final build). Then, create a docker-compose.yml file that orchestrates the backend, frontend, and a PostgreSQL database service. Ensure the services can communicate with each other."

## Prompt 5: CI/CD Pipeline with GitHub Actions

"Create a GitHub Actions workflow file (.github/workflows/ci-cd.yml). This pipeline should be triggered on a push to the main branch or on a pull request. The workflow should have jobs for:

Lint & Test: Install dependencies and run pytest for the backend and vitest for the frontend.

Build: If tests pass, build the Docker images for both services.

Deploy to Staging: Push the Docker images to Google Artifact Registry and deploy them to a staging environment on Google Cloud Run."
