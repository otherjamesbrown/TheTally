"""
Authentication schemas for TheTally backend.

This module contains Pydantic schemas for user authentication requests and responses,
including registration, login, 2FA setup, and JWT token handling.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    first_name: Optional[str] = Field(None, max_length=100, description="User first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User last name")
    username: Optional[str] = Field(None, max_length=50, description="Username")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    timezone: str = Field(default="UTC", max_length=50, description="User timezone")
    language: str = Field(default="en", max_length=10, description="User language preference")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if not v:
            raise ValueError('Password cannot be empty')
        
        # Check minimum length
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for required character types
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[@$!%*?&]', v):
            raise ValueError('Password must contain at least one special character (@$!%*?&)')
        
        # Check for common weak patterns
        weak_patterns = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if v.lower() in weak_patterns:
            raise ValueError('Password is too common and not allowed')
        
        # Check for repeated characters
        if len(set(v)) < 4:
            raise ValueError('Password must contain at least 4 different characters')
        
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if v is None:
            return v
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if v is None:
            return v
        
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', v)
        
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 10 and 15 digits')
        
        return v


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(default=False, description="Whether to extend session duration")


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    refresh_expires_in: int = Field(..., description="Refresh token expiration time in seconds")


class UserResponse(BaseModel):
    """Schema for user information response."""
    
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    username: Optional[str] = Field(None, description="Username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    full_name: str = Field(..., description="Full name")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether user is verified")
    is_superuser: bool = Field(..., description="Whether user is superuser")
    totp_enabled: bool = Field(..., description="Whether 2FA is enabled")
    timezone: str = Field(..., description="User timezone")
    language: str = Field(..., description="User language")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class TwoFactorSetupRequest(BaseModel):
    """Schema for 2FA setup request."""
    
    password: str = Field(..., description="Current password for verification")


class TwoFactorSetupResponse(BaseModel):
    """Schema for 2FA setup response."""
    
    secret: str = Field(..., description="TOTP secret for authenticator app")
    qr_code_url: str = Field(..., description="QR code URL for easy setup")
    backup_codes: list[str] = Field(..., description="Backup codes for account recovery")


class TwoFactorVerifyRequest(BaseModel):
    """Schema for 2FA verification request."""
    
    code: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")
    
    @validator('code')
    def validate_code(cls, v):
        """Validate TOTP code format."""
        if not v.isdigit():
            raise ValueError('TOTP code must contain only digits')
        return v


class TwoFactorVerifyResponse(BaseModel):
    """Schema for 2FA verification response."""
    
    success: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Response message")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    
    refresh_token: str = Field(..., description="JWT refresh token")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirmRequest(BaseModel):
    """Schema for password reset confirmation."""
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if not v:
            raise ValueError('Password cannot be empty')
        
        # Check minimum length
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for required character types
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[@$!%*?&]', v):
            raise ValueError('Password must contain at least one special character (@$!%*?&)')
        
        # Check for common weak patterns
        weak_patterns = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if v.lower() in weak_patterns:
            raise ValueError('Password is too common and not allowed')
        
        # Check for repeated characters
        if len(set(v)) < 4:
            raise ValueError('Password must contain at least 4 different characters')
        
        return v


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class SuccessResponse(BaseModel):
    """Schema for success responses."""
    
    success: bool = Field(default=True, description="Success status")
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Additional data")
