"""
Comprehensive tests for authentication system.

This module tests all authentication endpoints, services, and security utilities
including user registration, login, 2FA setup, JWT token management, and password operations.
"""

import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from app.main import app
from app.models.user import User
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TwoFactorSetupRequest, TwoFactorVerifyRequest
from app.services.auth import AuthService
from app.utils.security import SecurityUtils
from app.db.session import get_db


# Test client
client = TestClient(app)


class TestSecurityUtils:
    """Test security utilities."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPass123!"  # nosec B105
        hashed = SecurityUtils.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert SecurityUtils.verify_password(password, hashed)
    
    def test_hash_password_weak_password(self):
        """Test password hashing with weak password."""
        weak_passwords = [
            "123",  # Too short
            "password",  # No uppercase, numbers, special chars
            "PASSWORD",  # No lowercase, numbers, special chars
            "Password",  # No numbers, special chars
            "Password123",  # No special chars
            "password123!",  # No uppercase
        ]
        
        for password in weak_passwords:
            with pytest.raises(ValueError):
                SecurityUtils.hash_password(password)
    
    def test_verify_password(self):
        """Test password verification."""
        password = "TestPass123!"  # nosec B105
        hashed = SecurityUtils.hash_password(password)
        
        assert SecurityUtils.verify_password(password, hashed)
        assert not SecurityUtils.verify_password("wrongpassword", hashed)
    
    def test_generate_jwt_token(self):
        """Test JWT token generation."""
        user_id = "test-user-id"
        tenant_id = "test-tenant-id"
        
        access_token = SecurityUtils.generate_jwt_token(user_id, tenant_id, "access")
        refresh_token = SecurityUtils.generate_jwt_token(user_id, tenant_id, "refresh")
        
        assert access_token
        assert refresh_token
        assert access_token != refresh_token
    
    def test_verify_jwt_token(self):
        """Test JWT token verification."""
        user_id = "test-user-id"
        tenant_id = "test-tenant-id"
        
        token = SecurityUtils.generate_jwt_token(user_id, tenant_id, "access")
        payload = SecurityUtils.verify_jwt_token(token)
        
        assert payload
        assert payload["sub"] == user_id
        assert payload["tenant_id"] == tenant_id
        assert payload["token_type"] == "access"
    
    def test_verify_jwt_token_invalid(self):
        """Test JWT token verification with invalid token."""
        invalid_token = "invalid.token.here"
        payload = SecurityUtils.verify_jwt_token(invalid_token)
        
        assert payload is None
    
    def test_validate_email(self):
        """Test email validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test@.com",
            "",
            None
        ]
        
        for email in valid_emails:
            assert SecurityUtils.validate_email(email)
        
        for email in invalid_emails:
            assert not SecurityUtils.validate_email(email)
    
    def test_generate_2fa_secret(self):
        """Test 2FA secret generation."""
        secret = SecurityUtils.generate_2fa_secret()
        
        assert secret
        assert len(secret) > 0


class TestAuthService:
    """Test authentication service."""
    
    def test_register_user_success(self, db_session: Session):
        """Test successful user registration."""
        user_data = UserRegisterRequest(
            email="test@example.com",
            password="TestPass123!"  # nosec B105
            first_name="Test",
            last_name="User"
        )
        
        user, access_token, refresh_token = AuthService.register_user(
            db_session, user_data, "test-tenant"
        )
        
        assert user.email == user_data.email
        assert user.first_name == user_data.first_name
        assert user.last_name == user_data.last_name
        assert user.tenant_id == "test-tenant"
        assert access_token
        assert refresh_token
    
    def test_register_user_duplicate_email(self, db_session: Session):
        """Test user registration with duplicate email."""
        user_data = UserRegisterRequest(
            email="test@example.com",
            password="TestPass123!"  # nosec B105
        )
        
        # Register first user
        AuthService.register_user(db_session, user_data, "test-tenant")
        
        # Try to register with same email
        with pytest.raises(ValueError, match="User with this email already exists"):
            AuthService.register_user(db_session, user_data, "test-tenant")
    
    def test_authenticate_user_success(self, db_session: Session):
        """Test successful user authentication."""
        # Register user first
        user_data = UserRegisterRequest(
            email="test@example.com",
            password="TestPass123!"  # nosec B105
        )
        user, _, _ = AuthService.register_user(db_session, user_data, "test-tenant")
        
        # Authenticate user
        login_data = UserLoginRequest(
            email="test@example.com",
            password="TestPass123!"  # nosec B105
        )
        auth_user, access_token, refresh_token = AuthService.authenticate_user(
            db_session, login_data, "test-tenant"
        )
        
        assert auth_user.id == user.id
        assert access_token
        assert refresh_token
    
    def test_authenticate_user_invalid_credentials(self, db_session: Session):
        """Test user authentication with invalid credentials."""
        login_data = UserLoginRequest(
            email="nonexistent@example.com",
            password="wrongpassword"
        )
        
        with pytest.raises(ValueError, match="Invalid email or password"):
            AuthService.authenticate_user(db_session, login_data, "test-tenant")
    
    def test_authenticate_user_wrong_password(self, db_session: Session):
        """Test user authentication with wrong password."""
        # Register user first
        user_data = UserRegisterRequest(
            email="test@example.com",
            password="TestPass123!"  # nosec B105
        )
        AuthService.register_user(db_session, user_data, "test-tenant")
        
        # Try to authenticate with wrong password
        login_data = UserLoginRequest(
            email="test@example.com",
            password="WrongPass123!"
        )
        
        with pytest.raises(ValueError, match="Invalid email or password"):
            AuthService.authenticate_user(db_session, login_data, "test-tenant")
    
    def test_setup_2fa(self, db_session: Session):
        """Test 2FA setup."""
        # Register user first
        user_data = UserRegisterRequest(
            email="test@example.com",
            password="TestPass123!"  # nosec B105
        )
        user, _, _ = AuthService.register_user(db_session, user_data, "test-tenant")
        
        # Setup 2FA
        setup_data = TwoFactorSetupRequest(password="TestPass123!"  # nosec B105)
        result = AuthService.setup_2fa(db_session, user, setup_data)
        
        assert "secret" in result
        assert "qr_code_url" in result
        assert "backup_codes" in result
        assert len(result["backup_codes"]) == 10
    
    def test_setup_2fa_invalid_password(self, db_session: Session):
        """Test 2FA setup with invalid password."""
        # Register user first
        user_data = UserRegisterRequest(
            email="test@example.com",
            password="TestPass123!"  # nosec B105
        )
        user, _, _ = AuthService.register_user(db_session, user_data, "test-tenant")
        
        # Try to setup 2FA with wrong password
        setup_data = TwoFactorSetupRequest(password="WrongPass123!")
        
        with pytest.raises(ValueError, match="Invalid password"):
            AuthService.setup_2fa(db_session, user, setup_data)
    
    def test_verify_2fa(self, db_session: Session):
        """Test 2FA verification."""
        # Register user and setup 2FA
        user_data = UserRegisterRequest(
            email="test@example.com",
            password="TestPass123!"  # nosec B105
        )
        user, _, _ = AuthService.register_user(db_session, user_data, "test-tenant")
        
        setup_data = TwoFactorSetupRequest(password="TestPass123!"  # nosec B105)
        AuthService.setup_2fa(db_session, user, setup_data)
        
        # Mock TOTP verification
        with patch('pyotp.TOTP.verify', return_value=True):
            verify_data = TwoFactorVerifyRequest(code="123456")
            success = AuthService.verify_2fa(db_session, user, verify_data)
            
            assert success
            assert user.totp_enabled
    
    def test_refresh_tokens(self, db_session: Session):
        """Test token refresh."""
        # Register user first
        user_data = UserRegisterRequest(
            email="test@example.com",
            password="TestPass123!"  # nosec B105
        )
        user, _, refresh_token = AuthService.register_user(db_session, user_data, "test-tenant")
        
        # Refresh tokens
        auth_user, new_access_token, new_refresh_token = AuthService.refresh_tokens(
            db_session, refresh_token, "test-tenant"
        )
        
        assert auth_user.id == user.id
        assert new_access_token
        assert new_refresh_token
        assert new_refresh_token != refresh_token


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_register_endpoint_success(self, db_session: Session):
        """Test successful user registration endpoint."""
        user_data = {
            "email": "test@example.com",
            "password": "TestPass123!"  # nosec B105
            "first_name": "Test",
            "last_name": "User"
        }
        
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "refresh_expires_in" in data
    
    def test_register_endpoint_validation_error(self, db_session: Session):
        """Test user registration endpoint with validation error."""
        user_data = {
            "email": "invalid-email",
            "password": "weak"
        }
        
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_endpoint_duplicate_email(self, db_session: Session):
        """Test user registration endpoint with duplicate email."""
        user_data = {
            "email": "test@example.com",
            "password": "TestPass123!"  # nosec B105
        }
        
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            # Register first user
            client.post("/api/v1/auth/register", json=user_data)
            
            # Try to register with same email
            response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_login_endpoint_success(self, db_session: Session):
        """Test successful user login endpoint."""
        # Register user first
        user_data = {
            "email": "test@example.com",
            "password": "TestPass123!"  # nosec B105
        }
        
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            client.post("/api/v1/auth/register", json=user_data)
            
            # Login
            login_data = {
                "email": "test@example.com",
                "password": "TestPass123!"  # nosec B105
            }
            response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_endpoint_invalid_credentials(self, db_session: Session):
        """Test user login endpoint with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_refresh_endpoint_success(self, db_session: Session):
        """Test successful token refresh endpoint."""
        # Register user and get refresh token
        user_data = {
            "email": "test@example.com",
            "password": "TestPass123!"  # nosec B105
        }
        
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            register_response = client.post("/api/v1/auth/register", json=user_data)
            refresh_token = register_response.json()["refresh_token"]
            
            # Refresh tokens
            refresh_data = {"refresh_token": refresh_token}
            response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_endpoint_invalid_token(self, db_session: Session):
        """Test token refresh endpoint with invalid token."""
        refresh_data = {"refresh_token": "invalid.token.here"}
        
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]
    
    def test_get_current_user_endpoint(self, db_session: Session):
        """Test get current user endpoint."""
        # Register user and get access token
        user_data = {
            "email": "test@example.com",
            "password": "TestPass123!"  # nosec B105
        }
        
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            register_response = client.post("/api/v1/auth/register", json=user_data)
            access_token = register_response.json()["access_token"]
            
            # Get current user
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "created_at" in data
    
    def test_get_current_user_endpoint_unauthorized(self, db_session: Session):
        """Test get current user endpoint without authentication."""
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_setup_2fa_endpoint(self, db_session: Session):
        """Test 2FA setup endpoint."""
        # Register user and get access token
        user_data = {
            "email": "test@example.com",
            "password": "TestPass123!"  # nosec B105
        }
        
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            register_response = client.post("/api/v1/auth/register", json=user_data)
            access_token = register_response.json()["access_token"]
            
            # Setup 2FA
            setup_data = {"password": "TestPass123!"}
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.post("/api/v1/auth/2fa/setup", json=setup_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "secret" in data
        assert "qr_code_url" in data
        assert "backup_codes" in data
    
    def test_verify_2fa_endpoint(self, db_session: Session):
        """Test 2FA verification endpoint."""
        # Register user, setup 2FA, and get access token
        user_data = {
            "email": "test@example.com",
            "password": "TestPass123!"  # nosec B105
        }
        
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            register_response = client.post("/api/v1/auth/register", json=user_data)
            access_token = register_response.json()["access_token"]
            
            # Setup 2FA
            setup_data = {"password": "TestPass123!"}
            headers = {"Authorization": f"Bearer {access_token}"}
            client.post("/api/v1/auth/2fa/setup", json=setup_data, headers=headers)
            
            # Mock TOTP verification
            with patch('pyotp.TOTP.verify', return_value=True):
                verify_data = {"code": "123456"}
                response = client.post("/api/v1/auth/2fa/verify", json=verify_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "2FA has been successfully enabled" in data["message"]
    
    def test_logout_endpoint(self, db_session: Session):
        """Test logout endpoint."""
        # Register user and get access token
        user_data = {
            "email": "test@example.com",
            "password": "TestPass123!"  # nosec B105
        }
        
        with patch('app.api.routers.auth.get_db', return_value=db_session):
            register_response = client.post("/api/v1/auth/register", json=user_data)
            access_token = register_response.json()["access_token"]
            
            # Logout
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Successfully logged out" in data["message"]


@pytest.fixture
def db_session():
    """Create a test database session."""
    # This would be replaced with actual test database setup
    # For now, return a mock session
    return MagicMock()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
