"""
Authentication router for TheTally backend.

This module provides FastAPI endpoints for user authentication including
registration, login, 2FA setup, JWT token management, and password operations.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import structlog

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse,
    TwoFactorSetupRequest, TwoFactorSetupResponse, TwoFactorVerifyRequest,
    TwoFactorVerifyResponse, RefreshTokenRequest, PasswordResetRequest,
    PasswordResetConfirmRequest, ErrorResponse, SuccessResponse
)
from app.services.auth import AuthService
from app.utils.security import SecurityUtils
from app.core.config import settings

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme
security = HTTPBearer()

# Get logger
logger = structlog.get_logger(__name__)


def get_current_tenant_id(request: Request) -> str:
    """
    Extract tenant ID from request headers or use default.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Tenant ID string
    """
    # For now, use a default tenant ID
    # In a real multi-tenant system, this would be extracted from headers or JWT
    return request.headers.get("X-Tenant-ID", "default-tenant")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
) -> Optional[dict]:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        tenant_id: Current tenant ID
        
    Returns:
        User information if authenticated, None otherwise
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Verify JWT token
        payload = SecurityUtils.verify_jwt_token(credentials.credentials)
        
        if not payload or payload.get("token_type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = AuthService.get_current_user(db, user_id, tenant_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "id": str(user.id),
            "email": user.email,
            "tenant_id": user.tenant_id,
            "is_superuser": user.is_superuser
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user with the system.
    
    This endpoint creates a new user account and returns JWT tokens for immediate authentication.
    """
    try:
        tenant_id = get_current_tenant_id(request)
        
        # Register user
        user, access_token, refresh_token = AuthService.register_user(
            db, user_data, tenant_id
        )
        
        # Calculate token expiration times
        access_expires_in = SecurityUtils.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        refresh_expires_in = SecurityUtils.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        
        logger.info("User registration successful", 
                   user_id=str(user.id),
                   email=user_data.email[:3] + "***",
                   tenant_id=tenant_id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=access_expires_in,
            refresh_expires_in=refresh_expires_in
        )
        
    except ValueError as e:
        logger.warning("User registration failed", 
                      error=str(e),
                      email=user_data.email[:3] + "***")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("User registration failed", 
                    error=str(e),
                    email=user_data.email[:3] + "***")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return JWT tokens.
    
    This endpoint validates user credentials and returns access and refresh tokens.
    """
    try:
        tenant_id = get_current_tenant_id(request)
        
        # Authenticate user
        user, access_token, refresh_token = AuthService.authenticate_user(
            db, login_data, tenant_id
        )
        
        # Calculate token expiration times
        access_expires_in = SecurityUtils.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        refresh_expires_in = SecurityUtils.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        
        logger.info("User login successful", 
                   user_id=str(user.id),
                   email=login_data.email[:3] + "***",
                   tenant_id=tenant_id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=access_expires_in,
            refresh_expires_in=refresh_expires_in
        )
        
    except ValueError as e:
        logger.warning("User login failed", 
                      error=str(e),
                      email=login_data.email[:3] + "***")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error("User login failed", 
                    error=str(e),
                    email=login_data.email[:3] + "***")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh JWT tokens using a valid refresh token.
    
    This endpoint generates new access and refresh tokens using a valid refresh token.
    """
    try:
        tenant_id = get_current_tenant_id(request)
        
        # Refresh tokens
        user, access_token, refresh_token = AuthService.refresh_tokens(
            db, refresh_data.refresh_token, tenant_id
        )
        
        # Calculate token expiration times
        access_expires_in = SecurityUtils.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        refresh_expires_in = SecurityUtils.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        
        logger.info("Tokens refreshed successfully", 
                   user_id=str(user.id),
                   tenant_id=tenant_id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=access_expires_in,
            refresh_expires_in=refresh_expires_in
        )
        
    except ValueError as e:
        logger.warning("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user information.
    
    This endpoint returns the current authenticated user's profile information.
    """
    try:
        user = db.query(User).filter(User.id == current_user["id"]).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            totp_enabled=user.totp_enabled,
            timezone=user.timezone,
            language=user.language,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get current user info", 
                    error=str(e),
                    user_id=current_user.get("id"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(
    setup_data: TwoFactorSetupRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Setup 2FA for the current user.
    
    This endpoint generates a TOTP secret and QR code for 2FA setup.
    """
    try:
        user = db.query(User).filter(User.id == current_user["id"]).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Setup 2FA
        result = AuthService.setup_2fa(db, user, setup_data)
        
        logger.info("2FA setup initiated", 
                   user_id=str(user.id),
                   email=user.email[:3] + "***")
        
        return TwoFactorSetupResponse(
            secret=result["secret"],
            qr_code_url=result["qr_code_url"],
            backup_codes=result["backup_codes"]
        )
        
    except ValueError as e:
        logger.warning("2FA setup failed", 
                      error=str(e),
                      user_id=current_user.get("id"))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("2FA setup failed", 
                    error=str(e),
                    user_id=current_user.get("id"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="2FA setup failed"
        )


@router.post("/2fa/verify", response_model=TwoFactorVerifyResponse)
async def verify_2fa(
    verify_data: TwoFactorVerifyRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify 2FA code and enable 2FA.
    
    This endpoint verifies the TOTP code and enables 2FA for the user.
    """
    try:
        user = db.query(User).filter(User.id == current_user["id"]).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify 2FA
        success = AuthService.verify_2fa(db, user, verify_data)
        
        if success:
            logger.info("2FA verified and enabled", 
                       user_id=str(user.id),
                       email=user.email[:3] + "***")
            return TwoFactorVerifyResponse(
                success=True,
                message="2FA has been successfully enabled"
            )
        else:
            logger.warning("2FA verification failed", 
                          user_id=str(user.id),
                          email=user.email[:3] + "***")
            return TwoFactorVerifyResponse(
                success=False,
                message="Invalid 2FA code"
            )
        
    except Exception as e:
        logger.error("2FA verification failed", 
                    error=str(e),
                    user_id=current_user.get("id"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="2FA verification failed"
        )


@router.post("/logout", response_model=SuccessResponse)
async def logout_user(
    current_user: dict = Depends(get_current_user)
):
    """
    Logout the current user.
    
    This endpoint logs the user out (client should discard tokens).
    """
    try:
        logger.info("User logged out", 
                   user_id=current_user.get("id"),
                   email=current_user.get("email", "")[:3] + "***")
        
        return SuccessResponse(
            message="Successfully logged out"
        )
        
    except Exception as e:
        logger.error("Logout failed", 
                    error=str(e),
                    user_id=current_user.get("id"))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
