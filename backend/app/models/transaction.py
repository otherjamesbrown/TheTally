"""
Transaction model for TheTally backend.

This module contains the Transaction model for financial transactions with multi-tenant support.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Index, Numeric, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from .base import BaseModel


class Transaction(BaseModel):
    """
    Transaction model for financial transactions with multi-tenant support.
    
    This model represents financial transactions in the system with support for:
    - Multiple transaction types (debit, credit, transfer, etc.)
    - Account relationships and balance updates
    - Category and subcategory classification
    - Multi-tenant data isolation
    - Soft delete support
    - Import tracking and reconciliation
    """
    
    __tablename__ = "transactions"
    
    # Transaction identification
    external_id = Column(String(100), nullable=True, index=True)  # External system ID
    reference_number = Column(String(100), nullable=True, index=True)  # Bank reference
    
    # Account relationship
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    account = relationship("Account", backref="transactions")
    
    # Transaction details
    amount = Column(Numeric(15, 2), nullable=False, index=True)
    description = Column(String(500), nullable=False, index=True)
    original_description = Column(String(500), nullable=True)  # Original description from import
    
    # Transaction classification
    transaction_type = Column(String(50), nullable=False, index=True)  # debit, credit, transfer
    transaction_category = Column(String(100), nullable=True, index=True)  # Main category
    transaction_subcategory = Column(String(100), nullable=True, index=True)  # Subcategory
    
    # Date information
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    posted_date = Column(DateTime(timezone=True), nullable=True, index=True)
    effective_date = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Financial details
    currency = Column(String(3), default="USD", nullable=False, index=True)
    exchange_rate = Column(Numeric(10, 6), default=Decimal('1.000000'), nullable=False)
    original_amount = Column(Numeric(15, 2), nullable=True)  # Original currency amount
    original_currency = Column(String(3), nullable=True)  # Original currency
    
    # Transaction status
    status = Column(String(20), default="posted", nullable=False, index=True)  # pending, posted, cancelled, reconciled
    is_reconciled = Column(Boolean, default=False, nullable=False, index=True)
    is_duplicate = Column(Boolean, default=False, nullable=False, index=True)
    
    # Categorization
    is_auto_categorized = Column(Boolean, default=False, nullable=False, index=True)
    categorization_confidence = Column(Numeric(3, 2), nullable=True)  # 0.00 to 1.00
    categorization_rule_id = Column(Integer, ForeignKey('categorization_rules.id'), nullable=True)
    categorization_rule = relationship("CategorizationRule", backref="transactions")
    
    # Transfer information
    transfer_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    transfer_account = relationship("Account", foreign_keys=[transfer_account_id], backref="transfer_transactions")
    transfer_transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=True)
    transfer_transaction = relationship("Transaction", remote_side=[BaseModel.id], backref="related_transactions")
    
    # Merchant information
    merchant_name = Column(String(255), nullable=True, index=True)
    merchant_category_code = Column(String(10), nullable=True, index=True)
    merchant_address = Column(Text, nullable=True)
    
    # Payment information
    payment_method = Column(String(50), nullable=True, index=True)  # card, check, transfer, cash
    check_number = Column(String(20), nullable=True)
    authorization_code = Column(String(50), nullable=True)
    
    # Fees and charges
    fee_amount = Column(Numeric(15, 2), default=Decimal('0.00'), nullable=False)
    interest_amount = Column(Numeric(15, 2), default=Decimal('0.00'), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=Decimal('0.00'), nullable=False)
    
    # Import tracking
    import_batch_id = Column(String(100), nullable=True, index=True)
    import_source = Column(String(50), nullable=True, index=True)  # csv, ofx, qif, api
    import_file_name = Column(String(255), nullable=True)
    import_date = Column(DateTime(timezone=True), nullable=True)
    
    # User relationship
    user_id = Column(String(255), nullable=False, index=True)  # Owner of the transaction
    
    # Additional metadata
    notes = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_transactions_tenant_user', 'tenant_id', 'user_id'),
        Index('idx_transactions_tenant_account', 'tenant_id', 'account_id'),
        Index('idx_transactions_tenant_date', 'tenant_id', 'transaction_date'),
        Index('idx_transactions_tenant_category', 'tenant_id', 'transaction_category'),
        Index('idx_transactions_account_date', 'account_id', 'transaction_date'),
        Index('idx_transactions_amount', 'amount'),
        Index('idx_transactions_status', 'status'),
        Index('idx_transactions_external_id', 'external_id'),
        Index('idx_transactions_merchant', 'merchant_name'),
        Index('idx_transactions_import_batch', 'import_batch_id'),
    )
    
    def __repr__(self) -> str:
        """String representation of the Transaction."""
        return f"<Transaction(id={self.id}, amount={self.amount}, description={self.description[:30]}, tenant_id={self.tenant_id})>"
    
    @property
    def is_debit(self) -> bool:
        """Check if this is a debit transaction."""
        return self.transaction_type == "debit"
    
    @property
    def is_credit(self) -> bool:
        """Check if this is a credit transaction."""
        return self.transaction_type == "credit"
    
    @property
    def is_transfer(self) -> bool:
        """Check if this is a transfer transaction."""
        return self.transaction_type == "transfer"
    
    @property
    def effective_amount(self) -> Decimal:
        """Get the effective amount (positive for credits, negative for debits)."""
        if self.is_credit:
            return self.amount
        elif self.is_debit:
            return -self.amount
        else:
            return self.amount
    
    @property
    def total_amount(self) -> Decimal:
        """Get the total amount including fees and interest."""
        return self.amount + self.fee_amount + self.interest_amount + self.tax_amount
    
    @property
    def is_income(self) -> bool:
        """Check if this transaction represents income."""
        return self.is_credit and self.transaction_category in [
            'income', 'salary', 'wages', 'bonus', 'dividend', 'interest_income'
        ]
    
    @property
    def is_expense(self) -> bool:
        """Check if this transaction represents an expense."""
        return self.is_debit and self.transaction_category not in [
            'transfer', 'payment', 'refund'
        ]
    
    def get_tags_list(self) -> list:
        """Get tags as a list."""
        if not self.tags:
            return []
        try:
            import json
            return json.loads(self.tags)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_tags_list(self, tags: list) -> None:
        """Set tags from a list."""
        if tags:
            import json
            self.tags = json.dumps(tags)
        else:
            self.tags = None
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the transaction."""
        tags = self.get_tags_list()
        if tag not in tags:
            tags.append(tag)
            self.set_tags_list(tags)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the transaction."""
        tags = self.get_tags_list()
        if tag in tags:
            tags.remove(tag)
            self.set_tags_list(tags)
    
    def categorize(self, category: str, subcategory: str = None, 
                   confidence: float = None, rule_id: int = None) -> None:
        """
        Categorize the transaction.
        
        Args:
            category: Main category
            subcategory: Subcategory (optional)
            confidence: Categorization confidence (0.0 to 1.0)
            rule_id: ID of the categorization rule used
        """
        self.transaction_category = category
        self.transaction_subcategory = subcategory
        self.is_auto_categorized = rule_id is not None
        if confidence is not None:
            self.categorization_confidence = Decimal(str(confidence))
        if rule_id is not None:
            self.categorization_rule_id = rule_id
    
    def reconcile(self) -> None:
        """Mark the transaction as reconciled."""
        self.is_reconciled = True
        self.status = "reconciled"
    
    def unreconcile(self) -> None:
        """Mark the transaction as unreconciled."""
        self.is_reconciled = False
        self.status = "posted"
    
    def mark_duplicate(self) -> None:
        """Mark the transaction as a duplicate."""
        self.is_duplicate = True
    
    def unmark_duplicate(self) -> None:
        """Unmark the transaction as a duplicate."""
        self.is_duplicate = False
    
    def cancel(self) -> None:
        """Cancel the transaction."""
        self.status = "cancelled"
    
    def uncancel(self) -> None:
        """Uncancel the transaction."""
        self.status = "posted"
    
    def to_dict(self, exclude_sensitive: bool = True) -> dict:
        """
        Convert transaction to dictionary, optionally excluding sensitive fields.
        
        Args:
            exclude_sensitive: Whether to exclude sensitive fields
            
        Returns:
            Dictionary representation of the transaction
        """
        exclude_fields = ['notes', 'external_id', 'authorization_code']
        if exclude_sensitive:
            return self.to_dict(exclude_fields=exclude_fields)
        else:
            return self.to_dict(exclude_fields=[])
    
    def validate_amount_consistency(self) -> bool:
        """
        Validate that transaction amounts are consistent.
        
        Returns:
            True if amounts are consistent, False otherwise
        """
        # Amount should be positive
        if self.amount <= 0:
            return False
        
        # For transfers, both transactions should have the same amount
        if self.is_transfer and self.transfer_transaction:
            return self.amount == self.transfer_transaction.amount
        
        return True
    
    def get_balance_impact(self) -> Decimal:
        """
        Get the impact of this transaction on account balance.
        
        Returns:
            Positive amount for credits, negative for debits
        """
        return self.effective_amount
