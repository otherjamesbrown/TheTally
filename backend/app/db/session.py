"""
Database session configuration for TheTally backend.

This module provides database session management with support for:
- GCP Cloud SQL PostgreSQL
- SSL connections
- Connection pooling
- Multi-tenant architecture
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import structlog
from app.core.config import settings

# Get logger
logger = structlog.get_logger(__name__)

def create_database_engine():
    """
    Create database engine with GCP PostgreSQL configuration.
    
    Returns:
        SQLAlchemy engine configured for GCP Cloud SQL
    """
    # Build connection URL with SSL support
    if settings.GCP_PROJECT_ID:
        # GCP Cloud SQL configuration
        connection_url = (
            f"postgresql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
            f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}"
            f"/{settings.DATABASE_NAME}"
            f"?sslmode={settings.GCP_DATABASE_SSL_MODE}"
        )
        logger.info("Using GCP Cloud SQL PostgreSQL configuration")
    else:
        # Local development configuration
        connection_url = settings.DATABASE_URL
        logger.info("Using local PostgreSQL configuration")
    
    # Create engine with connection pooling
    engine = create_engine(
        connection_url,
        poolclass=QueuePool,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        pool_recycle=settings.DATABASE_POOL_RECYCLE,
        pool_pre_ping=True,
        echo=settings.DEBUG,
        connect_args={
            "sslmode": settings.GCP_DATABASE_SSL_MODE if settings.GCP_PROJECT_ID else "prefer"
        }
    )
    
    # Add connection event listeners for logging
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Set connection parameters for PostgreSQL."""
        with dbapi_connection.cursor() as cursor:
            # Set timezone to UTC
            cursor.execute("SET timezone TO 'UTC'")
            # Set statement timeout
            cursor.execute("SET statement_timeout = '30s'")
            # Set idle transaction timeout
            cursor.execute("SET idle_in_transaction_session_timeout = '10min'")
    
    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_connection, connection_record, connection_proxy):
        """Log when a connection is checked out from the pool."""
        logger.debug("Database connection checked out from pool")
    
    @event.listens_for(engine, "checkin")
    def receive_checkin(dbapi_connection, connection_record):
        """Log when a connection is checked in to the pool."""
        logger.debug("Database connection checked in to pool")
    
    return engine

# Create database engine
engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """
    Get database session with proper error handling and logging.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise
    finally:
        logger.debug("Database session closed")
        db.close()

def get_db_sync():
    """
    Get synchronous database session for non-async contexts.
    
    Returns:
        Database session
    """
    return SessionLocal()

def test_database_connection():
    """
    Test database connection and return status.
    
    Returns:
        Tuple of (is_connected, error_message)
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            if test_value == 1:
                logger.info("Database connection test successful")
                return True, None
            else:
                logger.error("Database connection test failed - unexpected result")
                return False, "Unexpected test result"
    except Exception as e:
        logger.error("Database connection test failed", error=str(e))
        return False, str(e)
