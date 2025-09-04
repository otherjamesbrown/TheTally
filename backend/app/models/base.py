"""
Base model class for TheTally backend.

This module provides a base model class that all other models inherit from.
It includes common functionality like audit fields, tenant isolation,
soft delete support, and common validation methods.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql import func
import uuid

# Create the declarative base
Base = declarative_base()


class BaseModel(Base):
    """
    Base model class providing common functionality for all models.
    
    This class provides:
    - Primary key (id)
    - Tenant isolation (tenant_id)
    - Audit fields (created_at, updated_at)
    - Soft delete support (is_deleted, deleted_at)
    - Common utility methods
    """
    
    __abstract__ = True
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Tenant isolation - all models must have tenant_id
    tenant_id = Column(String(255), nullable=False, index=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Soft delete support
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Common metadata
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate table name from class name.
        
        Converts CamelCase class names to snake_case table names.
        Example: UserAccount -> user_accounts
        """
        # Convert CamelCase to snake_case
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        
        # Add 's' for pluralization (simple approach)
        if not name.endswith('s'):
            name += 's'
        
        return name
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id}, tenant_id={self.tenant_id})>"
    
    def to_dict(self, exclude_fields: Optional[list] = None) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Args:
            exclude_fields: List of field names to exclude from output
            
        Returns:
            Dictionary representation of the model
        """
        exclude_fields = exclude_fields or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value
        
        return result
    
    def soft_delete(self, deleted_by: Optional[str] = None) -> None:
        """
        Soft delete the model instance.
        
        Args:
            deleted_by: User ID who performed the deletion
        """
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        if deleted_by:
            self.updated_by = deleted_by
    
    def restore(self, restored_by: Optional[str] = None) -> None:
        """
        Restore a soft-deleted model instance.
        
        Args:
            restored_by: User ID who performed the restoration
        """
        self.is_deleted = False
        self.deleted_at = None
        if restored_by:
            self.updated_by = restored_by
    
    def is_soft_deleted(self) -> bool:
        """
        Check if the model instance is soft deleted.
        
        Returns:
            True if soft deleted, False otherwise
        """
        return self.is_deleted
    
    def update_audit_fields(self, updated_by: Optional[str] = None) -> None:
        """
        Update audit fields.
        
        Args:
            updated_by: User ID who performed the update
        """
        self.updated_at = datetime.utcnow()
        if updated_by:
            self.updated_by = updated_by
    
    @classmethod
    def generate_tenant_id(cls) -> str:
        """
        Generate a unique tenant ID.
        
        Returns:
            Unique tenant ID string
        """
        return f"tenant_{uuid.uuid4().hex[:12]}"
    
    @classmethod
    def get_tenant_filter(cls, tenant_id: str):
        """
        Get SQLAlchemy filter for tenant isolation.
        
        Args:
            tenant_id: The tenant ID to filter by
            
        Returns:
            SQLAlchemy filter expression
        """
        return cls.tenant_id == tenant_id
    
    def belongs_to_tenant(self, tenant_id: str) -> bool:
        """
        Check if the model instance belongs to the specified tenant.
        
        Args:
            tenant_id: The tenant ID to check
            
        Returns:
            True if belongs to tenant, False otherwise
        """
        return self.tenant_id == tenant_id
    
    def validate_tenant_access(self, tenant_id: str) -> None:
        """
        Validate that the model instance belongs to the specified tenant.
        
        Args:
            tenant_id: The tenant ID to validate against
            
        Raises:
            ValueError: If the model doesn't belong to the tenant
        """
        if not self.belongs_to_tenant(tenant_id):
            raise ValueError(f"Model {self.__class__.__name__} with ID {self.id} does not belong to tenant {tenant_id}")
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.__class__.__name__}(id={self.id})"
