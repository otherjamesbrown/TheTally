"""
Unit tests for UserService.

This module contains comprehensive unit tests for the UserService class,
testing all CRUD operations, validation, and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from decimal import Decimal

from app.services.user_service import UserService
from app.models.user import User
from app.schemas.auth import UserRegisterRequest, UserUpdateRequest


class TestUserService:
    """Test cases for UserService."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def user_service(self, mock_db_session):
        """Create a UserService instance with mocked database session."""
        return UserService(db_session=mock_db_session)
    
    @pytest.fixture
    def sample_user_data(self):
        """Create sample user registration data."""
        return UserRegisterRequest(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            phone_number="+1234567890",
            timezone="UTC",
            language="en",
            password="testpassword123"
        )
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user object."""
        user = Mock(spec=User)
        user.id = "user_123"
        user.email = "test@example.com"
        user.username = "testuser"
        user.first_name = "Test"
        user.last_name = "User"
        user.tenant_id = "tenant_123"
        user.is_active = True
        user.is_verified = False
        user.is_superuser = False
        return user
    
    def test_create_user_success(self, user_service, sample_user_data, sample_user):
        """Test successful user creation."""
        # Mock database queries
        user_service.db.query.return_value.filter.return_value.first.return_value = None  # No existing user
        user_service.create.return_value = sample_user
        
        # Call the method
        result = user_service.create_user(sample_user_data, "tenant_123", "admin_123")
        
        # Assertions
        assert result == sample_user
        user_service.create.assert_called_once()
        user_service.db.commit.assert_called_once()
    
    def test_create_user_duplicate_email(self, user_service, sample_user_data, sample_user):
        """Test user creation with duplicate email."""
        # Mock existing user
        user_service.db.query.return_value.filter.return_value.first.return_value = sample_user
        
        # Call the method and expect ValueError
        with pytest.raises(ValueError, match="User with this email already exists"):
            user_service.create_user(sample_user_data, "tenant_123", "admin_123")
    
    def test_create_user_duplicate_username(self, user_service, sample_user_data, sample_user):
        """Test user creation with duplicate username."""
        # Mock no existing email but existing username
        def mock_query_side_effect():
            mock_query = Mock()
            mock_filter = Mock()
            mock_first = Mock()
            
            # First call (email check) returns None
            # Second call (username check) returns existing user
            mock_first.side_effect = [None, sample_user]
            mock_filter.first = mock_first
            mock_query.filter.return_value = mock_filter
            return mock_query
        
        user_service.db.query.side_effect = mock_query_side_effect
        
        # Call the method and expect ValueError
        with pytest.raises(ValueError, match="Username already taken"):
            user_service.create_user(sample_user_data, "tenant_123", "admin_123")
    
    def test_get_user_by_id_success(self, user_service, sample_user):
        """Test successful user retrieval by ID."""
        # Mock database query
        user_service.db.query.return_value.filter.return_value.first.return_value = sample_user
        
        # Call the method
        result = user_service.get_user_by_id("user_123", "tenant_123")
        
        # Assertions
        assert result == sample_user
        user_service.db.query.assert_called_once_with(User)
    
    def test_get_user_by_id_not_found(self, user_service):
        """Test user retrieval by ID when user not found."""
        # Mock database query returning None
        user_service.db.query.return_value.filter.return_value.first.return_value = None
        
        # Call the method
        result = user_service.get_user_by_id("user_123", "tenant_123")
        
        # Assertions
        assert result is None
    
    def test_get_user_by_email_success(self, user_service, sample_user):
        """Test successful user retrieval by email."""
        # Mock database query
        user_service.db.query.return_value.filter.return_value.first.return_value = sample_user
        
        # Call the method
        result = user_service.get_user_by_email("test@example.com", "tenant_123")
        
        # Assertions
        assert result == sample_user
        user_service.db.query.assert_called_once_with(User)
    
    def test_get_user_by_username_success(self, user_service, sample_user):
        """Test successful user retrieval by username."""
        # Mock database query
        user_service.db.query.return_value.filter.return_value.first.return_value = sample_user
        
        # Call the method
        result = user_service.get_user_by_username("testuser", "tenant_123")
        
        # Assertions
        assert result == sample_user
        user_service.db.query.assert_called_once_with(User)
    
    def test_get_users_success(self, user_service, sample_user):
        """Test successful users retrieval."""
        # Mock database query
        user_service.db.query.return_value.filter.return_value.all.return_value = [sample_user]
        
        # Call the method
        result = user_service.get_users("tenant_123", limit=10, offset=0, active_only=True)
        
        # Assertions
        assert result == [sample_user]
        user_service.db.query.assert_called_once_with(User)
    
    def test_search_users_success(self, user_service, sample_user):
        """Test successful user search."""
        # Mock database query
        user_service.db.query.return_value.filter.return_value.filter.return_value.all.return_value = [sample_user]
        
        # Call the method
        result = user_service.search_users("tenant_123", "test", limit=10)
        
        # Assertions
        assert result == [sample_user]
        user_service.db.query.assert_called_once_with(User)
    
    def test_update_user_success(self, user_service, sample_user):
        """Test successful user update."""
        # Mock get_user_by_id to return user
        user_service.get_user_by_id.return_value = sample_user
        
        # Mock update data
        update_data = UserUpdateRequest(
            first_name="Updated",
            last_name="Name"
        )
        
        # Call the method
        result = user_service.update_user("user_123", "tenant_123", update_data, "admin_123")
        
        # Assertions
        assert result == sample_user
        user_service.update.assert_called_once()
        user_service.get_user_by_id.assert_called_once_with("user_123", "tenant_123")
    
    def test_update_user_not_found(self, user_service):
        """Test user update when user not found."""
        # Mock get_user_by_id to return None
        user_service.get_user_by_id.return_value = None
        
        # Mock update data
        update_data = UserUpdateRequest(first_name="Updated")
        
        # Call the method and expect ValueError
        with pytest.raises(ValueError, match="User not found"):
            user_service.update_user("user_123", "tenant_123", update_data, "admin_123")
    
    def test_activate_user_success(self, user_service, sample_user):
        """Test successful user activation."""
        # Mock get_user_by_id to return user
        user_service.get_user_by_id.return_value = sample_user
        
        # Call the method
        result = user_service.activate_user("user_123", "tenant_123", "admin_123")
        
        # Assertions
        assert result == sample_user
        assert sample_user.is_active is True
        user_service.get_user_by_id.assert_called_once_with("user_123", "tenant_123")
    
    def test_deactivate_user_success(self, user_service, sample_user):
        """Test successful user deactivation."""
        # Mock get_user_by_id to return user
        user_service.get_user_by_id.return_value = sample_user
        
        # Call the method
        result = user_service.deactivate_user("user_123", "tenant_123", "admin_123")
        
        # Assertions
        assert result == sample_user
        assert sample_user.is_active is False
        user_service.get_user_by_id.assert_called_once_with("user_123", "tenant_123")
    
    def test_delete_user_success(self, user_service, sample_user):
        """Test successful user deletion."""
        # Mock get_user_by_id to return user
        user_service.get_user_by_id.return_value = sample_user
        
        # Call the method
        user_service.delete_user("user_123", "tenant_123", "admin_123")
        
        # Assertions
        sample_user.soft_delete.assert_called_once_with("admin_123")
        user_service.get_user_by_id.assert_called_once_with("user_123", "tenant_123")
    
    def test_get_user_stats_success(self, user_service):
        """Test successful user statistics retrieval."""
        # Mock database queries
        def mock_count_side_effect():
            mock_query = Mock()
            mock_filter = Mock()
            mock_count = Mock()
            
            # Return different counts for different filter combinations
            mock_count.side_effect = [100, 80, 60, 5]  # total, active, verified, superusers
            mock_filter.count = mock_count
            mock_query.filter.return_value = mock_filter
            return mock_query
        
        user_service.db.query.side_effect = mock_count_side_effect
        
        # Call the method
        result = user_service.get_user_stats("tenant_123")
        
        # Assertions
        assert result['total_users'] == 100
        assert result['active_users'] == 80
        assert result['inactive_users'] == 20
        assert result['verified_users'] == 60
        assert result['unverified_users'] == 40
        assert result['superusers'] == 5
        assert result['regular_users'] == 95
    
    def test_bulk_update_users_success(self, user_service):
        """Test successful bulk user update."""
        # Mock database query
        user_service.db.query.return_value.filter.return_value.update.return_value = 3
        
        # Call the method
        result = user_service.bulk_update_users(
            ["user_1", "user_2", "user_3"], 
            "tenant_123", 
            {"is_active": True}, 
            "admin_123"
        )
        
        # Assertions
        assert result == 3
        user_service.db.query.assert_called()
    
    def test_user_service_context_manager(self, mock_db_session):
        """Test UserService as context manager."""
        with UserService(db_session=mock_db_session) as service:
            assert service.db == mock_db_session
            assert service._session_owner is False
        
        # Should not close the session since we don't own it
        mock_db_session.close.assert_not_called()
    
    def test_user_service_without_db_session(self):
        """Test UserService without provided database session."""
        with patch('app.services.user_service.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            
            with UserService() as service:
                assert service.db == mock_session
                assert service._session_owner is True
            
            # Should close the session since we own it
            mock_session.close.assert_called_once()
