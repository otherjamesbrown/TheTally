"""
Categorization service for TheTally backend.

This module provides automated categorization services including rule management,
pattern matching, and bulk categorization operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
import structlog
from datetime import datetime
import re

from app.models.categorization_rule import CategorizationRule
from app.models.transaction import Transaction
from app.models.category import Category
from app.services.base import BaseService

# Get logger
logger = structlog.get_logger(__name__)


class CategorizationService(BaseService):
    """
    Categorization service providing automated transaction categorization.
    
    This service extends the base service with categorization-specific functionality:
    - Rule management and CRUD operations
    - Pattern matching and rule application
    - Bulk categorization operations
    - Rule performance tracking and analytics
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the categorization service.
        
        Args:
            db_session: Optional database session. If not provided, a new session will be created.
        """
        super().__init__(db_session)
        self.logger = logger.bind(service="CategorizationService")
    
    def create_rule(self, name: str, pattern: str, category_id: int,
                    rule_type: str, tenant_id: str, user_id: str = None,
                    **kwargs) -> CategorizationRule:
        """
        Create a new categorization rule.
        
        Args:
            name: Rule name
            pattern: Pattern to match against
            category_id: Target category ID
            rule_type: Type of rule (keyword, regex, amount, merchant, combined)
            tenant_id: Tenant ID for multi-tenant support
            user_id: Owner user ID (optional)
            **kwargs: Additional rule fields
            
        Returns:
            Created rule object
            
        Raises:
            ValueError: If validation fails
            Exception: If rule creation fails
        """
        try:
            # Validate rule type
            valid_types = ['keyword', 'regex', 'amount', 'merchant', 'combined']
            if rule_type not in valid_types:
                raise ValueError(f"Invalid rule type. Must be one of: {valid_types}")
            
            # Validate category exists
            category = self.db.query(Category).filter(
                Category.id == category_id,
                Category.tenant_id == tenant_id,
                Category.is_deleted == False
            ).first()
            if not category:
                raise ValueError("Category not found")
            
            # Validate pattern if it's a regex
            is_regex = kwargs.get('is_regex', False)
            if is_regex:
                try:
                    re.compile(pattern)
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern: {e}")
            
            # Set default values
            rule_data = {
                'name': name,
                'pattern': pattern,
                'category_id': category_id,
                'rule_type': rule_type,
                'tenant_id': tenant_id,
                'user_id': user_id,
                'is_case_sensitive': kwargs.get('is_case_sensitive', False),
                'is_regex': is_regex,
                'field_to_match': kwargs.get('field_to_match', 'description'),
                'priority': kwargs.get('priority', 100),
                'is_active': True,
                'is_system': False,
                'match_count': 0,
                'success_count': 0,
                'confidence_threshold': kwargs.get('confidence_threshold', Decimal('0.80')),
                'max_matches_per_day': kwargs.get('max_matches_per_day', 1000)
            }
            
            # Add additional fields
            rule_data.update(kwargs)
            
            # Create rule
            rule = self.create(CategorizationRule, **rule_data)
            
            self.logger.info("Categorization rule created successfully", 
                           rule_id=str(rule.id),
                           name=name,
                           rule_type=rule_type,
                           tenant_id=tenant_id)
            
            return rule
            
        except IntegrityError as e:
            self.logger.error("Rule creation failed due to database constraint", 
                            error=str(e),
                            name=name,
                            rule_type=rule_type)
            raise ValueError("Rule creation failed due to constraint violation")
        except Exception as e:
            self.logger.error("Rule creation failed", 
                            error=str(e),
                            name=name,
                            rule_type=rule_type)
            raise
    
    def get_rule_by_id(self, rule_id: int, tenant_id: str) -> Optional[CategorizationRule]:
        """
        Get rule by ID.
        
        Args:
            rule_id: Rule ID
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Rule object if found, None otherwise
        """
        try:
            rule = self.db.query(CategorizationRule).filter(
                CategorizationRule.id == rule_id,
                CategorizationRule.tenant_id == tenant_id,
                CategorizationRule.is_deleted == False
            ).first()
            
            if rule:
                self.logger.debug("Rule retrieved by ID", 
                               rule_id=rule_id,
                               tenant_id=tenant_id)
            else:
                self.logger.warning("Rule not found by ID", 
                                  rule_id=rule_id,
                                  tenant_id=tenant_id)
            
            return rule
            
        except Exception as e:
            self.logger.error("Failed to get rule by ID", 
                            error=str(e),
                            rule_id=rule_id,
                            tenant_id=tenant_id)
            raise
    
    def get_rules_by_category(self, category_id: int, tenant_id: str,
                             active_only: bool = True) -> List[CategorizationRule]:
        """
        Get rules for a category.
        
        Args:
            category_id: Category ID
            tenant_id: Tenant ID for multi-tenant support
            active_only: Whether to return only active rules
            
        Returns:
            List of rule objects
        """
        try:
            query = self.db.query(CategorizationRule).filter(
                CategorizationRule.category_id == category_id,
                CategorizationRule.tenant_id == tenant_id,
                CategorizationRule.is_deleted == False
            )
            
            if active_only:
                query = query.filter(CategorizationRule.is_active == True)
            
            rules = query.order_by(CategorizationRule.priority.desc()).all()
            
            self.logger.debug("Rules retrieved for category", 
                           category_id=category_id,
                           tenant_id=tenant_id,
                           count=len(rules),
                           active_only=active_only)
            
            return rules
            
        except Exception as e:
            self.logger.error("Failed to get rules by category", 
                            error=str(e),
                            category_id=category_id,
                            tenant_id=tenant_id)
            raise
    
    def get_active_rules(self, tenant_id: str, rule_type: str = None) -> List[CategorizationRule]:
        """
        Get active rules for a tenant.
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            rule_type: Optional rule type filter
            
        Returns:
            List of active rule objects ordered by priority
        """
        try:
            query = self.db.query(CategorizationRule).filter(
                CategorizationRule.tenant_id == tenant_id,
                CategorizationRule.is_deleted == False,
                CategorizationRule.is_active == True
            )
            
            if rule_type:
                query = query.filter(CategorizationRule.rule_type == rule_type)
            
            rules = query.order_by(CategorizationRule.priority.desc()).all()
            
            self.logger.debug("Active rules retrieved", 
                           tenant_id=tenant_id,
                           rule_type=rule_type,
                           count=len(rules))
            
            return rules
            
        except Exception as e:
            self.logger.error("Failed to get active rules", 
                            error=str(e),
                            tenant_id=tenant_id,
                            rule_type=rule_type)
            raise
    
    def categorize_transaction(self, transaction: Transaction, 
                              tenant_id: str) -> Tuple[bool, Optional[CategorizationRule]]:
        """
        Categorize a single transaction using active rules.
        
        Args:
            transaction: Transaction object to categorize
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Tuple of (success, rule_used)
        """
        try:
            # Get active rules ordered by priority
            rules = self.get_active_rules(tenant_id)
            
            for rule in rules:
                if rule.matches_transaction(transaction):
                    success = rule.apply_to_transaction(transaction)
                    if success:
                        self.logger.info("Transaction categorized", 
                                       transaction_id=transaction.id,
                                       rule_id=rule.id,
                                       category=rule.category.name)
                        return True, rule
            
            self.logger.debug("No matching rule found for transaction", 
                           transaction_id=transaction.id,
                           description=transaction.description[:50] + "***")
            
            return False, None
            
        except Exception as e:
            self.logger.error("Failed to categorize transaction", 
                            error=str(e),
                            transaction_id=transaction.id)
            raise
    
    def bulk_categorize_transactions(self, transaction_ids: List[int], 
                                   tenant_id: str) -> Dict[str, Any]:
        """
        Categorize multiple transactions.
        
        Args:
            transaction_ids: List of transaction IDs to categorize
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Dictionary with categorization results
        """
        try:
            # Get transactions
            transactions = self.db.query(Transaction).filter(
                Transaction.id.in_(transaction_ids),
                Transaction.tenant_id == tenant_id,
                Transaction.is_deleted == False
            ).all()
            
            if not transactions:
                return {'categorized': 0, 'failed': 0, 'total': 0}
            
            # Get active rules
            rules = self.get_active_rules(tenant_id)
            
            categorized_count = 0
            failed_count = 0
            
            for transaction in transactions:
                try:
                    success, rule_used = self.categorize_transaction(transaction, tenant_id)
                    if success:
                        categorized_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    self.logger.error("Failed to categorize transaction in bulk", 
                                    error=str(e),
                                    transaction_id=transaction.id)
                    failed_count += 1
            
            results = {
                'categorized': categorized_count,
                'failed': failed_count,
                'total': len(transactions)
            }
            
            self.logger.info("Bulk categorization completed", 
                           tenant_id=tenant_id,
                           results=results)
            
            return results
            
        except Exception as e:
            self.logger.error("Failed to bulk categorize transactions", 
                            error=str(e),
                            tenant_id=tenant_id,
                            transaction_count=len(transaction_ids))
            raise
    
    def categorize_account_transactions(self, account_id: int, tenant_id: str,
                                       start_date: datetime = None,
                                       end_date: datetime = None) -> Dict[str, Any]:
        """
        Categorize all transactions for an account.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with categorization results
        """
        try:
            # Get transactions for account
            query = self.db.query(Transaction).filter(
                Transaction.account_id == account_id,
                Transaction.tenant_id == tenant_id,
                Transaction.is_deleted == False
            )
            
            if start_date:
                query = query.filter(Transaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(Transaction.transaction_date <= end_date)
            
            transactions = query.all()
            
            if not transactions:
                return {'categorized': 0, 'failed': 0, 'total': 0}
            
            # Categorize transactions
            categorized_count = 0
            failed_count = 0
            
            for transaction in transactions:
                try:
                    success, rule_used = self.categorize_transaction(transaction, tenant_id)
                    if success:
                        categorized_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    self.logger.error("Failed to categorize account transaction", 
                                    error=str(e),
                                    transaction_id=transaction.id)
                    failed_count += 1
            
            results = {
                'categorized': categorized_count,
                'failed': failed_count,
                'total': len(transactions)
            }
            
            self.logger.info("Account transactions categorized", 
                           account_id=account_id,
                           tenant_id=tenant_id,
                           results=results)
            
            return results
            
        except Exception as e:
            self.logger.error("Failed to categorize account transactions", 
                            error=str(e),
                            account_id=account_id,
                            tenant_id=tenant_id)
            raise
    
    def test_rule(self, rule_id: int, tenant_id: str, 
                  test_transactions: List[Transaction] = None) -> Dict[str, Any]:
        """
        Test a rule against transactions.
        
        Args:
            rule_id: Rule ID to test
            tenant_id: Tenant ID for multi-tenant support
            test_transactions: Optional list of transactions to test against
            
        Returns:
            Dictionary with test results
        """
        try:
            rule = self.get_rule_by_id(rule_id, tenant_id)
            if not rule:
                raise ValueError("Rule not found")
            
            # Get test transactions if not provided
            if test_transactions is None:
                test_transactions = self.db.query(Transaction).filter(
                    Transaction.tenant_id == tenant_id,
                    Transaction.is_deleted == False
                ).limit(100).all()
            
            # Test rule
            results = rule.test_against_transactions(test_transactions)
            
            self.logger.info("Rule tested", 
                           rule_id=rule_id,
                           tenant_id=tenant_id,
                           results=results)
            
            return results
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to test rule", 
                            error=str(e),
                            rule_id=rule_id,
                            tenant_id=tenant_id)
            raise
    
    def update_rule(self, rule_id: int, tenant_id: str,
                   update_data: Dict[str, Any], updated_by: str = None) -> CategorizationRule:
        """
        Update rule information.
        
        Args:
            rule_id: Rule ID
            tenant_id: Tenant ID for multi-tenant support
            update_data: Dictionary of fields to update
            updated_by: User ID who updated this rule
            
        Returns:
            Updated rule object
            
        Raises:
            ValueError: If rule not found or validation fails
        """
        try:
            rule = self.get_rule_by_id(rule_id, tenant_id)
            if not rule:
                raise ValueError("Rule not found")
            
            # Validate pattern if it's being updated and is a regex
            if 'pattern' in update_data and rule.is_regex:
                try:
                    re.compile(update_data['pattern'])
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern: {e}")
            
            # Update rule
            self.update(rule, **update_data)
            if updated_by:
                rule.updated_by = updated_by
            rule.update_audit_fields(updated_by)
            
            self.logger.info("Rule updated successfully", 
                           rule_id=rule_id,
                           tenant_id=tenant_id)
            
            return rule
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to update rule", 
                            error=str(e),
                            rule_id=rule_id,
                            tenant_id=tenant_id)
            raise
    
    def archive_rule(self, rule_id: int, tenant_id: str,
                    archived_by: str = None) -> CategorizationRule:
        """
        Archive a rule.
        
        Args:
            rule_id: Rule ID
            tenant_id: Tenant ID for multi-tenant support
            archived_by: User ID who archived this rule
            
        Returns:
            Archived rule object
        """
        try:
            rule = self.get_rule_by_id(rule_id, tenant_id)
            if not rule:
                raise ValueError("Rule not found")
            
            rule.archive(archived_by)
            
            self.logger.info("Rule archived", 
                           rule_id=rule_id,
                           tenant_id=tenant_id)
            
            return rule
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to archive rule", 
                            error=str(e),
                            rule_id=rule_id,
                            tenant_id=tenant_id)
            raise
    
    def delete_rule(self, rule_id: int, tenant_id: str,
                   deleted_by: str = None) -> None:
        """
        Soft delete a rule.
        
        Args:
            rule_id: Rule ID
            tenant_id: Tenant ID for multi-tenant support
            deleted_by: User ID who deleted this rule
        """
        try:
            rule = self.get_rule_by_id(rule_id, tenant_id)
            if not rule:
                raise ValueError("Rule not found")
            
            # Check if rule can be deleted
            if not rule.can_be_deleted():
                raise ValueError("Rule cannot be deleted because it's high-performing or system-created")
            
            rule.soft_delete(deleted_by)
            
            self.logger.info("Rule deleted", 
                           rule_id=rule_id,
                           tenant_id=tenant_id)
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to delete rule", 
                            error=str(e),
                            rule_id=rule_id,
                            tenant_id=tenant_id)
            raise
    
    def get_rule_stats(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get rule statistics for a tenant.
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Dictionary with rule statistics
        """
        try:
            total_rules = self.db.query(CategorizationRule).filter(
                CategorizationRule.tenant_id == tenant_id,
                CategorizationRule.is_deleted == False
            ).count()
            
            active_rules = self.db.query(CategorizationRule).filter(
                CategorizationRule.tenant_id == tenant_id,
                CategorizationRule.is_deleted == False,
                CategorizationRule.is_active == True
            ).count()
            
            system_rules = self.db.query(CategorizationRule).filter(
                CategorizationRule.tenant_id == tenant_id,
                CategorizationRule.is_deleted == False,
                CategorizationRule.is_system == True
            ).count()
            
            # Get type breakdown
            type_breakdown = {}
            for rule_type in ['keyword', 'regex', 'amount', 'merchant', 'combined']:
                count = self.db.query(CategorizationRule).filter(
                    CategorizationRule.tenant_id == tenant_id,
                    CategorizationRule.is_deleted == False,
                    CategorizationRule.is_active == True,
                    CategorizationRule.rule_type == rule_type
                ).count()
                type_breakdown[rule_type] = count
            
            # Get most successful rules
            most_successful = self.db.query(CategorizationRule).filter(
                CategorizationRule.tenant_id == tenant_id,
                CategorizationRule.is_deleted == False,
                CategorizationRule.is_active == True
            ).order_by(CategorizationRule.success_count.desc()).limit(5).all()
            
            most_successful_data = [
                {
                    'id': rule.id,
                    'name': rule.name,
                    'success_count': rule.success_count,
                    'match_count': rule.match_count,
                    'success_rate': float(rule.success_rate),
                    'rule_type': rule.rule_type
                }
                for rule in most_successful
            ]
            
            stats = {
                'total_rules': total_rules,
                'active_rules': active_rules,
                'inactive_rules': total_rules - active_rules,
                'system_rules': system_rules,
                'user_rules': total_rules - system_rules,
                'type_breakdown': type_breakdown,
                'most_successful_rules': most_successful_data
            }
            
            self.logger.debug("Rule stats retrieved", 
                           tenant_id=tenant_id,
                           stats=stats)
            
            return stats
            
        except Exception as e:
            self.logger.error("Failed to get rule stats", 
                            error=str(e),
                            tenant_id=tenant_id)
            raise
