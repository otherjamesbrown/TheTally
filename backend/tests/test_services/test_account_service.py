"""
Unit tests for AccountService.

This module contains comprehensive unit tests for the AccountService class,
testing all CRUD operations, balance management, and validation.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from decimal import Decimal

from app.services.account_service import AccountService
from app.models.account import Account


class TestAccountService:
    """Test cases for AccountService."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def account_service(self, mock_db_session):
        """Create an AccountService instance with mocked database session."""
        return AccountService(db_session=mock_db_session)
    
    @pytest.fixture
    def sample_account(self):
        """Create a sample account object."""
        account = Mock(spec=Account)
        account.id = 1
        account.name = "Test Account"
        account.account_type = "current"
        account.user_id = "user_123"
        account.tenant_id = "tenant_123"
        account.current_balance = Decimal('1000.00')
        account.available_balance = Decimal('1000.00')
        account.pending_balance = Decimal('0.00')
        account.currency = "USD"
        account.is_active = True
        account.is_archived = False
        return account
    
    def test_create_account_success(self, account_service, sample_account):
        """Test successful account creation."""
        # Mock create method
        account_service.create.return_value = sample_account
        
        # Call the method
        result = account_service.create_account(
            "Test Account", "current", "user_123", "tenant_123"
        )
        
        # Assertions
        assert result == sample_account
        account_service.create.assert_called_once()
    
    def test_create_account_invalid_type(self, account_service):
        """Test account creation with invalid account type."""
        # Call the method and expect ValueError
        with pytest.raises(ValueError, match="Invalid account type"):
            account_service.create_account(
                "Test Account", "invalid_type", "user_123", "tenant_123"
            )
    
    def test_get_account_by_id_success(self, account_service, sample_account):
        """Test successful account retrieval by ID."""
        # Mock database query
        account_service.db.query.return_value.filter.return_value.first.return_value = sample_account
        
        # Call the method
        result = account_service.get_account_by_id(1, "tenant_123")
        
        # Assertions
        assert result == sample_account
        account_service.db.query.assert_called_once_with(Account)
    
    def test_get_account_by_id_not_found(self, account_service):
        """Test account retrieval by ID when account not found."""
        # Mock database query returning None
        account_service.db.query.return_value.filter.return_value.first.return_value = None
        
        # Call the method
        result = account_service.get_account_by_id(1, "tenant_123")
        
        # Assertions
        assert result is None
    
    def test_get_accounts_by_user_success(self, account_service, sample_account):
        """Test successful accounts retrieval by user."""
        # Mock database query
        account_service.db.query.return_value.filter.return_value.all.return_value = [sample_account]
        
        # Call the method
        result = account_service.get_accounts_by_user("user_123", "tenant_123", active_only=True)
        
        # Assertions
        assert result == [sample_account]
        account_service.db.query.assert_called_once_with(Account)
    
    def test_get_accounts_by_type_success(self, account_service, sample_account):
        """Test successful accounts retrieval by type."""
        # Mock database query
        account_service.db.query.return_value.filter.return_value.all.return_value = [sample_account]
        
        # Call the method
        result = account_service.get_accounts_by_type("current", "tenant_123", active_only=True)
        
        # Assertions
        assert result == [sample_account]
        account_service.db.query.assert_called_once_with(Account)
    
    def test_search_accounts_success(self, account_service, sample_account):
        """Test successful account search."""
        # Mock database query
        account_service.db.query.return_value.filter.return_value.filter.return_value.all.return_value = [sample_account]
        
        # Call the method
        result = account_service.search_accounts("tenant_123", "test", limit=10)
        
        # Assertions
        assert result == [sample_account]
        account_service.db.query.assert_called_once_with(Account)
    
    def test_update_account_success(self, account_service, sample_account):
        """Test successful account update."""
        # Mock get_account_by_id to return account
        account_service.get_account_by_id.return_value = sample_account
        
        # Mock update data
        update_data = {"name": "Updated Account"}
        
        # Call the method
        result = account_service.update_account(1, "tenant_123", update_data, "admin_123")
        
        # Assertions
        assert result == sample_account
        account_service.update.assert_called_once()
        account_service.get_account_by_id.assert_called_once_with(1, "tenant_123")
    
    def test_update_account_not_found(self, account_service):
        """Test account update when account not found."""
        # Mock get_account_by_id to return None
        account_service.get_account_by_id.return_value = None
        
        # Mock update data
        update_data = {"name": "Updated Account"}
        
        # Call the method and expect ValueError
        with pytest.raises(ValueError, match="Account not found"):
            account_service.update_account(1, "tenant_123", update_data, "admin_123")
    
    def test_update_balance_success(self, account_service, sample_account):
        """Test successful balance update."""
        # Mock get_account_by_id to return account
        account_service.get_account_by_id.return_value = sample_account
        
        # Call the method
        result = account_service.update_balance(1, "tenant_123", Decimal('1500.00'), "current", "admin_123")
        
        # Assertions
        assert result == sample_account
        sample_account.update_balance.assert_called_once_with(Decimal('1500.00'), "current")
        account_service.get_account_by_id.assert_called_once_with(1, "tenant_123")
    
    def test_add_to_balance_success(self, account_service, sample_account):
        """Test successful balance addition."""
        # Mock get_account_by_id to return account
        account_service.get_account_by_id.return_value = sample_account
        
        # Call the method
        result = account_service.add_to_balance(1, "tenant_123", Decimal('500.00'), "current", "admin_123")
        
        # Assertions
        assert result == sample_account
        sample_account.add_to_balance.assert_called_once_with(Decimal('500.00'), "current")
        account_service.get_account_by_id.assert_called_once_with(1, "tenant_123")
    
    def test_archive_account_success(self, account_service, sample_account):
        """Test successful account archiving."""
        # Mock get_account_by_id to return account
        account_service.get_account_by_id.return_value = sample_account
        
        # Call the method
        result = account_service.archive_account(1, "tenant_123", "admin_123")
        
        # Assertions
        assert result == sample_account
        sample_account.archive.assert_called_once_with("admin_123")
        account_service.get_account_by_id.assert_called_once_with(1, "tenant_123")
    
    def test_unarchive_account_success(self, account_service, sample_account):
        """Test successful account unarchiving."""
        # Mock get_account_by_id to return account
        account_service.get_account_by_id.return_value = sample_account
        
        # Call the method
        result = account_service.unarchive_account(1, "tenant_123", "admin_123")
        
        # Assertions
        assert result == sample_account
        sample_account.unarchive.assert_called_once_with("admin_123")
        account_service.get_account_by_id.assert_called_once_with(1, "tenant_123")
    
    def test_delete_account_success(self, account_service, sample_account):
        """Test successful account deletion."""
        # Mock get_account_by_id to return account
        account_service.get_account_by_id.return_value = sample_account
        
        # Call the method
        account_service.delete_account(1, "tenant_123", "admin_123")
        
        # Assertions
        sample_account.soft_delete.assert_called_once_with("admin_123")
        account_service.get_account_by_id.assert_called_once_with(1, "tenant_123")
    
    def test_get_account_balance_success(self, account_service, sample_account):
        """Test successful balance retrieval."""
        # Mock get_account_by_id to return account
        account_service.get_account_by_id.return_value = sample_account
        sample_account.effective_balance = Decimal('1000.00')
        
        # Call the method
        result = account_service.get_account_balance(1, "tenant_123")
        
        # Assertions
        assert result == Decimal('1000.00')
        account_service.get_account_by_id.assert_called_once_with(1, "tenant_123")
    
    def test_validate_account_balance_success(self, account_service, sample_account):
        """Test successful balance validation."""
        # Mock get_account_by_id to return account
        account_service.get_account_by_id.return_value = sample_account
        sample_account.validate_balance_consistency.return_value = True
        
        # Call the method
        result = account_service.validate_account_balance(1, "tenant_123")
        
        # Assertions
        assert result is True
        sample_account.validate_balance_consistency.assert_called_once()
        account_service.get_account_by_id.assert_called_once_with(1, "tenant_123")
    
    def test_get_account_stats_success(self, account_service):
        """Test successful account statistics retrieval."""
        # Mock database queries
        def mock_count_side_effect():
            mock_query = Mock()
            mock_filter = Mock()
            mock_count = Mock()
            
            # Return different counts for different filter combinations
            mock_count.side_effect = [50, 40, 10]  # total, active, archived
            mock_filter.count = mock_count
            mock_query.filter.return_value = mock_filter
            return mock_query
        
        account_service.db.query.side_effect = mock_count_side_effect
        
        # Mock active accounts query for balance calculation
        mock_account = Mock()
        mock_account.effective_balance = Decimal('1000.00')
        account_service.db.query.return_value.filter.return_value.all.return_value = [mock_account]
        
        # Call the method
        result = account_service.get_account_stats("tenant_123")
        
        # Assertions
        assert result['total_accounts'] == 50
        assert result['active_accounts'] == 40
        assert result['archived_accounts'] == 10
        assert 'total_balance' in result
        assert 'type_breakdown' in result
    
    def test_account_service_context_manager(self, mock_db_session):
        """Test AccountService as context manager."""
        with AccountService(db_session=mock_db_session) as service:
            assert service.db == mock_db_session
            assert service._session_owner is False
        
        # Should not close the session since we don't own it
        mock_db_session.close.assert_not_called()
    
    def test_account_service_without_db_session(self):
        """Test AccountService without provided database session."""
        with patch('app.services.account_service.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            
            with AccountService() as service:
                assert service.db == mock_session
                assert service._session_owner is True
            
            # Should close the session since we own it
            mock_session.close.assert_called_once()
