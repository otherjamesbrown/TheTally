"""
Category model for TheTally backend.

This module contains the Category model for transaction categorization with multi-tenant support.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Index, Numeric, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from .base import BaseModel


class Category(BaseModel):
    """
    Category model for transaction categorization with multi-tenant support.
    
    This model represents transaction categories in the system with support for:
    - Hierarchical category structure (parent/child relationships)
    - Category types and classifications
    - Multi-tenant data isolation
    - Soft delete support
    - Category usage tracking and analytics
    """
    
    __tablename__ = "categories"
    
    # Category identification
    name = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    slug = Column(String(100), nullable=False, index=True)  # URL-friendly identifier
    
    # Category hierarchy
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    parent = relationship("Category", remote_side=[BaseModel.id], backref="subcategories")
    
    # Category classification
    category_type = Column(String(50), nullable=False, index=True)  # income, expense, transfer, other
    category_group = Column(String(100), nullable=True, index=True)  # food, transportation, utilities, etc.
    
    # Category settings
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_default = Column(Boolean, default=False, nullable=False, index=True)
    is_system = Column(Boolean, default=False, nullable=False, index=True)  # System-created category
    
    # Visual representation
    color = Column(String(7), nullable=True)  # Hex color code
    icon = Column(String(50), nullable=True)  # Icon identifier
    
    # Category metadata
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0, nullable=False, index=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Budget and planning
    budget_amount = Column(Numeric(15, 2), nullable=True)
    budget_period = Column(String(20), nullable=True)  # monthly, yearly, etc.
    budget_start_date = Column(DateTime(timezone=True), nullable=True)
    budget_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # User relationship
    user_id = Column(String(255), nullable=True, index=True)  # Owner (null for system categories)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_categories_tenant_type', 'tenant_id', 'category_type'),
        Index('idx_categories_tenant_group', 'tenant_id', 'category_group'),
        Index('idx_categories_tenant_active', 'tenant_id', 'is_active'),
        Index('idx_categories_tenant_system', 'tenant_id', 'is_system'),
        Index('idx_categories_parent', 'parent_id'),
        Index('idx_categories_slug', 'slug'),
        Index('idx_categories_usage', 'usage_count'),
        Index('idx_categories_user', 'user_id'),
    )
    
    def __repr__(self) -> str:
        """String representation of the Category."""
        return f"<Category(id={self.id}, name={self.name}, type={self.category_type}, tenant_id={self.tenant_id})>"
    
    @property
    def full_path(self) -> str:
        """Get the full hierarchical path of the category."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    @property
    def level(self) -> int:
        """Get the hierarchy level of the category (0 for root)."""
        if self.parent:
            return self.parent.level + 1
        return 0
    
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf category (no subcategories)."""
        return len(self.subcategories) == 0
    
    @property
    def is_root(self) -> bool:
        """Check if this is a root category (no parent)."""
        return self.parent_id is None
    
    @property
    def effective_name(self) -> str:
        """Get the effective display name."""
        return self.display_name or self.name
    
    def get_ancestors(self) -> list:
        """
        Get all ancestor categories.
        
        Returns:
            List of ancestor categories from root to parent
        """
        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors
    
    def get_descendants(self, include_self: bool = False) -> list:
        """
        Get all descendant categories.
        
        Args:
            include_self: Whether to include this category in the result
            
        Returns:
            List of descendant categories
        """
        descendants = []
        if include_self:
            descendants.append(self)
        
        for subcategory in self.subcategories:
            descendants.extend(subcategory.get_descendants(include_self=True))
        
        return descendants
    
    def get_siblings(self, include_self: bool = False) -> list:
        """
        Get sibling categories (same parent).
        
        Args:
            include_self: Whether to include this category in the result
            
        Returns:
            List of sibling categories
        """
        if not self.parent:
            return []
        
        siblings = [cat for cat in self.parent.subcategories if cat.id != self.id]
        if include_self:
            siblings.append(self)
        
        return siblings
    
    def increment_usage(self) -> None:
        """Increment the usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
    
    def reset_usage(self) -> None:
        """Reset the usage count and last used timestamp."""
        self.usage_count = 0
        self.last_used_at = None
    
    def set_budget(self, amount: Decimal, period: str = "monthly", 
                   start_date: datetime = None, end_date: datetime = None) -> None:
        """
        Set budget information for the category.
        
        Args:
            amount: Budget amount
            period: Budget period (monthly, yearly, etc.)
            start_date: Budget start date
            end_date: Budget end date
        """
        self.budget_amount = amount
        self.budget_period = period
        if start_date:
            self.budget_start_date = start_date
        if end_date:
            self.budget_end_date = end_date
    
    def clear_budget(self) -> None:
        """Clear budget information."""
        self.budget_amount = None
        self.budget_period = None
        self.budget_start_date = None
        self.budget_end_date = None
    
    def is_budget_active(self) -> bool:
        """Check if the budget is currently active."""
        if not self.budget_amount or not self.budget_start_date:
            return False
        
        now = datetime.utcnow()
        if self.budget_end_date and now > self.budget_end_date:
            return False
        
        return now >= self.budget_start_date
    
    def get_budget_remaining(self, spent_amount: Decimal) -> Decimal:
        """
        Get the remaining budget amount.
        
        Args:
            spent_amount: Amount already spent in this category
            
        Returns:
            Remaining budget amount
        """
        if not self.budget_amount or not self.is_budget_active():
            return Decimal('0.00')
        
        return max(Decimal('0.00'), self.budget_amount - spent_amount)
    
    def can_be_deleted(self) -> bool:
        """
        Check if the category can be safely deleted.
        
        Returns:
            True if category can be deleted, False otherwise
        """
        # System categories cannot be deleted
        if self.is_system:
            return False
        
        # Categories with subcategories cannot be deleted
        if self.subcategories:
            return False
        
        # Categories with high usage should not be deleted
        if self.usage_count > 10:
            return False
        
        return True
    
    def archive(self, archived_by: str = None) -> None:
        """
        Archive the category.
        
        Args:
            archived_by: User ID who archived the category
        """
        self.is_active = False
        if archived_by:
            self.updated_by = archived_by
        self.update_audit_fields(archived_by)
    
    def unarchive(self, unarchived_by: str = None) -> None:
        """
        Unarchive the category.
        
        Args:
            unarchived_by: User ID who unarchived the category
        """
        self.is_active = True
        if unarchived_by:
            self.updated_by = unarchived_by
        self.update_audit_fields(unarchived_by)
    
    def to_dict(self, exclude_sensitive: bool = True) -> dict:
        """
        Convert category to dictionary, optionally excluding sensitive fields.
        
        Args:
            exclude_sensitive: Whether to exclude sensitive fields
            
        Returns:
            Dictionary representation of the category
        """
        exclude_fields = ['notes']
        if exclude_sensitive:
            return self.to_dict(exclude_fields=exclude_fields)
        else:
            return self.to_dict(exclude_fields=[])
    
    def validate_hierarchy(self) -> bool:
        """
        Validate that the category hierarchy is consistent.
        
        Returns:
            True if hierarchy is valid, False otherwise
        """
        # Category cannot be its own parent
        if self.parent_id == self.id:
            return False
        
        # Check for circular references
        current = self.parent
        while current:
            if current.id == self.id:
                return False
            current = current.parent
        
        return True
