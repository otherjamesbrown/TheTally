"""
User model for TheTally backend.

This module contains the User model with authentication and multi-tenant support.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import BaseModel


class User(BaseModel):
    """
    User model for authentication and multi-tenant support.
    
    This model represents users in the system with support for:
    - Multi-tenant architecture
    - Authentication fields
    - 2FA support
    - Audit trail
    """
    
    __tablename__ = "users"
    
    # User identification
    email = Column(String(254), nullable=False, unique=True, index=True)
    username = Column(String(50), nullable=True, unique=True, index=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # 2FA support
    totp_secret = Column(String(32), nullable=True)
    totp_enabled = Column(Boolean, default=False, nullable=False)
    
    # User profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    # Security
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(String(10), default="0", nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Email verification
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Preferences
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    
    # Additional metadata
    notes = Column(Text, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_users_tenant_email', 'tenant_id', 'email'),
        Index('idx_users_tenant_active', 'tenant_id', 'is_active'),
        Index('idx_users_last_login', 'last_login'),
    )
    
    def __repr__(self) -> str:
        """String representation of the User."""
        return f"<User(id={self.id}, email={self.email}, tenant_id={self.tenant_id})>"
    
    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email.split('@')[0]
    
    @property
    def is_locked(self) -> bool:
        """Check if the user account is locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def lock_account(self, duration_minutes: int = 30) -> None:
        """
        Lock the user account for the specified duration.
        
        Args:
            duration_minutes: Duration to lock the account in minutes
        """
        from datetime import timedelta
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def unlock_account(self) -> None:
        """Unlock the user account."""
        self.locked_until = None
        self.failed_login_attempts = "0"
    
    def increment_failed_login(self) -> None:
        """Increment the failed login attempts counter."""
        try:
            current_attempts = int(self.failed_login_attempts)
            self.failed_login_attempts = str(current_attempts + 1)
        except (ValueError, TypeError):
            self.failed_login_attempts = "1"
    
    def reset_failed_login(self) -> None:
        """Reset the failed login attempts counter."""
        self.failed_login_attempts = "0"
    
    def to_dict(self, exclude_sensitive: bool = True) -> dict:
        """
        Convert user to dictionary, optionally excluding sensitive fields.
        
        Args:
            exclude_sensitive: Whether to exclude sensitive fields like password_hash
            
        Returns:
            Dictionary representation of the user
        """
        exclude_fields = ['password_hash', 'totp_secret', 'password_reset_token', 'email_verification_token']
        if exclude_sensitive:
            return self.to_dict(exclude_fields=exclude_fields)
        else:
            return self.to_dict(exclude_fields=[])
