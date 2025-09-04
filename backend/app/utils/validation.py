"""
Validation utilities for TheTally backend.

This module provides comprehensive input validation and sanitization utilities
following security-first principles.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from pydantic import BaseModel, ValidationError
import structlog
from app.utils.logging import get_audit_logger

logger = get_audit_logger("validation")


class ValidationUtils:
    """
    Validation utilities class providing comprehensive input validation.
    """
    
    # Common regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{10,20}$')
    CURRENCY_PATTERN = re.compile(r'^[A-Z]{3}$')
    
    # Field length limits
    MAX_STRING_LENGTH = 1000
    MAX_EMAIL_LENGTH = 254
    MAX_PASSWORD_LENGTH = 128
    MIN_PASSWORD_LENGTH = 8
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format and security."""
        if not email or not isinstance(email, str):
            return False
        
        if len(email) > cls.MAX_EMAIL_LENGTH:
            return False
        
        return bool(cls.EMAIL_PATTERN.match(email))
    
    @classmethod
    def validate_password(cls, password: str) -> tuple[bool, List[str]]:
        """
        Validate password strength.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not password:
            errors.append("Password is required")
            return False, errors
        
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters")
        
        if len(password) > cls.MAX_PASSWORD_LENGTH:
            errors.append(f"Password must be no more than {cls.MAX_PASSWORD_LENGTH} characters")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[@$!%*?&]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_amount(cls, amount: Union[str, int, float, Decimal]) -> tuple[bool, Optional[Decimal]]:
        """
        Validate monetary amount.
        
        Returns:
            Tuple of (is_valid, decimal_amount)
        """
        try:
            if isinstance(amount, str):
                # Remove currency symbols and whitespace
                cleaned = re.sub(r'[^\d.,\-]', '', amount)
                decimal_amount = Decimal(cleaned)
            else:
                decimal_amount = Decimal(str(amount))
            
            # Check reasonable bounds
            if decimal_amount < Decimal('-999999999.99') or decimal_amount > Decimal('999999999.99'):
                return False, None
            
            return True, decimal_amount
        except (InvalidOperation, ValueError):
            return False, None
    
    @classmethod
    def sanitize_string(cls, input_string: str, max_length: int = MAX_STRING_LENGTH) -> str:
        """Sanitize string input to prevent injection attacks."""
        if not input_string or not isinstance(input_string, str):
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', input_string)
        
        # Limit length
        sanitized = sanitized[:max_length]
        
        # Strip whitespace
        return sanitized.strip()
    
    @classmethod
    def validate_tenant_id(cls, tenant_id: str) -> bool:
        """Validate tenant ID format."""
        if not tenant_id or not isinstance(tenant_id, str):
            return False
        
        # Tenant ID should be alphanumeric with underscores
        return bool(re.match(r'^[a-zA-Z0-9_]{1,50}$', tenant_id))
    
    @classmethod
    def validate_transaction_data(cls, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate transaction data structure."""
        errors = []
        
        # Required fields
        required_fields = ['amount', 'description', 'account_id', 'tenant_id']
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate amount
        if 'amount' in data:
            is_valid, _ = cls.validate_amount(data['amount'])
            if not is_valid:
                errors.append("Invalid amount format")
        
        # Validate description
        if 'description' in data:
            if not isinstance(data['description'], str) or len(data['description']) > 500:
                errors.append("Description must be a string with max 500 characters")
        
        return len(errors) == 0, errors
