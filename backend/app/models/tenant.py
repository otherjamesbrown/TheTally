"""
Tenant model for TheTally backend.

This module contains the Tenant model for multi-tenant architecture support.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .base import BaseModel


class Tenant(BaseModel):
    """
    Tenant model for multi-tenant architecture.
    
    This model represents organizations/tenants in the system with support for:
    - Multi-tenant data isolation
    - Organization management
    - Subscription and billing
    - Feature flags
    """
    
    __tablename__ = "tenants"
    
    # Tenant identification
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    domain = Column(String(255), nullable=True, unique=True, index=True)
    
    # Organization details
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    
    # Contact information
    contact_email = Column(String(254), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_trial = Column(Boolean, default=True, nullable=False)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Subscription information
    subscription_plan = Column(String(50), default="free", nullable=False)
    subscription_status = Column(String(20), default="active", nullable=False)
    subscription_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Feature flags
    features = Column(Text, nullable=True)  # JSON string of enabled features
    
    # Limits and quotas
    max_users = Column(String(10), default="5", nullable=False)
    max_storage_mb = Column(String(10), default="1000", nullable=False)
    max_transactions = Column(String(10), default="10000", nullable=False)
    
    # Billing
    billing_email = Column(String(254), nullable=True)
    billing_address = Column(Text, nullable=True)
    tax_id = Column(String(50), nullable=True)
    
    # Settings
    timezone = Column(String(50), default="UTC", nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    date_format = Column(String(20), default="YYYY-MM-DD", nullable=False)
    
    # Additional metadata
    notes = Column(Text, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_tenants_slug', 'slug'),
        Index('idx_tenants_domain', 'domain'),
        Index('idx_tenants_active', 'is_active'),
        Index('idx_tenants_subscription', 'subscription_status'),
    )
    
    def __repr__(self) -> str:
        """String representation of the Tenant."""
        return f"<Tenant(id={self.id}, name={self.name}, slug={self.slug})>"
    
    @property
    def is_trial_expired(self) -> bool:
        """Check if the trial period has expired."""
        if not self.is_trial or self.trial_ends_at is None:
            return False
        return datetime.utcnow() > self.trial_ends_at
    
    @property
    def is_subscription_active(self) -> bool:
        """Check if the subscription is active."""
        if self.subscription_status != "active":
            return False
        if self.subscription_ends_at is None:
            return True
        return datetime.utcnow() < self.subscription_ends_at
    
    def get_feature(self, feature_name: str) -> bool:
        """
        Check if a specific feature is enabled for this tenant.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            True if feature is enabled, False otherwise
        """
        if not self.features:
            return False
        
        try:
            import json
            features = json.loads(self.features)
            return features.get(feature_name, False)
        except (json.JSONDecodeError, TypeError):
            return False
    
    def set_feature(self, feature_name: str, enabled: bool) -> None:
        """
        Enable or disable a feature for this tenant.
        
        Args:
            feature_name: Name of the feature
            enabled: Whether to enable the feature
        """
        try:
            import json
            features = json.loads(self.features) if self.features else {}
            features[feature_name] = enabled
            self.features = json.dumps(features)
        except (json.JSONDecodeError, TypeError):
            self.features = json.dumps({feature_name: enabled})
    
    def get_quota(self, quota_name: str) -> int:
        """
        Get the quota value for a specific resource.
        
        Args:
            quota_name: Name of the quota (max_users, max_storage_mb, max_transactions)
            
        Returns:
            Quota value as integer
        """
        quota_field = getattr(self, quota_name, "0")
        try:
            return int(quota_field)
        except (ValueError, TypeError):
            return 0
    
    def set_quota(self, quota_name: str, value: int) -> None:
        """
        Set the quota value for a specific resource.
        
        Args:
            quota_name: Name of the quota
            value: Quota value to set
        """
        if hasattr(self, quota_name):
            setattr(self, quota_name, str(value))
    
    def to_dict(self, exclude_sensitive: bool = True) -> dict:
        """
        Convert tenant to dictionary, optionally excluding sensitive fields.
        
        Args:
            exclude_sensitive: Whether to exclude sensitive fields
            
        Returns:
            Dictionary representation of the tenant
        """
        exclude_fields = ['billing_address', 'tax_id', 'notes']
        if exclude_sensitive:
            return self.to_dict(exclude_fields=exclude_fields)
        else:
            return self.to_dict(exclude_fields=[])
