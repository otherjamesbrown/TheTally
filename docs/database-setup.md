# Database Setup Guide

This guide covers setting up PostgreSQL database on Google Cloud Platform for TheTally application.

## Overview

TheTally uses PostgreSQL as its primary database with the following features:
- **Multi-tenant architecture** with tenant isolation
- **SSL connections** for security
- **Connection pooling** for performance
- **Automated backups** for data protection
- **Alembic migrations** for schema management

## Prerequisites

- Google Cloud Platform account
- `gcloud` CLI installed and authenticated
- Project with billing enabled
- Required APIs enabled (SQL Admin, Cloud Resource Manager)

## Quick Setup

### 1. Automated Setup (Recommended)

Run the automated setup script:

```bash
# Set your GCP project ID
export GCP_PROJECT_ID="your-project-id"

# Run the setup script
./scripts/setup-gcp-database.sh
```

The script will:
- Create a Cloud SQL PostgreSQL instance
- Set up the database and user
- Generate secure passwords
- Display connection information

### 2. Manual Setup

If you prefer manual setup, follow these steps:

#### Step 1: Enable APIs

```bash
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
```

#### Step 2: Create Cloud SQL Instance

```bash
gcloud sql instances create thetally-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 \
    --deletion-protection
```

#### Step 3: Set Root Password

```bash
gcloud sql users set-password root \
    --host=% \
    --instance=thetally-postgres \
    --password="$(openssl rand -base64 32)"  # nosec B105
```

#### Step 4: Create Database

```bash
gcloud sql databases create thetally_prod \
    --instance=thetally-postgres
```

#### Step 5: Create Database User

```bash
gcloud sql users create thetally_user \
    --instance=thetally-postgres \
    --password="$(openssl rand -base64 32)"  # nosec B105
```

## Configuration

### Environment Variables

Set the following environment variables in your `.env` file:

```bash
# GCP Configuration
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
GCP_DATABASE_INSTANCE=thetally-postgres
GCP_DATABASE_VERSION=POSTGRES_15
GCP_DATABASE_TIER=db-f1-micro
GCP_DATABASE_SSL_MODE=require

# Database Connection
DATABASE_HOST=your-instance-ip
DATABASE_PORT=5432
DATABASE_NAME=thetally_prod
DATABASE_USER=thetally_user
DATABASE_PASSWORD=${DATABASE_PASSWORD:-your-secure-password}  # nosec B105

# Connection Pool
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

### Database URL

The application constructs the database URL as:
```
postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?sslmode={GCP_DATABASE_SSL_MODE}
```

## Database Migrations

### Running Migrations

```bash
# Check current migration status
alembic current

# Run all pending migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Rollback one migration
alembic downgrade -1
```

### Migration Files

Migrations are stored in `backend/alembic/versions/` and follow the naming convention:
- `001_initial_migration.py` - Initial schema
- `002_add_feature.py` - Feature additions
- `003_update_schema.py` - Schema updates

## Security

### SSL Connections

All database connections use SSL by default:
- **Development**: `sslmode=prefer`
- **Production**: `sslmode=require`

### Connection Security

- Database access is restricted to authorized IPs
- User passwords are generated securely
- Connection pooling prevents connection exhaustion
- Prepared statements prevent SQL injection

### Backup Strategy

- **Automated daily backups** at 3:00 AM UTC
- **Point-in-time recovery** enabled
- **Binary logging** for replication
- **7-day retention** for backups

## Monitoring

### Health Checks

The application includes database health checks:

```python
from app.db.session import test_database_connection

# Test connection
is_connected, error = test_database_connection()
if is_connected:
    print("Database connection successful")
else:
    print(f"Database connection failed: {error}")
```

### Health Endpoint

Access the health endpoint to check database status:
```bash
curl http://localhost:8000/api/v1/health
```

## Troubleshooting

### Common Issues

#### Connection Refused
```bash
# Check if instance is running
gcloud sql instances describe thetally-postgres

# Check authorized networks
gcloud sql instances describe thetally-postgres --format="value(settings.ipConfiguration.authorizedNetworks[].value)"
```

#### SSL Certificate Issues
```bash
# Download SSL certificate
gcloud sql ssl-certs create client-cert thetally-postgres --cert-file=client-cert.pem --key-file=client-key.pem
```

#### Migration Failures
```bash
# Check migration status
alembic current

# Show migration history
alembic history

# Reset to specific migration
alembic downgrade <revision_id>
```

### Performance Tuning

#### Connection Pool Settings
```python
# Adjust pool size based on load
DATABASE_POOL_SIZE=20          # Base connections
DATABASE_MAX_OVERFLOW=30       # Additional connections
DATABASE_POOL_TIMEOUT=60       # Connection timeout
DATABASE_POOL_RECYCLE=1800     # Connection recycle time
```

#### Database Instance Sizing
- **Development**: `db-f1-micro` (1 vCPU, 0.6 GB RAM)
- **Staging**: `db-g1-small` (1 vCPU, 1.7 GB RAM)
- **Production**: `db-n1-standard-2` (2 vCPUs, 7.5 GB RAM)

## Development Setup

### Local Development

For local development, you can use a local PostgreSQL instance:

```bash
# Install PostgreSQL locally
brew install postgresql  # macOS
sudo apt-get install postgresql  # Ubuntu

# Start PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Ubuntu

# Create local database
createdb thetally_dev
```

### Docker Development

Use Docker for consistent development environment:

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: thetally_dev
      POSTGRES_USER: thetally_user
      POSTGRES_PASSWORD: password  # nosec B105
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Production Considerations

### High Availability

For production, consider:
- **Multi-zone deployment** for high availability
- **Read replicas** for read scaling
- **Connection pooling** with PgBouncer
- **Monitoring** with Cloud Monitoring

### Scaling

- **Vertical scaling**: Upgrade instance tier
- **Horizontal scaling**: Add read replicas
- **Connection pooling**: Use Cloud SQL Proxy
- **Caching**: Implement Redis for frequently accessed data

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Cloud SQL documentation
3. Check application logs for errors
4. Contact the development team

## References

- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
