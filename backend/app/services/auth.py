"""
Authentication service for TheTally backend.

This module provides authentication services including user registration, login,
2FA setup, JWT token management, and password operations.
"""

import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import structlog

from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest, UserLoginRequest, TwoFactorSetupRequest,
    TwoFactorVerifyRequest, PasswordResetConfirmRequest
)
from app.utils.security import SecurityUtils
from app.core.config import settings

# Get logger
logger = structlog.get_logger(__name__)


class AuthService:
    """
    Authentication service providing user management and security operations.
    """
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegisterRequest, tenant_id: str) -> Tuple[User, str, str]:
        """
        Register a new user with the system.
        
        Args:
            db: Database session
            user_data: User registration data
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Tuple of (user, access_token, refresh_token)
            
        Raises:
            ValueError: If user already exists or validation fails
            Exception: If registration fails
        """
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(
                User.email == user_data.email,
                User.tenant_id == tenant_id
            ).first()
            
            if existing_user:
                logger.warning("User registration attempted with existing email", 
                             email=user_data.email[:3] + "***",
                             tenant_id=tenant_id)
                raise ValueError("User with this email already exists")
            
            # Check username uniqueness if provided
            if user_data.username:
                existing_username = db.query(User).filter(
                    User.username == user_data.username,
                    User.tenant_id == tenant_id
                ).first()
                
                if existing_username:
                    logger.warning("User registration attempted with existing username", 
                                 username=user_data.username,
                                 tenant_id=tenant_id)
                    raise ValueError("Username already taken")
            
            # Hash password
            password_hash = SecurityUtils.hash_password(user_data.password)
            
            # Create user
            user = User(
                email=user_data.email,
                username=user_data.username,
                password_hash=password_hash,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone_number=user_data.phone_number,
                timezone=user_data.timezone,
                language=user_data.language,
                tenant_id=tenant_id,
                is_active=True,
                is_verified=False,
                is_superuser=False
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Generate JWT tokens
            access_token = SecurityUtils.generate_jwt_token(
                str(user.id), tenant_id, "access"
            )
            refresh_token = SecurityUtils.generate_jwt_token(
                str(user.id), tenant_id, "refresh"
            )
            
            logger.info("User registered successfully", 
                       user_id=str(user.id),
                       email=user_data.email[:3] + "***",
                       tenant_id=tenant_id)
            
            return user, access_token, refresh_token
            
        except IntegrityError as e:
            db.rollback()
            logger.error("User registration failed due to database constraint", 
                        error=str(e),
                        email=user_data.email[:3] + "***")
            raise ValueError("User registration failed due to constraint violation")
        except Exception as e:
            db.rollback()
            logger.error("User registration failed", 
                        error=str(e),
                        email=user_data.email[:3] + "***")
            raise
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLoginRequest, tenant_id: str) -> Tuple[User, str, str]:
        """
        Authenticate a user and return JWT tokens.
        
        Args:
            db: Database session
            login_data: User login data
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Tuple of (user, access_token, refresh_token)
            
        Raises:
            ValueError: If authentication fails
        """
        try:
            # Find user by email
            user = db.query(User).filter(
                User.email == login_data.email,
                User.tenant_id == tenant_id
            ).first()
            
            if not user:
                logger.warning("Login attempt with non-existent email", 
                             email=login_data.email[:3] + "***",
                             tenant_id=tenant_id)
                raise ValueError("Invalid email or password")
            
            # Check if user is active
            if not user.is_active:
                logger.warning("Login attempt with inactive user", 
                             user_id=str(user.id),
                             email=login_data.email[:3] + "***")
                raise ValueError("Account is deactivated")
            
            # Check if account is locked
            if user.is_locked:
                logger.warning("Login attempt with locked account", 
                             user_id=str(user.id),
                             email=login_data.email[:3] + "***")
                raise ValueError("Account is temporarily locked")
            
            # Verify password
            if not SecurityUtils.verify_password(login_data.password, user.password_hash):
                # Increment failed login attempts
                user.increment_failed_login()
                
                # Lock account after 5 failed attempts
                if int(user.failed_login_attempts) >= 5:
                    user.lock_account(30)  # Lock for 30 minutes
                    logger.warning("Account locked due to too many failed login attempts", 
                                 user_id=str(user.id),
                                 failed_attempts=user.failed_login_attempts)
                
                db.commit()
                
                logger.warning("Login failed - invalid password", 
                             user_id=str(user.id),
                             email=login_data.email[:3] + "***")
                raise ValueError("Invalid email or password")
            
            # Reset failed login attempts on successful login
            user.reset_failed_login()
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Generate JWT tokens
            access_token = SecurityUtils.generate_jwt_token(
                str(user.id), tenant_id, "access"
            )
            refresh_token = SecurityUtils.generate_jwt_token(
                str(user.id), tenant_id, "refresh"
            )
            
            logger.info("User authenticated successfully", 
                       user_id=str(user.id),
                       email=login_data.email[:3] + "***",
                       tenant_id=tenant_id)
            
            return user, access_token, refresh_token
            
        except ValueError:
            raise
        except Exception as e:
            logger.error("User authentication failed", 
                        error=str(e),
                        email=login_data.email[:3] + "***")
            raise ValueError("Authentication failed")
    
    @staticmethod
    def setup_2fa(db: Session, user: User, setup_data: TwoFactorSetupRequest) -> Dict[str, Any]:
        """
        Setup 2FA for a user.
        
        Args:
            db: Database session
            user: User to setup 2FA for
            setup_data: 2FA setup data including password verification
            
        Returns:
            Dictionary containing secret, QR code URL, and backup codes
            
        Raises:
            ValueError: If password verification fails or setup fails
        """
        try:
            # Verify current password
            if not SecurityUtils.verify_password(setup_data.password, user.password_hash):
                logger.warning("2FA setup failed - invalid password", 
                             user_id=str(user.id))
                raise ValueError("Invalid password")
            
            # Generate TOTP secret
            totp_secret = SecurityUtils.generate_2fa_secret()
            
            # Create TOTP object
            totp = pyotp.TOTP(totp_secret)
            
            # Generate QR code URL
            qr_code_url = totp.provisioning_uri(
                name=user.email,
                issuer_name=settings.PROJECT_NAME
            )
            
            # Generate QR code as base64
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_code_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            qr_code_data_url = f"data:image/png;base64,{qr_code_base64}"
            
            # Generate backup codes
            backup_codes = [
                SecurityUtils.generate_secure_random_string(8).upper()
                for _ in range(10)
            ]
            
            # Update user with 2FA secret (but don't enable yet)
            user.totp_secret = totp_secret
            db.commit()
            
            logger.info("2FA setup initiated", 
                       user_id=str(user.id),
                       email=user.email[:3] + "***")
            
            return {
                "secret": totp_secret,
                "qr_code_url": qr_code_data_url,
                "backup_codes": backup_codes
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error("2FA setup failed", 
                        error=str(e),
                        user_id=str(user.id))
            raise ValueError("2FA setup failed")
    
    @staticmethod
    def verify_2fa(db: Session, user: User, verify_data: TwoFactorVerifyRequest) -> bool:
        """
        Verify 2FA code and enable 2FA if verification succeeds.
        
        Args:
            db: Database session
            user: User to verify 2FA for
            verify_data: 2FA verification data
            
        Returns:
            True if verification succeeds, False otherwise
        """
        try:
            if not user.totp_secret:
                logger.warning("2FA verification attempted without secret", 
                             user_id=str(user.id))
                return False
            
            # Create TOTP object
            totp = pyotp.TOTP(user.totp_secret)
            
            # Verify the code
            is_valid = totp.verify(verify_data.code, valid_window=1)
            
            if is_valid:
                # Enable 2FA
                user.totp_enabled = True
                db.commit()
                
                logger.info("2FA verified and enabled", 
                           user_id=str(user.id),
                           email=user.email[:3] + "***")
            else:
                logger.warning("2FA verification failed", 
                             user_id=str(user.id),
                             email=user.email[:3] + "***")
            
            return is_valid
            
        except Exception as e:
            logger.error("2FA verification failed", 
                        error=str(e),
                        user_id=str(user.id))
            return False
    
    @staticmethod
    def verify_2fa_login(db: Session, user: User, code: str) -> bool:
        """
        Verify 2FA code during login.
        
        Args:
            db: Database session
            user: User to verify 2FA for
            code: 2FA code to verify
            
        Returns:
            True if verification succeeds, False otherwise
        """
        try:
            if not user.totp_enabled or not user.totp_secret:
                return True  # 2FA not enabled, skip verification
            
            # Create TOTP object
            totp = pyotp.TOTP(user.totp_secret)
            
            # Verify the code
            is_valid = totp.verify(code, valid_window=1)
            
            if is_valid:
                logger.info("2FA login verification successful", 
                           user_id=str(user.id),
                           email=user.email[:3] + "***")
            else:
                logger.warning("2FA login verification failed", 
                             user_id=str(user.id),
                             email=user.email[:3] + "***")
            
            return is_valid
            
        except Exception as e:
            logger.error("2FA login verification failed", 
                        error=str(e),
                        user_id=str(user.id))
            return False
    
    @staticmethod
    def refresh_tokens(db: Session, refresh_token: str, tenant_id: str) -> Tuple[User, str, str]:
        """
        Refresh JWT tokens using a valid refresh token.
        
        Args:
            db: Database session
            refresh_token: Valid refresh token
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Tuple of (user, new_access_token, new_refresh_token)
            
        Raises:
            ValueError: If refresh token is invalid
        """
        try:
            # Verify refresh token
            payload = SecurityUtils.verify_jwt_token(refresh_token)
            
            if not payload or payload.get("token_type") != "refresh":
                logger.warning("Invalid refresh token provided")
                raise ValueError("Invalid refresh token")
            
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("Refresh token missing user ID")
                raise ValueError("Invalid refresh token")
            
            # Get user
            user = db.query(User).filter(
                User.id == user_id,
                User.tenant_id == tenant_id
            ).first()
            
            if not user or not user.is_active:
                logger.warning("Refresh token for non-existent or inactive user", 
                             user_id=user_id)
                raise ValueError("Invalid refresh token")
            
            # Generate new tokens
            access_token = SecurityUtils.generate_jwt_token(
                str(user.id), tenant_id, "access"
            )
            new_refresh_token = SecurityUtils.generate_jwt_token(
                str(user.id), tenant_id, "refresh"
            )
            
            logger.info("Tokens refreshed successfully", 
                       user_id=str(user.id),
                       tenant_id=tenant_id)
            
            return user, access_token, new_refresh_token
            
        except ValueError:
            raise
        except Exception as e:
            logger.error("Token refresh failed", 
                        error=str(e))
            raise ValueError("Token refresh failed")
    
    @staticmethod
    def get_current_user(db: Session, user_id: str, tenant_id: str) -> Optional[User]:
        """
        Get current user by ID and tenant.
        
        Args:
            db: Database session
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            User object if found and active, None otherwise
        """
        try:
            user = db.query(User).filter(
                User.id == user_id,
                User.tenant_id == tenant_id,
                User.is_active == True
            ).first()
            
            if user:
                logger.debug("Current user retrieved", 
                           user_id=str(user.id),
                           tenant_id=tenant_id)
            else:
                logger.warning("Current user not found or inactive", 
                             user_id=user_id,
                             tenant_id=tenant_id)
            
            return user
            
        except Exception as e:
            logger.error("Failed to get current user", 
                        error=str(e),
                        user_id=user_id,
                        tenant_id=tenant_id)
            return None
