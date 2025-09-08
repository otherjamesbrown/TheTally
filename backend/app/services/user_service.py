"""
User service for TheTally backend.

This module provides user management services including CRUD operations,
profile management, user search, and user status management.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import structlog
from datetime import datetime

from app.models.user import User
from app.services.base import BaseService
from app.schemas.auth import UserRegisterRequest, UserUpdateRequest

# Get logger
logger = structlog.get_logger(__name__)


class UserService(BaseService):
    """
    User service providing comprehensive user management operations.
    
    This service extends the base service with user-specific functionality:
    - User CRUD operations
    - Profile management
    - User search and filtering
    - User status management
    - Bulk operations
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the user service.
        
        Args:
            db_session: Optional database session. If not provided, a new session will be created.
        """
        super().__init__(db_session)
        self.logger = logger.bind(service="UserService")
    
    def create_user(self, user_data: UserRegisterRequest, tenant_id: str, created_by: str = None) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User registration data
            tenant_id: Tenant ID for multi-tenant support
            created_by: User ID who created this user
            
        Returns:
            Created user object
            
        Raises:
            ValueError: If user already exists or validation fails
            Exception: If user creation fails
        """
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(user_data.email, tenant_id)
            if existing_user:
                self.logger.warning("User creation attempted with existing email", 
                                 email=user_data.email[:3] + "***",
                                 tenant_id=tenant_id)
                raise ValueError("User with this email already exists")
            
            # Check username uniqueness if provided
            if user_data.username:
                existing_username = self.get_user_by_username(user_data.username, tenant_id)
                if existing_username:
                    self.logger.warning("User creation attempted with existing username", 
                                     username=user_data.username,
                                     tenant_id=tenant_id)
                    raise ValueError("Username already taken")
            
            # Create user
            user = self.create(User, 
                email=user_data.email,
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone_number=user_data.phone_number,
                timezone=user_data.timezone,
                language=user_data.language,
                tenant_id=tenant_id,
                created_by=created_by
            )
            
            self.logger.info("User created successfully", 
                           user_id=str(user.id),
                           email=user_data.email[:3] + "***",
                           tenant_id=tenant_id)
            
            return user
            
        except IntegrityError as e:
            self.logger.error("User creation failed due to database constraint", 
                            error=str(e),
                            email=user_data.email[:3] + "***")
            raise ValueError("User creation failed due to constraint violation")
        except Exception as e:
            self.logger.error("User creation failed", 
                            error=str(e),
                            email=user_data.email[:3] + "***")
            raise
    
    def get_user_by_id(self, user_id: str, tenant_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            User object if found, None otherwise
        """
        try:
            user = self.db.query(User).filter(
                User.id == user_id,
                User.tenant_id == tenant_id,
                User.is_deleted == False
            ).first()
            
            if user:
                self.logger.debug("User retrieved by ID", 
                               user_id=user_id,
                               tenant_id=tenant_id)
            else:
                self.logger.warning("User not found by ID", 
                                  user_id=user_id,
                                  tenant_id=tenant_id)
            
            return user
            
        except Exception as e:
            self.logger.error("Failed to get user by ID", 
                            error=str(e),
                            user_id=user_id,
                            tenant_id=tenant_id)
            raise
    
    def get_user_by_email(self, email: str, tenant_id: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            User object if found, None otherwise
        """
        try:
            user = self.db.query(User).filter(
                User.email == email,
                User.tenant_id == tenant_id,
                User.is_deleted == False
            ).first()
            
            if user:
                self.logger.debug("User retrieved by email", 
                               email=email[:3] + "***",
                               tenant_id=tenant_id)
            else:
                self.logger.warning("User not found by email", 
                                  email=email[:3] + "***",
                                  tenant_id=tenant_id)
            
            return user
            
        except Exception as e:
            self.logger.error("Failed to get user by email", 
                            error=str(e),
                            email=email[:3] + "***",
                            tenant_id=tenant_id)
            raise
    
    def get_user_by_username(self, username: str, tenant_id: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            User object if found, None otherwise
        """
        try:
            user = self.db.query(User).filter(
                User.username == username,
                User.tenant_id == tenant_id,
                User.is_deleted == False
            ).first()
            
            if user:
                self.logger.debug("User retrieved by username", 
                               username=username,
                               tenant_id=tenant_id)
            else:
                self.logger.warning("User not found by username", 
                                  username=username,
                                  tenant_id=tenant_id)
            
            return user
            
        except Exception as e:
            self.logger.error("Failed to get user by username", 
                            error=str(e),
                            username=username,
                            tenant_id=tenant_id)
            raise
    
    def get_users(self, tenant_id: str, limit: Optional[int] = None, 
                  offset: Optional[int] = None, active_only: bool = True) -> List[User]:
        """
        Get users for a tenant.
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            active_only: Whether to return only active users
            
        Returns:
            List of user objects
        """
        try:
            query = self.db.query(User).filter(
                User.tenant_id == tenant_id,
                User.is_deleted == False
            )
            
            if active_only:
                query = query.filter(User.is_active == True)
            
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            users = query.all()
            
            self.logger.debug("Users retrieved", 
                           tenant_id=tenant_id,
                           count=len(users),
                           active_only=active_only)
            
            return users
            
        except Exception as e:
            self.logger.error("Failed to get users", 
                            error=str(e),
                            tenant_id=tenant_id)
            raise
    
    def search_users(self, tenant_id: str, search_term: str, 
                    limit: Optional[int] = None) -> List[User]:
        """
        Search users by name, email, or username.
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            search_term: Search term
            limit: Optional limit on number of results
            
        Returns:
            List of matching user objects
        """
        try:
            query = self.db.query(User).filter(
                User.tenant_id == tenant_id,
                User.is_deleted == False,
                User.is_active == True
            ).filter(
                (User.first_name.ilike(f"%{search_term}%")) |
                (User.last_name.ilike(f"%{search_term}%")) |
                (User.email.ilike(f"%{search_term}%")) |
                (User.username.ilike(f"%{search_term}%"))
            )
            
            if limit:
                query = query.limit(limit)
            
            users = query.all()
            
            self.logger.debug("Users searched", 
                           tenant_id=tenant_id,
                           search_term=search_term[:10] + "***",
                           count=len(users))
            
            return users
            
        except Exception as e:
            self.logger.error("Failed to search users", 
                            error=str(e),
                            tenant_id=tenant_id,
                            search_term=search_term[:10] + "***")
            raise
    
    def update_user(self, user_id: str, tenant_id: str, 
                   user_data: UserUpdateRequest, updated_by: str = None) -> User:
        """
        Update user information.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID for multi-tenant support
            user_data: User update data
            updated_by: User ID who updated this user
            
        Returns:
            Updated user object
            
        Raises:
            ValueError: If user not found or validation fails
        """
        try:
            user = self.get_user_by_id(user_id, tenant_id)
            if not user:
                raise ValueError("User not found")
            
            # Check username uniqueness if provided
            if user_data.username and user_data.username != user.username:
                existing_username = self.get_user_by_username(user_data.username, tenant_id)
                if existing_username:
                    raise ValueError("Username already taken")
            
            # Update user fields
            update_fields = {}
            if user_data.first_name is not None:
                update_fields['first_name'] = user_data.first_name
            if user_data.last_name is not None:
                update_fields['last_name'] = user_data.last_name
            if user_data.username is not None:
                update_fields['username'] = user_data.username
            if user_data.phone_number is not None:
                update_fields['phone_number'] = user_data.phone_number
            if user_data.timezone is not None:
                update_fields['timezone'] = user_data.timezone
            if user_data.language is not None:
                update_fields['language'] = user_data.language
            
            if update_fields:
                self.update(user, **update_fields)
                if updated_by:
                    user.updated_by = updated_by
                user.update_audit_fields(updated_by)
            
            self.logger.info("User updated successfully", 
                           user_id=user_id,
                           tenant_id=tenant_id)
            
            return user
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to update user", 
                            error=str(e),
                            user_id=user_id,
                            tenant_id=tenant_id)
            raise
    
    def activate_user(self, user_id: str, tenant_id: str, updated_by: str = None) -> User:
        """
        Activate a user.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID for multi-tenant support
            updated_by: User ID who activated this user
            
        Returns:
            Updated user object
        """
        try:
            user = self.get_user_by_id(user_id, tenant_id)
            if not user:
                raise ValueError("User not found")
            
            user.is_active = True
            if updated_by:
                user.updated_by = updated_by
            user.update_audit_fields(updated_by)
            
            self.logger.info("User activated", 
                           user_id=user_id,
                           tenant_id=tenant_id)
            
            return user
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to activate user", 
                            error=str(e),
                            user_id=user_id,
                            tenant_id=tenant_id)
            raise
    
    def deactivate_user(self, user_id: str, tenant_id: str, updated_by: str = None) -> User:
        """
        Deactivate a user.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID for multi-tenant support
            updated_by: User ID who deactivated this user
            
        Returns:
            Updated user object
        """
        try:
            user = self.get_user_by_id(user_id, tenant_id)
            if not user:
                raise ValueError("User not found")
            
            user.is_active = False
            if updated_by:
                user.updated_by = updated_by
            user.update_audit_fields(updated_by)
            
            self.logger.info("User deactivated", 
                           user_id=user_id,
                           tenant_id=tenant_id)
            
            return user
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to deactivate user", 
                            error=str(e),
                            user_id=user_id,
                            tenant_id=tenant_id)
            raise
    
    def delete_user(self, user_id: str, tenant_id: str, deleted_by: str = None) -> None:
        """
        Soft delete a user.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID for multi-tenant support
            deleted_by: User ID who deleted this user
        """
        try:
            user = self.get_user_by_id(user_id, tenant_id)
            if not user:
                raise ValueError("User not found")
            
            user.soft_delete(deleted_by)
            
            self.logger.info("User deleted", 
                           user_id=user_id,
                           tenant_id=tenant_id)
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to delete user", 
                            error=str(e),
                            user_id=user_id,
                            tenant_id=tenant_id)
            raise
    
    def restore_user(self, user_id: str, tenant_id: str, restored_by: str = None) -> User:
        """
        Restore a soft-deleted user.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID for multi-tenant support
            restored_by: User ID who restored this user
            
        Returns:
            Restored user object
        """
        try:
            user = self.db.query(User).filter(
                User.id == user_id,
                User.tenant_id == tenant_id,
                User.is_deleted == True
            ).first()
            
            if not user:
                raise ValueError("Deleted user not found")
            
            user.restore(restored_by)
            
            self.logger.info("User restored", 
                           user_id=user_id,
                           tenant_id=tenant_id)
            
            return user
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to restore user", 
                            error=str(e),
                            user_id=user_id,
                            tenant_id=tenant_id)
            raise
    
    def get_user_stats(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get user statistics for a tenant.
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Dictionary with user statistics
        """
        try:
            total_users = self.db.query(User).filter(
                User.tenant_id == tenant_id,
                User.is_deleted == False
            ).count()
            
            active_users = self.db.query(User).filter(
                User.tenant_id == tenant_id,
                User.is_deleted == False,
                User.is_active == True
            ).count()
            
            verified_users = self.db.query(User).filter(
                User.tenant_id == tenant_id,
                User.is_deleted == False,
                User.is_verified == True
            ).count()
            
            superusers = self.db.query(User).filter(
                User.tenant_id == tenant_id,
                User.is_deleted == False,
                User.is_superuser == True
            ).count()
            
            stats = {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'verified_users': verified_users,
                'unverified_users': total_users - verified_users,
                'superusers': superusers,
                'regular_users': total_users - superusers
            }
            
            self.logger.debug("User stats retrieved", 
                           tenant_id=tenant_id,
                           stats=stats)
            
            return stats
            
        except Exception as e:
            self.logger.error("Failed to get user stats", 
                            error=str(e),
                            tenant_id=tenant_id)
            raise
    
    def bulk_update_users(self, user_ids: List[str], tenant_id: str, 
                         update_data: Dict[str, Any], updated_by: str = None) -> int:
        """
        Bulk update multiple users.
        
        Args:
            user_ids: List of user IDs to update
            tenant_id: Tenant ID for multi-tenant support
            update_data: Dictionary of fields to update
            updated_by: User ID who performed the update
            
        Returns:
            Number of users updated
        """
        try:
            updated_count = self.db.query(User).filter(
                User.id.in_(user_ids),
                User.tenant_id == tenant_id,
                User.is_deleted == False
            ).update(update_data, synchronize_session=False)
            
            if updated_by:
                # Update the updated_by field for all updated users
                self.db.query(User).filter(
                    User.id.in_(user_ids),
                    User.tenant_id == tenant_id,
                    User.is_deleted == False
                ).update({'updated_by': updated_by}, synchronize_session=False)
            
            self.logger.info("Users bulk updated", 
                           tenant_id=tenant_id,
                           user_count=len(user_ids),
                           updated_count=updated_count)
            
            return updated_count
            
        except Exception as e:
            self.logger.error("Failed to bulk update users", 
                            error=str(e),
                            tenant_id=tenant_id,
                            user_count=len(user_ids))
            raise
