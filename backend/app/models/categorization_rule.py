"""
CategorizationRule model for TheTally backend.

This module contains the CategorizationRule model for automated transaction categorization with multi-tenant support.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Index, Numeric, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from .base import BaseModel


class CategorizationRule(BaseModel):
    """
    CategorizationRule model for automated transaction categorization with multi-tenant support.
    
    This model represents categorization rules in the system with support for:
    - Pattern matching (regex, keywords, amount ranges)
    - Rule priority and conflict resolution
    - Multi-tenant data isolation
    - Soft delete support
    - Rule performance tracking and analytics
    """
    
    __tablename__ = "categorization_rules"
    
    # Rule identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Rule configuration
    rule_type = Column(String(50), nullable=False, index=True)  # keyword, regex, amount, merchant, combined
    pattern = Column(Text, nullable=False)  # The pattern to match against
    is_case_sensitive = Column(Boolean, default=False, nullable=False)
    is_regex = Column(Boolean, default=False, nullable=False)
    
    # Rule conditions
    field_to_match = Column(String(50), default="description", nullable=False)  # description, merchant, amount, etc.
    amount_min = Column(Numeric(15, 2), nullable=True)  # Minimum amount condition
    amount_max = Column(Numeric(15, 2), nullable=True)  # Maximum amount condition
    
    # Rule actions
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False, index=True)
    category = relationship("Category", backref="categorization_rules")
    subcategory = Column(String(100), nullable=True)
    
    # Rule settings
    priority = Column(Integer, default=100, nullable=False, index=True)  # Higher number = higher priority
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_system = Column(Boolean, default=False, nullable=False, index=True)  # System-created rule
    
    # Rule performance tracking
    match_count = Column(Integer, default=0, nullable=False, index=True)
    success_count = Column(Integer, default=0, nullable=False, index=True)
    last_matched_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Rule validation
    confidence_threshold = Column(Numeric(3, 2), default=Decimal('0.80'), nullable=False)  # 0.00 to 1.00
    max_matches_per_day = Column(Integer, default=1000, nullable=False)
    
    # User relationship
    user_id = Column(String(255), nullable=True, index=True)  # Owner (null for system rules)
    
    # Additional metadata
    notes = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_categorization_rules_tenant_type', 'tenant_id', 'rule_type'),
        Index('idx_categorization_rules_tenant_active', 'tenant_id', 'is_active'),
        Index('idx_categorization_rules_tenant_priority', 'tenant_id', 'priority'),
        Index('idx_categorization_rules_category', 'category_id'),
        Index('idx_categorization_rules_user', 'user_id'),
        Index('idx_categorization_rules_match_count', 'match_count'),
        Index('idx_categorization_rules_success_count', 'success_count'),
    )
    
    def __repr__(self) -> str:
        """String representation of the CategorizationRule."""
        return f"<CategorizationRule(id={self.id}, name={self.name}, pattern={self.pattern[:30]}, tenant_id={self.tenant_id})>"
    
    @property
    def success_rate(self) -> float:
        """Get the success rate of the rule."""
        if self.match_count == 0:
            return 0.0
        return float(self.success_count / self.match_count)
    
    @property
    def is_high_performing(self) -> bool:
        """Check if the rule is high performing."""
        return self.success_rate >= 0.8 and self.match_count >= 10
    
    @property
    def is_low_performing(self) -> bool:
        """Check if the rule is low performing."""
        return self.success_rate < 0.3 and self.match_count >= 5
    
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
        """Add a tag to the rule."""
        tags = self.get_tags_list()
        if tag not in tags:
            tags.append(tag)
            self.set_tags_list(tags)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the rule."""
        tags = self.get_tags_list()
        if tag in tags:
            tags.remove(tag)
            self.set_tags_list(tags)
    
    def matches_transaction(self, transaction) -> bool:
        """
        Check if the rule matches a transaction.
        
        Args:
            transaction: Transaction object to check
            
        Returns:
            True if rule matches, False otherwise
        """
        try:
            # Check amount conditions
            if self.amount_min is not None and transaction.amount < self.amount_min:
                return False
            if self.amount_max is not None and transaction.amount > self.amount_max:
                return False
            
            # Get the field value to match against
            field_value = getattr(transaction, self.field_to_match, "")
            if not field_value:
                return False
            
            # Convert to string for pattern matching
            field_value = str(field_value)
            
            # Apply case sensitivity
            if not self.is_case_sensitive:
                field_value = field_value.lower()
                pattern = self.pattern.lower()
            else:
                pattern = self.pattern
            
            # Perform pattern matching
            if self.is_regex:
                import re
                try:
                    return bool(re.search(pattern, field_value))
                except re.error:
                    return False
            else:
                return pattern in field_value
            
        except Exception:
            return False
    
    def apply_to_transaction(self, transaction) -> bool:
        """
        Apply the rule to a transaction.
        
        Args:
            transaction: Transaction object to categorize
            
        Returns:
            True if rule was applied, False otherwise
        """
        if not self.matches_transaction(transaction):
            return False
        
        # Check if we've exceeded daily match limit
        if self.match_count >= self.max_matches_per_day:
            return False
        
        # Apply categorization
        transaction.categorize(
            category=self.category.name,
            subcategory=self.subcategory,
            confidence=float(self.confidence_threshold),
            rule_id=self.id
        )
        
        # Update rule statistics
        self.match_count += 1
        self.success_count += 1
        self.last_matched_at = datetime.utcnow()
        self.last_success_at = datetime.utcnow()
        
        return True
    
    def record_match(self, success: bool = True) -> None:
        """
        Record a match for the rule.
        
        Args:
            success: Whether the match was successful
        """
        self.match_count += 1
        if success:
            self.success_count += 1
            self.last_success_at = datetime.utcnow()
        self.last_matched_at = datetime.utcnow()
    
    def reset_statistics(self) -> None:
        """Reset rule statistics."""
        self.match_count = 0
        self.success_count = 0
        self.last_matched_at = None
        self.last_success_at = None
    
    def test_against_transactions(self, transactions) -> dict:
        """
        Test the rule against a list of transactions.
        
        Args:
            transactions: List of transaction objects to test
            
        Returns:
            Dictionary with test results
        """
        results = {
            'total_tested': len(transactions),
            'matches': 0,
            'successes': 0,
            'false_positives': 0,
            'false_negatives': 0
        }
        
        for transaction in transactions:
            if self.matches_transaction(transaction):
                results['matches'] += 1
                
                # Check if the categorization would be correct
                expected_category = transaction.transaction_category
                if expected_category == self.category.name:
                    results['successes'] += 1
                else:
                    results['false_positives'] += 1
            else:
                # Check if we missed a transaction that should have matched
                if transaction.transaction_category == self.category.name:
                    results['false_negatives'] += 1
        
        return results
    
    def can_be_deleted(self) -> bool:
        """
        Check if the rule can be safely deleted.
        
        Returns:
            True if rule can be deleted, False otherwise
        """
        # System rules cannot be deleted
        if self.is_system:
            return False
        
        # High-performing rules should not be deleted
        if self.is_high_performing:
            return False
        
        return True
    
    def archive(self, archived_by: str = None) -> None:
        """
        Archive the rule.
        
        Args:
            archived_by: User ID who archived the rule
        """
        self.is_active = False
        if archived_by:
            self.updated_by = archived_by
        self.update_audit_fields(archived_by)
    
    def unarchive(self, unarchived_by: str = None) -> None:
        """
        Unarchive the rule.
        
        Args:
            unarchived_by: User ID who unarchived the rule
        """
        self.is_active = True
        if unarchived_by:
            self.updated_by = unarchived_by
        self.update_audit_fields(unarchived_by)
    
    def to_dict(self, exclude_sensitive: bool = True) -> dict:
        """
        Convert rule to dictionary, optionally excluding sensitive fields.
        
        Args:
            exclude_sensitive: Whether to exclude sensitive fields
            
        Returns:
            Dictionary representation of the rule
        """
        exclude_fields = ['notes']
        if exclude_sensitive:
            return self.to_dict(exclude_fields=exclude_fields)
        else:
            return self.to_dict(exclude_fields=[])
    
    def validate_pattern(self) -> bool:
        """
        Validate that the rule pattern is valid.
        
        Returns:
            True if pattern is valid, False otherwise
        """
        if not self.pattern:
            return False
        
        if self.is_regex:
            try:
                import re
                re.compile(self.pattern)
                return True
            except re.error:
                return False
        
        return True
    
    def validate_amount_range(self) -> bool:
        """
        Validate that the amount range is consistent.
        
        Returns:
            True if amount range is valid, False otherwise
        """
        if self.amount_min is not None and self.amount_max is not None:
            return self.amount_min <= self.amount_max
        
        return True
