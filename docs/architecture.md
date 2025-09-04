# System Architecture

## Overview

TheTally is a multi-tenant financial tracking application built with a modern microservices architecture. The system allows users to import financial data, categorize transactions, and visualize their spending patterns.

## High-Level Architecture

### Production Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cloud Run     │    │   Cloud Run     │    │   Compute Engine│
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (PostgreSQL)  │
│   Auto-scaling  │    │   Auto-scaling  │    │   Self-managed  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cloud Run     │    │   Compute Engine│    │   Cloud Storage │
│   (Frontend)    │    │   (Logging)     │    │   (File Uploads)│
│   Metrics       │◄──►│   Loki+Prometheus│   │   + Log Archive│
└─────────────────┘    │   +Grafana      │    └─────────────────┘
                       └─────────────────┘
```

### Development Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   FastAPI       │    │   PostgreSQL    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI) with Emotion
- **Routing**: React Router
- **State Management**: React Context + Hooks
- **Charts**: Recharts

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy with Alembic migrations
- **Authentication**: JWT with refresh tokens + 2FA (TOTP)
- **File Processing**: Built-in CSV/OFX/QIF parsers
- **API Documentation**: FastAPI auto-generated OpenAPI/Swagger

### Database
- **Primary**: PostgreSQL
- **Architecture**: Multi-tenant (shared database, tenant isolation via tenant_id)
- **Migrations**: Alembic

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Cloud Platform**: Google Cloud Platform (GCP)
- **CI/CD**: GitHub Actions
- **Container Registry**: Google Artifact Registry
- **Deployment**: Google Cloud Run (Frontend & Backend)
- **Database**: Self-managed PostgreSQL on Compute Engine
- **File Storage**: Google Cloud Storage
- **Secrets**: Google Secret Manager
- **Logging**: Grafana Loki + Prometheus + Grafana on Compute Engine
- **Monitoring**: Self-managed observability stack

## Database Schema (Initial Planning)

*This section will be updated as we develop the application*

### Core Tables
- `users` - User accounts and authentication
- `tenants` - Multi-tenant organization (initially 1:1 with users)
- `accounts` - Financial accounts (Current Account, Savings, etc.)
- `transactions` - Individual financial transactions
- `categories` - Transaction categories
- `categorization_rules` - User-defined rules for auto-categorization

### Multi-Tenancy
All data tables will include a `tenant_id` column to ensure data isolation between users.

## API Structure

*This section will be detailed in api-specification.md*

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `POST /auth/2fa/enable` - Enable 2FA
- `POST /auth/2fa/verify` - Verify 2FA

### Core Endpoints
- `GET /health` - Health check
- `GET /users/me` - Current user profile
- `POST /import/upload` - File upload for transaction import
- `GET /transactions` - List transactions
- `POST /categories` - Create category
- `POST /rules` - Create categorization rule

## Security Architecture

- **Authentication**: JWT access tokens (15 min) + refresh tokens (7 days)
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: All data encrypted at rest and in transit
- **Multi-Factor Authentication**: TOTP-based 2FA
- **Input Validation**: Pydantic schemas for all API inputs
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

## Deployment Architecture

### Development
- Local development with Docker Compose
- Hot reload for both frontend and backend

### Staging
- Automated deployment via GitHub Actions
- Google Cloud Run services (staging environment)
- Self-managed PostgreSQL on Compute Engine (staging instance)

### Production
- Manual approval required for deployment
- Google Cloud Run services (production environment)
- Self-managed PostgreSQL on Compute Engine (production instance)
- Automated backups to Cloud Storage
- Monitoring and logging

## Future Considerations

- **Vector Database**: PostgreSQL with pgvector extension for ML features
- **Caching**: Redis for session management and caching (self-managed on Compute Engine)
- **Monitoring**: Google Cloud Monitoring and Logging
- **Open Banking**: Integration with TrueLayer or similar API
- **Machine Learning**: ML-based categorization engine using PostgreSQL
- **Search**: Full-text search using PostgreSQL's built-in capabilities
- **Analytics**: Time-series data using PostgreSQL with TimescaleDB extension

---

*This document will be updated as the architecture evolves during development.*
