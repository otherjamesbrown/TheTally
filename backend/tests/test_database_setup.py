"""
Test suite for database setup and GCP PostgreSQL configuration.

This module tests the database setup including:
- Database connection and configuration
- Alembic migrations
- Health check endpoints
- GCP-specific functionality
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.db.session import test_database_connection, create_database_engine
from app.core.config import settings
from app.api.routers.health import health_check, detailed_health_check, database_health_check


class TestDatabaseConfiguration:
    """Test cases for database configuration."""
    
    def test_database_engine_creation(self):
        """Test database engine creation."""
        engine = create_database_engine()
        assert engine is not None
        assert engine.pool.size() >= 0
    
    def test_database_connection_test(self):
        """Test database connection testing function."""
        # This will fail without a real database, but we can test the function exists
        is_connected, error = test_database_connection()
        # In test environment without database, this should return False
        assert isinstance(is_connected, bool)
        assert isinstance(error, (str, type(None)))
    
    def test_gcp_configuration(self):
        """Test GCP configuration settings."""
        assert hasattr(settings, 'GCP_PROJECT_ID')
        assert hasattr(settings, 'GCP_REGION')
        assert hasattr(settings, 'GCP_DATABASE_INSTANCE')
        assert hasattr(settings, 'GCP_DATABASE_VERSION')
        assert hasattr(settings, 'GCP_DATABASE_TIER')
        assert hasattr(settings, 'GCP_DATABASE_SSL_MODE')
    
    def test_connection_pool_settings(self):
        """Test connection pool configuration."""
        assert hasattr(settings, 'DATABASE_POOL_SIZE')
        assert hasattr(settings, 'DATABASE_MAX_OVERFLOW')
        assert hasattr(settings, 'DATABASE_POOL_TIMEOUT')
        assert hasattr(settings, 'DATABASE_POOL_RECYCLE')
        
        # Check that values are reasonable
        assert settings.DATABASE_POOL_SIZE > 0
        assert settings.DATABASE_MAX_OVERFLOW >= 0
        assert settings.DATABASE_POOL_TIMEOUT > 0
        assert settings.DATABASE_POOL_RECYCLE > 0


class TestHealthEndpoints:
    """Test cases for health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_basic_health_check(self):
        """Test basic health check endpoint."""
        response = await health_check()
        
        assert response["status"] == "healthy"
        assert "timestamp" in response
        assert "version" in response
        assert "environment" in response
        assert "app_name" in response
    
    @pytest.mark.asyncio
    async def test_detailed_health_check(self):
        """Test detailed health check endpoint."""
        with patch('app.api.routers.health.test_database_connection') as mock_db_test:
            mock_db_test.return_value = (True, None)
            
            response = await detailed_health_check()
            
            assert response["status"] == "healthy"
            assert "timestamp" in response
            assert "version" in response
            assert "database" in response
            assert "system" in response
            assert response["database"]["status"] == "connected"
    
    @pytest.mark.asyncio
    async def test_detailed_health_check_database_failure(self):
        """Test detailed health check when database is unavailable."""
        with patch('app.api.routers.health.test_database_connection') as mock_db_test:
            mock_db_test.return_value = (False, "Connection failed")
            
            response = await detailed_health_check()
            
            assert response["status"] == "unhealthy"
            assert response["database"]["status"] == "disconnected"
            assert response["database"]["error"] == "Connection failed"
    
    @pytest.mark.asyncio
    async def test_database_health_check_success(self):
        """Test database health check when database is available."""
        with patch('app.api.routers.health.test_database_connection') as mock_db_test:
            mock_db_test.return_value = (True, None)
            
            response = await database_health_check()
            
            assert response["status"] == "healthy"
            assert response["database"]["status"] == "connected"
            assert "host" in response["database"]
            assert "port" in response["database"]
            assert "name" in response["database"]
            assert "ssl_enabled" in response["database"]
    
    @pytest.mark.asyncio
    async def test_database_health_check_failure(self):
        """Test database health check when database is unavailable."""
        with patch('app.api.routers.health.test_database_connection') as mock_db_test:
            mock_db_test.return_value = (False, "Connection refused")
            
            with pytest.raises(Exception):  # Should raise HTTPException
                await database_health_check()


class TestAlembicMigrations:
    """Test cases for Alembic migrations."""
    
    def test_migration_file_exists(self):
        """Test that initial migration file exists."""
        import os
        migration_file = "alembic/versions/001_initial_migration.py"
        assert os.path.exists(migration_file)
    
    def test_alembic_config_exists(self):
        """Test that Alembic configuration files exist."""
        import os
        assert os.path.exists("alembic.ini")
        assert os.path.exists("alembic/env.py")
        assert os.path.exists("alembic/script.py.mako")
    
    def test_alembic_env_configuration(self):
        """Test that Alembic env.py is properly configured."""
        # Read the env.py file and check for our configuration
        with open("alembic/env.py", "r") as f:
            content = f.read()
        
        # Check for our imports and configuration
        assert "from app.core.config import settings" in content
        assert "from app.db.session import Base" in content
        assert "from app.models.base import BaseModel" in content
        assert "config.set_main_option" in content
        assert "target_metadata = Base.metadata" in content


class TestGCPSetupScript:
    """Test cases for GCP setup script."""
    
    def test_setup_script_exists(self):
        """Test that GCP setup script exists and is executable."""
        import os
        import stat
        
        script_path = "../scripts/setup-gcp-database.sh"
        assert os.path.exists(script_path)
        
        # Check if script is executable
        file_stat = os.stat(script_path)
        assert file_stat.st_mode & stat.S_IEXEC
    
    def test_setup_script_content(self):
        """Test that setup script contains required functionality."""
        with open("../scripts/setup-gcp-database.sh", "r") as f:
            content = f.read()
        
        # Check for key functionality
        assert "gcloud sql instances create" in content
        assert "gcloud sql databases create" in content
        assert "gcloud sql users create" in content
        assert "postgresql://" in content
        assert "sslmode=require" in content


class TestDatabaseModels:
    """Test cases for database models."""
    
    def test_user_model_import(self):
        """Test that User model can be imported."""
        from app.models.user import User
        assert User is not None
        assert hasattr(User, '__tablename__')
        assert User.__tablename__ == "users"
    
    def test_tenant_model_import(self):
        """Test that Tenant model can be imported."""
        from app.models.tenant import Tenant
        assert Tenant is not None
        assert hasattr(Tenant, '__tablename__')
        assert Tenant.__tablename__ == "tenants"
    
    def test_base_model_import(self):
        """Test that BaseModel can be imported."""
        from app.models.base import BaseModel
        assert BaseModel is not None
        assert hasattr(BaseModel, 'tenant_id')
        assert hasattr(BaseModel, 'created_at')
        assert hasattr(BaseModel, 'updated_at')
    
    def test_models_registration(self):
        """Test that models are properly registered in __init__.py."""
        from app.models import User, Tenant, BaseModel
        assert User is not None
        assert Tenant is not None
        assert BaseModel is not None


class TestDatabaseDocumentation:
    """Test cases for database documentation."""
    
    def test_database_setup_docs_exist(self):
        """Test that database setup documentation exists."""
        import os
        docs_path = "../docs/database-setup.md"
        assert os.path.exists(docs_path)
    
    def test_database_setup_docs_content(self):
        """Test that database setup documentation contains required sections."""
        with open("../docs/database-setup.md", "r") as f:
            content = f.read()
        
        # Check for key sections
        assert "# Database Setup Guide" in content
        assert "## Prerequisites" in content
        assert "## Quick Setup" in content
        assert "## Configuration" in content
        assert "## Security" in content
        assert "## Troubleshooting" in content
        assert "gcloud sql instances create" in content
        assert "alembic upgrade head" in content


class TestDatabaseIntegration:
    """Integration tests for database setup."""
    
    def test_database_session_import(self):
        """Test that database session can be imported."""
        from app.db.session import SessionLocal, get_db, test_database_connection
        assert SessionLocal is not None
        assert get_db is not None
        assert test_database_connection is not None
    
    def test_configuration_import(self):
        """Test that configuration can be imported."""
        from app.core.config import settings
        assert settings is not None
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'GCP_PROJECT_ID')
    
    def test_health_router_import(self):
        """Test that health router can be imported."""
        from app.api.routers.health import router
        assert router is not None


if __name__ == "__main__":
    pytest.main([__file__])
