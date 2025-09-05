# Docker Setup Guide

This document provides comprehensive instructions for running TheTally application using Docker containers.

## Overview

TheTally application is fully containerized with separate containers for:
- **PostgreSQL Database**: Data persistence layer
- **FastAPI Backend**: REST API and business logic
- **React Frontend**: User interface served by Nginx

## Prerequisites

- Docker Engine 20.10+ 
- Docker Compose 2.0+
- At least 2GB RAM available for containers
- Ports 3000, 8000, and 5432 available (for development)

## Quick Start

### Development Environment

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/otherjamesbrown/TheTally.git
   cd TheTally
   ```

2. **Start development environment**:
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432

### Production Environment

1. **Set up environment variables**:
   ```bash
   cp docker.env.example .env
   # Edit .env with your production values
   ```

2. **Start production environment**:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

3. **Access the application**:
   - Frontend: http://localhost (port 80)
   - Backend API: Internal only (use reverse proxy)

## Docker Compose Files

### Development (`docker-compose.dev.yml`)
- **Purpose**: Local development with hot reload
- **Features**:
  - Volume mounting for live code changes
  - Debug logging enabled
  - All ports exposed for easy access
  - Hot reload for both frontend and backend

### Production (`docker-compose.prod.yml`)
- **Purpose**: Production deployment
- **Features**:
  - Optimized builds with multi-stage Dockerfiles
  - Security hardening (non-root users)
  - Health checks and restart policies
  - Minimal port exposure
  - Environment variable configuration

### Default (`docker-compose.yml`)
- **Purpose**: General purpose setup
- **Features**: Balanced configuration for testing and staging

## Container Details

### Backend Container
- **Base Image**: Python 3.11-slim
- **Multi-stage Build**: Optimized for production
- **Security**: Non-root user execution
- **Health Check**: `/api/v1/health` endpoint
- **Dependencies**: PostgreSQL database

### Frontend Container
- **Build Stage**: Node.js 18 Alpine
- **Production Stage**: Nginx 1.25 Alpine
- **Security**: Non-root user execution
- **Health Check**: `/health` endpoint
- **Features**: SPA routing support, API proxy

### Database Container
- **Base Image**: PostgreSQL 15 Alpine
- **Features**: 
  - Automatic initialization scripts
  - Health checks
  - Persistent data volumes
  - UTF-8 encoding

## Environment Variables

### Required Variables
- `POSTGRES_PASSWORD`: Database password
- `SECRET_KEY`: JWT signing key
- `DATABASE_URL`: Full database connection string

### Optional Variables
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)
- `CORS_ORIGINS`: Allowed CORS origins
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT expiration (default: 30)

## Volume Management

### Development Volumes
- `postgres_dev_data`: Development database data
- `./backend:/app`: Backend code mounting
- `./frontend:/app`: Frontend code mounting

### Production Volumes
- `postgres_data`: Production database data
- No code mounting (uses built images)

## Network Configuration

### Development Network
- **Name**: `thetally-dev-network`
- **Type**: Bridge
- **Services**: All containers can communicate

### Production Network
- **Name**: `thetally-network`
- **Type**: Bridge
- **Services**: Isolated container communication

## Health Checks

All containers include health checks:
- **Database**: PostgreSQL readiness check
- **Backend**: HTTP health endpoint check
- **Frontend**: HTTP health endpoint check

## Security Features

### Container Security
- Non-root user execution
- Minimal base images (Alpine Linux)
- No unnecessary packages
- Proper file permissions

### Network Security
- Isolated container networks
- Minimal port exposure
- Internal service communication

### Data Security
- Environment variable configuration
- Secure default passwords
- Database initialization scripts

## Troubleshooting

### Common Issues

1. **Port Conflicts**:
   ```bash
   # Check what's using the ports
   lsof -i :3000
   lsof -i :8000
   lsof -i :5432
   ```

2. **Container Won't Start**:
   ```bash
   # Check container logs
   docker compose logs [service-name]
   
   # Check container status
   docker compose ps
   ```

3. **Database Connection Issues**:
   ```bash
   # Check database logs
   docker compose logs database
   
   # Test database connection
   docker compose exec database psql -U thetally_user -d thetally_dev
   ```

4. **Build Failures**:
   ```bash
   # Clean build (no cache)
   docker compose build --no-cache
   
   # Remove all containers and volumes
   docker compose down -v
   ```

### Performance Optimization

1. **Resource Limits**:
   ```yaml
   # Add to service definition
   deploy:
     resources:
       limits:
         memory: 512M
         cpus: '0.5'
   ```

2. **Build Optimization**:
   - Use `.dockerignore` files
   - Leverage Docker layer caching
   - Multi-stage builds

## Maintenance

### Regular Tasks

1. **Update Dependencies**:
   ```bash
   # Update base images
   docker compose pull
   
   # Rebuild with updates
   docker compose up --build
   ```

2. **Clean Up**:
   ```bash
   # Remove unused containers and images
   docker system prune -a
   
   # Remove specific volumes
   docker volume rm thetally_postgres_data
   ```

3. **Backup Database**:
   ```bash
   # Create backup
   docker compose exec database pg_dump -U thetally_user thetally_prod > backup.sql
   
   # Restore backup
   docker compose exec -T database psql -U thetally_user thetally_prod < backup.sql
   ```

## Development Workflow

### Making Changes

1. **Backend Changes**:
   - Edit code in `./backend/`
   - Changes are automatically reflected (dev mode)
   - Restart container if needed: `docker compose restart backend`

2. **Frontend Changes**:
   - Edit code in `./frontend/`
   - Changes are automatically reflected (dev mode)
   - Restart container if needed: `docker compose restart frontend`

3. **Database Changes**:
   - Run migrations: `docker compose exec backend alembic upgrade head`
   - Check database: `docker compose exec database psql -U thetally_user -d thetally_dev`

### Testing

```bash
# Run backend tests
docker compose exec backend pytest

# Run frontend tests
docker compose exec frontend npm test

# Run all tests
docker compose exec backend pytest && docker compose exec frontend npm test
```

## Production Deployment

### Pre-deployment Checklist

- [ ] Update environment variables
- [ ] Set secure passwords
- [ ] Configure reverse proxy (Nginx/Traefik)
- [ ] Set up SSL certificates
- [ ] Configure monitoring and logging
- [ ] Set up database backups
- [ ] Test health checks

### Deployment Commands

```bash
# Production deployment
docker compose -f docker-compose.prod.yml up -d --build

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

## Monitoring

### Health Monitoring
- Use container health checks
- Monitor `/api/v1/health` endpoint
- Set up alerts for container failures

### Log Monitoring
- Centralized logging with structured logs
- Use Grafana Loki for log aggregation
- Monitor application and container logs

### Performance Monitoring
- Use Prometheus for metrics collection
- Monitor container resource usage
- Set up alerts for resource limits

## Support

For issues related to Docker setup:
1. Check this documentation
2. Review container logs
3. Check GitHub issues
4. Contact the development team
