"""
Security utilities for TheTally backend.

This module provides security-related utilities including password hashing,
JWT token handling, input validation, and security logging.
"""

import re
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from passlib.context import CryptContext
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
import structlog
from app.core.config import settings

# Configure password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Get logger
logger = structlog.get_logger(__name__)


class SecurityUtils:
    """
    Security utilities class providing secure password handling, JWT operations,
    and input validation with comprehensive audit logging.
    """
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    PASSWORD_PATTERN = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'
    )
    
    # JWT settings
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash a password using bcrypt with 12 rounds.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        # Validate password strength
        cls._validate_password_strength(password)
        
        try:
            hashed = pwd_context.hash(password)
            logger.info("Password hashed successfully", 
                       password_length=len(password),
                       hash_algorithm="bcrypt")
            return hashed
        except Exception as e:
            logger.error("Password hashing failed", error=str(e))
            raise
    
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            is_valid = pwd_context.verify(plain_password, hashed_password)
            logger.info("Password verification completed", 
                       is_valid=is_valid,
                       password_length=len(plain_password))
            return is_valid
        except Exception as e:
            logger.error("Password verification failed", error=str(e))
            return False
    
    @classmethod
    def generate_jwt_token(cls, user_id: str, tenant_id: str, 
                          token_type: str = "access") -> str:
        """
        Generate a JWT token for user authentication.
        
        Args:
            user_id: User ID to include in token
            tenant_id: Tenant ID to include in token
            token_type: Type of token ("access" or "refresh")
            
        Returns:
            JWT token string
        """
        try:
            # Set expiration based on token type
            if token_type == "access":
                expire_minutes = cls.ACCESS_TOKEN_EXPIRE_MINUTES
                expire_delta = timedelta(minutes=expire_minutes)
            else:  # refresh
                expire_days = cls.REFRESH_TOKEN_EXPIRE_DAYS
                expire_delta = timedelta(days=expire_days)
            
            expire = datetime.utcnow() + expire_delta
            
            # Create token payload
            payload = {
                "sub": user_id,
                "tenant_id": tenant_id,
                "token_type": token_type,
                "exp": expire,
                "iat": datetime.utcnow(),
                "jti": secrets.token_urlsafe(32)  # Unique token ID
            }
            
            # Generate token
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm=cls.ALGORITHM)
            
            logger.info("JWT token generated", 
                       user_id=user_id,
                       tenant_id=tenant_id,
                       token_type=token_type,
                       expires_at=expire.isoformat())
            
            return token
        except Exception as e:
            logger.error("JWT token generation failed", 
                        user_id=user_id,
                        tenant_id=tenant_id,
                        error=str(e))
            raise
    
    @classmethod
    def verify_jwt_token(cls, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string to verify
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[cls.ALGORITHM])
            
            logger.info("JWT token verified successfully", 
                       user_id=payload.get("sub"),
                       tenant_id=payload.get("tenant_id"),
                       token_type=payload.get("token_type"))
            
            return payload
        except ExpiredSignatureError:
            logger.warning("JWT token expired", token=token[:20] + "...")
            return None
        except JWTClaimsError as e:
            logger.warning("JWT token claims invalid", error=str(e))
            return None
        except JWTError as e:
            logger.error("JWT token verification failed", error=str(e))
            return None
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """
        Validate email address format and security.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email is valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        # Basic email regex (RFC 5322 compliant)
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        is_valid = bool(email_pattern.match(email)) and len(email) <= 254
        
        logger.debug("Email validation completed", 
                    email=email[:3] + "***",  # Mask email for privacy
                    is_valid=is_valid)
        
        return is_valid
    
    @classmethod
    def sanitize_input(cls, input_string: str, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            input_string: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not input_string or not isinstance(input_string, str):
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', input_string)
        
        # Limit length
        sanitized = sanitized[:max_length]
        
        # Strip whitespace
        sanitized = sanitized.strip()
        
        logger.debug("Input sanitized", 
                    original_length=len(input_string),
                    sanitized_length=len(sanitized))
        
        return sanitized
    
    @classmethod
    def generate_secure_random_string(cls, length: int = 32) -> str:
        """
        Generate a cryptographically secure random string.
        
        Args:
            length: Length of the string to generate
            
        Returns:
            Secure random string
        """
        try:
            random_string = secrets.token_urlsafe(length)
            logger.debug("Secure random string generated", length=length)
            return random_string
        except Exception as e:
            logger.error("Secure random string generation failed", error=str(e))
            raise
    
    @classmethod
    def generate_2fa_secret(cls) -> str:
        """
        Generate a TOTP secret for 2FA.
        
        Returns:
            Base32 encoded secret for TOTP
        """
        try:
            secret = secrets.token_urlsafe(20)  # 160 bits
            logger.info("2FA secret generated")
            return secret
        except Exception as e:
            logger.error("2FA secret generation failed", error=str(e))
            raise
    
    @classmethod
    def _validate_password_strength(cls, password: str) -> None:
        """
        Validate password strength requirements.
        
        Args:
            password: Password to validate
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {cls.MIN_PASSWORD_LENGTH} characters long")
        
        if len(password) > cls.MAX_PASSWORD_LENGTH:
            raise ValueError(f"Password must be no more than {cls.MAX_PASSWORD_LENGTH} characters long")
        
        if not cls.PASSWORD_PATTERN.match(password):
            raise ValueError(
                "Password must contain at least one lowercase letter, "
                "one uppercase letter, one digit, and one special character"
            )
        
        # Check for common weak patterns
        if password.lower() in ['password', '123456', 'qwerty', 'admin']:
            raise ValueError("Password is too common and not allowed")
        
        # Check for repeated characters
        if len(set(password)) < 4:
            raise ValueError("Password must contain at least 4 different characters")
    
    @classmethod
    def hash_sensitive_data(cls, data: str) -> str:
        """
        Hash sensitive data for logging purposes.
        
        Args:
            data: Sensitive data to hash
            
        Returns:
            Hashed representation of the data
        """
        if not data:
            return ""
        
        # Use HMAC with a secret key for consistent hashing
        hashed = hmac.new(
            settings.SECRET_KEY.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"hash:{hashed[:16]}"  # Return first 16 chars for brevity
