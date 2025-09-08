"""
Account model for TheTally backend.

This module contains the Account model for financial accounts with multi-tenant support.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Index, Numeric, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from .base import BaseModel


class Account(BaseModel):
    """
    Account model for financial accounts with multi-tenant support.
    
    This model represents financial accounts in the system with support for:
    - Multiple account types (current, savings, credit, investment, etc.)
    - Balance tracking and history
    - Account relationships and hierarchies
    - Multi-tenant data isolation
    - Soft delete support
    """
    
    __tablename__ = "accounts"
    
    # Account identification
    name = Column(String(255), nullable=False, index=True)
    account_number = Column(String(50), nullable=True, index=True)
    external_id = Column(String(100), nullable=True, index=True)  # External system ID
    
    # Account type and classification
    account_type = Column(String(50), nullable=False, index=True)  # current, savings, credit, investment, etc.
    account_subtype = Column(String(50), nullable=True, index=True)  # checking, money_market, etc.
    
    # Financial institution
    institution_name = Column(String(255), nullable=True, index=True)
    institution_id = Column(String(100), nullable=True, index=True)
    routing_number = Column(String(20), nullable=True)
    
    # Balance information
    current_balance = Column(Numeric(15, 2), default=Decimal('0.00'), nullable=False)
    available_balance = Column(Numeric(15, 2), nullable=True)  # For credit accounts
    pending_balance = Column(Numeric(15, 2), default=Decimal('0.00'), nullable=False)
    
    # Account settings
    currency = Column(String(3), default="USD", nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    
    # Credit account specific fields
    credit_limit = Column(Numeric(15, 2), nullable=True)
    minimum_payment = Column(Numeric(15, 2), nullable=True)
    interest_rate = Column(Numeric(5, 4), nullable=True)  # Annual percentage rate
    
    # Account hierarchy
    parent_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    parent_account = relationship("Account", remote_side=[BaseModel.id], backref="sub_accounts")
    
    # User relationship
    user_id = Column(String(255), nullable=False, index=True)  # Owner of the account
    
    # Account metadata
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Import/export tracking
    last_imported_at = Column(DateTime(timezone=True), nullable=True)
    last_updated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_accounts_tenant_user', 'tenant_id', 'user_id'),
        Index('idx_accounts_tenant_type', 'tenant_id', 'account_type'),
        Index('idx_accounts_tenant_active', 'tenant_id', 'is_active'),
        Index('idx_accounts_user_type', 'user_id', 'account_type'),
        Index('idx_accounts_external_id', 'external_id'),
        Index('idx_accounts_institution', 'institution_name'),
    )
    
    def __repr__(self) -> str:
        """String representation of the Account."""
        return f"<Account(id={self.id}, name={self.name}, type={self.account_type}, tenant_id={self.tenant_id})>"
    
    @property
    def display_name(self) -> str:
        """Get the display name for the account."""
        if self.account_number:
            return f"{self.name} ({self.account_number})"
        return self.name
    
    @property
    def is_credit_account(self) -> bool:
        """Check if this is a credit account."""
        return self.account_type in ['credit', 'credit_card', 'line_of_credit']
    
    @property
    def is_investment_account(self) -> bool:
        """Check if this is an investment account."""
        return self.account_type in ['investment', 'pension', 'isa', 'retirement']
    
    @property
    def effective_balance(self) -> Decimal:
        """Get the effective balance (current for most accounts, available for credit)."""
        if self.is_credit_account and self.available_balance is not None:
            return self.available_balance
        return self.current_balance
    
    def update_balance(self, new_balance: Decimal, balance_type: str = "current") -> None:
        """
        Update account balance.
        
        Args:
            new_balance: New balance amount
            balance_type: Type of balance to update (current, available, pending)
        """
        if balance_type == "current":
            self.current_balance = new_balance
        elif balance_type == "available":
            self.available_balance = new_balance
        elif balance_type == "pending":
            self.pending_balance = new_balance
        else:
            raise ValueError(f"Invalid balance type: {balance_type}")
        
        self.last_updated_at = datetime.utcnow()
    
    def add_to_balance(self, amount: Decimal, balance_type: str = "current") -> None:
        """
        Add amount to account balance.
        
        Args:
            amount: Amount to add (can be negative for deductions)
            balance_type: Type of balance to update
        """
        if balance_type == "current":
            self.current_balance += amount
        elif balance_type == "available":
            if self.available_balance is None:
                self.available_balance = self.current_balance
            self.available_balance += amount
        elif balance_type == "pending":
            self.pending_balance += amount
        else:
            raise ValueError(f"Invalid balance type: {balance_type}")
        
        self.last_updated_at = datetime.utcnow()
    
    def can_withdraw(self, amount: Decimal) -> bool:
        """
        Check if account can withdraw the specified amount.
        
        Args:
            amount: Amount to withdraw
            
        Returns:
            True if withdrawal is allowed, False otherwise
        """
        if self.is_credit_account:
            # For credit accounts, check if we have available credit
            available = self.available_balance or self.credit_limit or Decimal('0')
            return amount <= available
        else:
            # For regular accounts, check if we have sufficient balance
            return amount <= self.current_balance
    
    def get_credit_utilization(self) -> float:
        """
        Get credit utilization percentage for credit accounts.
        
        Returns:
            Credit utilization as a percentage (0.0 to 1.0)
        """
        if not self.is_credit_account or not self.credit_limit:
            return 0.0
        
        used_amount = self.credit_limit - (self.available_balance or self.current_balance)
        return float(used_amount / self.credit_limit)
    
    def archive(self, archived_by: str = None) -> None:
        """
        Archive the account.
        
        Args:
            archived_by: User ID who archived the account
        """
        self.is_archived = True
        self.is_active = False
        if archived_by:
            self.updated_by = archived_by
        self.update_audit_fields(archived_by)
    
    def unarchive(self, unarchived_by: str = None) -> None:
        """
        Unarchive the account.
        
        Args:
            unarchived_by: User ID who unarchived the account
        """
        self.is_archived = False
        self.is_active = True
        if unarchived_by:
            self.updated_by = unarchived_by
        self.update_audit_fields(unarchived_by)
    
    def to_dict(self, exclude_sensitive: bool = True) -> dict:
        """
        Convert account to dictionary, optionally excluding sensitive fields.
        
        Args:
            exclude_sensitive: Whether to exclude sensitive fields
            
        Returns:
            Dictionary representation of the account
        """
        exclude_fields = ['notes', 'external_id', 'routing_number']
        if exclude_sensitive:
            return self.to_dict(exclude_fields=exclude_fields)
        else:
            return self.to_dict(exclude_fields=[])
    
    def validate_balance_consistency(self) -> bool:
        """
        Validate that account balances are consistent.
        
        Returns:
            True if balances are consistent, False otherwise
        """
        # For credit accounts, available balance should not exceed credit limit
        if self.is_credit_account and self.credit_limit and self.available_balance:
            return self.available_balance <= self.credit_limit
        
        # For regular accounts, available balance should equal current balance
        if not self.is_credit_account and self.available_balance:
            return self.available_balance == self.current_balance
        
        return True
