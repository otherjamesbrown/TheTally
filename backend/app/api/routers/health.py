"""
Health check endpoints for TheTally backend.

This module provides health check endpoints for monitoring application and database status.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
import structlog
from app.db.session import test_database_connection
from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Basic health status and application information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "app_name": settings.APP_NAME
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with system and database information.
    
    Returns:
        Comprehensive health status including system metrics and database connectivity
    """
    import psutil
    
    # Test database connection
    db_connected, db_error = test_database_connection()
    
    # Determine overall health status
    overall_status = "healthy"
    if not db_connected:
        overall_status = "unhealthy"
    
    health_data = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "app_name": settings.APP_NAME,
        "database": {
            "status": "connected" if db_connected else "disconnected",
            "error": db_error if not db_connected else None
        },
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }
    
    # Log health check
    logger.info("Health check performed", 
               status=overall_status,
               db_connected=db_connected)
    
    return health_data

@router.get("/health/database")
async def database_health_check():
    """
    Database-specific health check.
    
    Returns:
        Database connection status and performance metrics
    """
    db_connected, db_error = test_database_connection()
    
    if not db_connected:
        logger.warning("Database health check failed", error=db_error)
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {db_error}"
        )
    
    logger.info("Database health check successful")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "status": "connected",
            "host": settings.DATABASE_HOST,
            "port": settings.DATABASE_PORT,
            "name": settings.DATABASE_NAME,
            "ssl_enabled": settings.GCP_DATABASE_SSL_MODE == "require"
        }
    }

@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes/container orchestration.
    
    Returns:
        Application readiness status
    """
    # Test database connection
    db_connected, db_error = test_database_connection()
    
    if not db_connected:
        logger.warning("Readiness check failed - database not available", error=db_error)
        raise HTTPException(
            status_code=503,
            detail="Application not ready - database unavailable"
        )
    
    logger.info("Readiness check passed")
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration.
    
    Returns:
        Application liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
