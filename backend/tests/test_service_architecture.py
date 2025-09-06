"""
Test suite for service layer architecture.

This module tests the service layer architecture including base service,
security utilities, logging utilities, and validation utilities.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from decimal import Decimal
from app.services.base import BaseService
from app.utils.security import SecurityUtils
from app.utils.validation import ValidationUtils
from app.utils.logging import LoggingUtils


class TestBaseService:
    """Test cases for BaseService class."""
    
    def test_base_service_initialization(self):
        """Test BaseService initialization."""
        service = BaseService()
        assert service._db_session is None
        assert service._session_owner is True
        assert service.logger is not None
    
    def test_base_service_with_session(self):
        """Test BaseService with provided session."""
        mock_session = Mock()
        service = BaseService(db_session=mock_session)
        assert service._db_session == mock_session
        assert service._session_owner is False
    
    def test_context_manager(self):
        """Test BaseService as context manager."""
        with BaseService() as service:
            assert service is not None
        # Session should be closed after context exit
        assert service._db_session is None


class TestSecurityUtils:
    """Test cases for SecurityUtils class."""
    
    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = "TestPassword123!"  # nosec B105
        hashed = SecurityUtils.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert SecurityUtils.verify_password(password, hashed)
        assert not SecurityUtils.verify_password("wrong_password", hashed)
    
    def test_password_validation(self):
        """Test password strength validation."""
        # Valid password
        valid_password = "TestPassword123!"  # nosec B105
        SecurityUtils._validate_password_strength(valid_password)
        
        # Invalid passwords
        with pytest.raises(ValueError):
            SecurityUtils._validate_password_strength("")
        
        with pytest.raises(ValueError):
            SecurityUtils._validate_password_strength("short")
        
        with pytest.raises(ValueError):
            SecurityUtils._validate_password_strength("nouppercase123!")
        
        with pytest.raises(ValueError):
            SecurityUtils._validate_password_strength("NOLOWERCASE123!")
    
    def test_email_validation(self):
        """Test email validation."""
        assert SecurityUtils.validate_email("test@example.com")
        assert SecurityUtils.validate_email("user.name+tag@domain.co.uk")
        assert not SecurityUtils.validate_email("invalid-email")
        assert not SecurityUtils.validate_email("")
        assert not SecurityUtils.validate_email(None)
    
    def test_input_sanitization(self):
        """Test input sanitization."""
        malicious_input = "test\x00string\x1fwith\x7fcontrol"
        sanitized = SecurityUtils.sanitize_input(malicious_input)
        assert sanitized == "teststringwithcontrol"
        
        # Test length limiting
        long_input = "a" * 2000
        sanitized = SecurityUtils.sanitize_input(long_input, max_length=100)
        assert len(sanitized) == 100
    
    def test_secure_random_string(self):
        """Test secure random string generation."""
        random_string = SecurityUtils.generate_secure_random_string(32)
        # token_urlsafe returns base64 encoded string which is longer than input
        assert len(random_string) >= 32
        assert isinstance(random_string, str)
        
        # Should be different each time
        another_string = SecurityUtils.generate_secure_random_string(32)
        assert random_string != another_string


class TestValidationUtils:
    """Test cases for ValidationUtils class."""
    
    def test_email_validation(self):
        """Test email validation."""
        assert ValidationUtils.validate_email("test@example.com")
        assert ValidationUtils.validate_email("user.name@domain.co.uk")
        assert not ValidationUtils.validate_email("invalid-email")
        assert not ValidationUtils.validate_email("")
        assert not ValidationUtils.validate_email(None)
    
    def test_password_validation(self):
        """Test password validation."""
        # Valid password
        is_valid, errors = ValidationUtils.validate_password("TestPassword123!")
        assert is_valid
        assert len(errors) == 0
        
        # Invalid passwords
        is_valid, errors = ValidationUtils.validate_password("short")
        assert not is_valid
        assert len(errors) > 0
        
        is_valid, errors = ValidationUtils.validate_password("nouppercase123!")
        assert not is_valid
        assert "uppercase" in errors[0]
    
    def test_amount_validation(self):
        """Test monetary amount validation."""
        # Valid amounts
        is_valid, amount = ValidationUtils.validate_amount("123.45")
        assert is_valid
        assert amount == Decimal("123.45")
        
        is_valid, amount = ValidationUtils.validate_amount(100.50)
        assert is_valid
        assert amount == Decimal("100.50")
        
        # Invalid amounts
        is_valid, amount = ValidationUtils.validate_amount("invalid")
        assert not is_valid
        assert amount is None
        
        is_valid, amount = ValidationUtils.validate_amount("")
        assert not is_valid
        assert amount is None
    
    def test_string_sanitization(self):
        """Test string sanitization."""
        malicious_input = "test\x00string\x1fwith\x7fcontrol"
        sanitized = ValidationUtils.sanitize_string(malicious_input)
        assert sanitized == "teststringwithcontrol"
        
        # Test length limiting
        long_input = "a" * 2000
        sanitized = ValidationUtils.sanitize_string(long_input, max_length=100)
        assert len(sanitized) == 100
    
    def test_tenant_id_validation(self):
        """Test tenant ID validation."""
        assert ValidationUtils.validate_tenant_id("tenant_123")
        assert ValidationUtils.validate_tenant_id("user_abc_123")
        assert not ValidationUtils.validate_tenant_id("invalid-tenant")
        assert not ValidationUtils.validate_tenant_id("")
        assert not ValidationUtils.validate_tenant_id(None)
    
    def test_transaction_data_validation(self):
        """Test transaction data validation."""
        # Valid transaction data
        valid_data = {
            "amount": "123.45",
            "description": "Test transaction",
            "account_id": "acc_123",
            "tenant_id": "tenant_123"
        }
        is_valid, errors = ValidationUtils.validate_transaction_data(valid_data)
        assert is_valid
        assert len(errors) == 0
        
        # Invalid transaction data
        invalid_data = {
            "amount": "invalid",
            "description": "Test transaction",
            "account_id": "acc_123"
            # Missing tenant_id
        }
        is_valid, errors = ValidationUtils.validate_transaction_data(invalid_data)
        assert not is_valid
        assert len(errors) > 0


class TestLoggingUtils:
    """Test cases for LoggingUtils class."""
    
    def test_logger_creation(self):
        """Test logger creation for different types."""
        audit_logger = LoggingUtils.get_audit_logger("test_audit")
        functional_logger = LoggingUtils.get_functional_logger("test_functional")
        debug_logger = LoggingUtils.get_debug_logger("test_debug")
        
        assert audit_logger is not None
        assert functional_logger is not None
        assert debug_logger is not None
    
    def test_security_event_logging(self):
        """Test security event logging."""
        with patch('app.utils.logging.structlog.get_logger') as mock_logger:
            LoggingUtils.log_security_event(
                event_type="login_attempt",
                user_id="user_123",
                tenant_id="tenant_456",
                ip_address="192.168.1.1"
            )
            mock_logger.return_value.bind.return_value.info.assert_called_once()
    
    def test_user_action_logging(self):
        """Test user action logging."""
        with patch('app.utils.logging.structlog.get_logger') as mock_logger:
            LoggingUtils.log_user_action(
                action="create_transaction",
                user_id="user_123",
                tenant_id="tenant_456",
                resource_type="transaction"
            )
            mock_logger.return_value.bind.return_value.info.assert_called_once()
    
    def test_ai_context_logging(self):
        """Test AI context logging."""
        with patch('app.utils.logging.structlog.get_logger') as mock_logger:
            LoggingUtils.log_ai_context(
                ai_action="code_generation",
                reasoning="User requested service layer implementation",
                token_usage=1500
            )
            mock_logger.return_value.bind.return_value.info.assert_called_once()
    
    def test_error_logging(self):
        """Test error logging."""
        with patch('app.utils.logging.structlog.get_logger') as mock_logger:
            test_error = ValueError("Test error")
            LoggingUtils.log_error(test_error, {"context": "test"})
            mock_logger.return_value.bind.return_value.error.assert_called_once()
    
    def test_performance_logging(self):
        """Test performance logging."""
        with patch('app.utils.logging.structlog.get_logger') as mock_logger:
            LoggingUtils.log_performance("test_operation", 150.5)
            mock_logger.return_value.bind.return_value.info.assert_called_once()


class TestServiceArchitectureIntegration:
    """Integration tests for service layer architecture."""
    
    def test_module_imports(self):
        """Test that all modules can be imported without errors."""
        from app.services import BaseService
        from app.models import BaseModel
        from app.utils import SecurityUtils, ValidationUtils, LoggingUtils
        
        assert BaseService is not None
        assert BaseModel is not None
        assert SecurityUtils is not None
        assert ValidationUtils is not None
        assert LoggingUtils is not None
    
    def test_security_integration(self):
        """Test security utilities integration."""
        # Test password flow
        password = "SecurePassword123!"  # nosec B105
        hashed = SecurityUtils.hash_password(password)
        assert SecurityUtils.verify_password(password, hashed)
        
        # Test email validation
        assert SecurityUtils.validate_email("test@example.com")
        
        # Test input sanitization
        sanitized = SecurityUtils.sanitize_input("test\x00input")
        assert sanitized == "testinput"
    
    def test_validation_integration(self):
        """Test validation utilities integration."""
        # Test transaction validation
        transaction_data = {
            "amount": "123.45",
            "description": "Test transaction",
            "account_id": "acc_123",
            "tenant_id": "tenant_123"
        }
        is_valid, errors = ValidationUtils.validate_transaction_data(transaction_data)
        assert is_valid
        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__])
