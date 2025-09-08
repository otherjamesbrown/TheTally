"""
Transaction service for TheTally backend.

This module provides transaction management services including CRUD operations,
transaction queries, validation, and bulk operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
import structlog
from datetime import datetime, date

from app.models.transaction import Transaction
from app.models.account import Account
from app.services.base import BaseService

# Get logger
logger = structlog.get_logger(__name__)


class TransactionService(BaseService):
    """
    Transaction service providing comprehensive transaction management operations.
    
    This service extends the base service with transaction-specific functionality:
    - Transaction CRUD operations
    - Transaction queries and filtering
    - Transaction validation and integrity checks
    - Bulk operations and imports
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the transaction service.
        
        Args:
            db_session: Optional database session. If not provided, a new session will be created.
        """
        super().__init__(db_session)
        self.logger = logger.bind(service="TransactionService")
    
    def create_transaction(self, account_id: int, amount: Decimal, description: str,
                          transaction_type: str, user_id: str, tenant_id: str,
                          transaction_date: datetime = None, **kwargs) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            account_id: Account ID
            amount: Transaction amount
            description: Transaction description
            transaction_type: Type of transaction (debit, credit, transfer)
            user_id: Owner user ID
            tenant_id: Tenant ID for multi-tenant support
            transaction_date: Transaction date (defaults to now)
            **kwargs: Additional transaction fields
            
        Returns:
            Created transaction object
            
        Raises:
            ValueError: If validation fails
            Exception: If transaction creation fails
        """
        try:
            # Validate transaction type
            valid_types = ['debit', 'credit', 'transfer']
            if transaction_type not in valid_types:
                raise ValueError(f"Invalid transaction type. Must be one of: {valid_types}")
            
            # Validate amount
            if amount <= 0:
                raise ValueError("Transaction amount must be positive")
            
            # Set default values
            if transaction_date is None:
                transaction_date = datetime.utcnow()
            
            transaction_data = {
                'account_id': account_id,
                'amount': amount,
                'description': description,
                'transaction_type': transaction_type,
                'user_id': user_id,
                'tenant_id': tenant_id,
                'transaction_date': transaction_date,
                'currency': kwargs.get('currency', 'USD'),
                'exchange_rate': kwargs.get('exchange_rate', Decimal('1.000000')),
                'status': kwargs.get('status', 'posted'),
                'is_reconciled': False,
                'is_duplicate': False,
                'is_auto_categorized': False,
                'fee_amount': kwargs.get('fee_amount', Decimal('0.00')),
                'interest_amount': kwargs.get('interest_amount', Decimal('0.00')),
                'tax_amount': kwargs.get('tax_amount', Decimal('0.00'))
            }
            
            # Add additional fields
            transaction_data.update(kwargs)
            
            # Create transaction
            transaction = self.create(Transaction, **transaction_data)
            
            # Update account balance if this is not a pending transaction
            if transaction.status == 'posted':
                self._update_account_balance(account_id, tenant_id, transaction)
            
            self.logger.info("Transaction created successfully", 
                           transaction_id=str(transaction.id),
                           account_id=account_id,
                           amount=str(amount),
                           transaction_type=transaction_type,
                           user_id=user_id,
                           tenant_id=tenant_id)
            
            return transaction
            
        except IntegrityError as e:
            self.logger.error("Transaction creation failed due to database constraint", 
                            error=str(e),
                            account_id=account_id,
                            amount=str(amount))
            raise ValueError("Transaction creation failed due to constraint violation")
        except Exception as e:
            self.logger.error("Transaction creation failed", 
                            error=str(e),
                            account_id=account_id,
                            amount=str(amount))
            raise
    
    def get_transaction_by_id(self, transaction_id: int, tenant_id: str) -> Optional[Transaction]:
        """
        Get transaction by ID.
        
        Args:
            transaction_id: Transaction ID
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Transaction object if found, None otherwise
        """
        try:
            transaction = self.db.query(Transaction).filter(
                Transaction.id == transaction_id,
                Transaction.tenant_id == tenant_id,
                Transaction.is_deleted == False
            ).first()
            
            if transaction:
                self.logger.debug("Transaction retrieved by ID", 
                               transaction_id=transaction_id,
                               tenant_id=tenant_id)
            else:
                self.logger.warning("Transaction not found by ID", 
                                  transaction_id=transaction_id,
                                  tenant_id=tenant_id)
            
            return transaction
            
        except Exception as e:
            self.logger.error("Failed to get transaction by ID", 
                            error=str(e),
                            transaction_id=transaction_id,
                            tenant_id=tenant_id)
            raise
    
    def get_transactions_by_account(self, account_id: int, tenant_id: str,
                                   limit: Optional[int] = None, offset: Optional[int] = None,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> List[Transaction]:
        """
        Get transactions for an account.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of transaction objects
        """
        try:
            query = self.db.query(Transaction).filter(
                Transaction.account_id == account_id,
                Transaction.tenant_id == tenant_id,
                Transaction.is_deleted == False
            )
            
            if start_date:
                query = query.filter(Transaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(Transaction.transaction_date <= end_date)
            
            query = query.order_by(Transaction.transaction_date.desc())
            
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            transactions = query.all()
            
            self.logger.debug("Transactions retrieved for account", 
                           account_id=account_id,
                           tenant_id=tenant_id,
                           count=len(transactions))
            
            return transactions
            
        except Exception as e:
            self.logger.error("Failed to get transactions by account", 
                            error=str(e),
                            account_id=account_id,
                            tenant_id=tenant_id)
            raise
    
    def get_transactions_by_user(self, user_id: str, tenant_id: str,
                                limit: Optional[int] = None, offset: Optional[int] = None,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> List[Transaction]:
        """
        Get transactions for a user.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID for multi-tenant support
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of transaction objects
        """
        try:
            query = self.db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.tenant_id == tenant_id,
                Transaction.is_deleted == False
            )
            
            if start_date:
                query = query.filter(Transaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(Transaction.transaction_date <= end_date)
            
            query = query.order_by(Transaction.transaction_date.desc())
            
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            transactions = query.all()
            
            self.logger.debug("Transactions retrieved for user", 
                           user_id=user_id,
                           tenant_id=tenant_id,
                           count=len(transactions))
            
            return transactions
            
        except Exception as e:
            self.logger.error("Failed to get transactions by user", 
                            error=str(e),
                            user_id=user_id,
                            tenant_id=tenant_id)
            raise
    
    def search_transactions(self, tenant_id: str, search_term: str,
                           limit: Optional[int] = None) -> List[Transaction]:
        """
        Search transactions by description or merchant name.
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            search_term: Search term
            limit: Optional limit on number of results
            
        Returns:
            List of matching transaction objects
        """
        try:
            query = self.db.query(Transaction).filter(
                Transaction.tenant_id == tenant_id,
                Transaction.is_deleted == False
            ).filter(
                (Transaction.description.ilike(f"%{search_term}%")) |
                (Transaction.merchant_name.ilike(f"%{search_term}%"))
            ).order_by(Transaction.transaction_date.desc())
            
            if limit:
                query = query.limit(limit)
            
            transactions = query.all()
            
            self.logger.debug("Transactions searched", 
                           tenant_id=tenant_id,
                           search_term=search_term[:10] + "***",
                           count=len(transactions))
            
            return transactions
            
        except Exception as e:
            self.logger.error("Failed to search transactions", 
                            error=str(e),
                            tenant_id=tenant_id,
                            search_term=search_term[:10] + "***")
            raise
    
    def get_transactions_by_category(self, category: str, tenant_id: str,
                                    limit: Optional[int] = None) -> List[Transaction]:
        """
        Get transactions by category.
        
        Args:
            category: Transaction category
            tenant_id: Tenant ID for multi-tenant support
            limit: Optional limit on number of results
            
        Returns:
            List of transaction objects
        """
        try:
            query = self.db.query(Transaction).filter(
                Transaction.transaction_category == category,
                Transaction.tenant_id == tenant_id,
                Transaction.is_deleted == False
            ).order_by(Transaction.transaction_date.desc())
            
            if limit:
                query = query.limit(limit)
            
            transactions = query.all()
            
            self.logger.debug("Transactions retrieved by category", 
                           category=category,
                           tenant_id=tenant_id,
                           count=len(transactions))
            
            return transactions
            
        except Exception as e:
            self.logger.error("Failed to get transactions by category", 
                            error=str(e),
                            category=category,
                            tenant_id=tenant_id)
            raise
    
    def update_transaction(self, transaction_id: int, tenant_id: str,
                          update_data: Dict[str, Any], updated_by: str = None) -> Transaction:
        """
        Update transaction information.
        
        Args:
            transaction_id: Transaction ID
            tenant_id: Tenant ID for multi-tenant support
            update_data: Dictionary of fields to update
            updated_by: User ID who updated this transaction
            
        Returns:
            Updated transaction object
            
        Raises:
            ValueError: If transaction not found or validation fails
        """
        try:
            transaction = self.get_transaction_by_id(transaction_id, tenant_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            # Store old amount for balance update
            old_amount = transaction.amount
            old_status = transaction.status
            
            # Update transaction
            self.update(transaction, **update_data)
            if updated_by:
                transaction.updated_by = updated_by
            transaction.update_audit_fields(updated_by)
            
            # Update account balance if amount or status changed
            if 'amount' in update_data or 'status' in update_data:
                self._update_account_balance(transaction.account_id, tenant_id, transaction, old_amount, old_status)
            
            self.logger.info("Transaction updated successfully", 
                           transaction_id=transaction_id,
                           tenant_id=tenant_id)
            
            return transaction
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to update transaction", 
                            error=str(e),
                            transaction_id=transaction_id,
                            tenant_id=tenant_id)
            raise
    
    def categorize_transaction(self, transaction_id: int, tenant_id: str,
                              category: str, subcategory: str = None,
                              confidence: float = None, rule_id: int = None,
                              updated_by: str = None) -> Transaction:
        """
        Categorize a transaction.
        
        Args:
            transaction_id: Transaction ID
            tenant_id: Tenant ID for multi-tenant support
            category: Main category
            subcategory: Subcategory (optional)
            confidence: Categorization confidence (0.0 to 1.0)
            rule_id: ID of the categorization rule used
            updated_by: User ID who categorized this transaction
            
        Returns:
            Updated transaction object
        """
        try:
            transaction = self.get_transaction_by_id(transaction_id, tenant_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            # Categorize transaction
            transaction.categorize(category, subcategory, confidence, rule_id)
            if updated_by:
                transaction.updated_by = updated_by
            transaction.update_audit_fields(updated_by)
            
            self.logger.info("Transaction categorized", 
                           transaction_id=transaction_id,
                           tenant_id=tenant_id,
                           category=category,
                           subcategory=subcategory)
            
            return transaction
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to categorize transaction", 
                            error=str(e),
                            transaction_id=transaction_id,
                            tenant_id=tenant_id)
            raise
    
    def reconcile_transaction(self, transaction_id: int, tenant_id: str,
                             reconciled_by: str = None) -> Transaction:
        """
        Reconcile a transaction.
        
        Args:
            transaction_id: Transaction ID
            tenant_id: Tenant ID for multi-tenant support
            reconciled_by: User ID who reconciled this transaction
            
        Returns:
            Updated transaction object
        """
        try:
            transaction = self.get_transaction_by_id(transaction_id, tenant_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            transaction.reconcile()
            if reconciled_by:
                transaction.updated_by = reconciled_by
            transaction.update_audit_fields(reconciled_by)
            
            self.logger.info("Transaction reconciled", 
                           transaction_id=transaction_id,
                           tenant_id=tenant_id)
            
            return transaction
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to reconcile transaction", 
                            error=str(e),
                            transaction_id=transaction_id,
                            tenant_id=tenant_id)
            raise
    
    def delete_transaction(self, transaction_id: int, tenant_id: str,
                          deleted_by: str = None) -> None:
        """
        Soft delete a transaction.
        
        Args:
            transaction_id: Transaction ID
            tenant_id: Tenant ID for multi-tenant support
            deleted_by: User ID who deleted this transaction
        """
        try:
            transaction = self.get_transaction_by_id(transaction_id, tenant_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            # Reverse account balance if transaction was posted
            if transaction.status == 'posted':
                self._reverse_account_balance(transaction.account_id, tenant_id, transaction)
            
            transaction.soft_delete(deleted_by)
            
            self.logger.info("Transaction deleted", 
                           transaction_id=transaction_id,
                           tenant_id=tenant_id)
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to delete transaction", 
                            error=str(e),
                            transaction_id=transaction_id,
                            tenant_id=tenant_id)
            raise
    
    def get_transaction_stats(self, tenant_id: str, user_id: str = None,
                             start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Get transaction statistics.
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            user_id: Optional user ID to filter by
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with transaction statistics
        """
        try:
            query = self.db.query(Transaction).filter(
                Transaction.tenant_id == tenant_id,
                Transaction.is_deleted == False
            )
            
            if user_id:
                query = query.filter(Transaction.user_id == user_id)
            if start_date:
                query = query.filter(Transaction.transaction_date >= start_date)
            if end_date:
                query = query.filter(Transaction.transaction_date <= end_date)
            
            transactions = query.all()
            
            # Calculate statistics
            total_count = len(transactions)
            total_amount = sum(t.effective_amount for t in transactions)
            
            # Income vs expenses
            income_transactions = [t for t in transactions if t.is_income]
            expense_transactions = [t for t in transactions if t.is_expense]
            
            income_amount = sum(t.effective_amount for t in income_transactions)
            expense_amount = sum(t.effective_amount for t in expense_transactions)
            
            # Category breakdown
            category_breakdown = {}
            for transaction in transactions:
                if transaction.transaction_category:
                    category = transaction.transaction_category
                    if category not in category_breakdown:
                        category_breakdown[category] = {'count': 0, 'amount': Decimal('0.00')}
                    category_breakdown[category]['count'] += 1
                    category_breakdown[category]['amount'] += transaction.effective_amount
            
            stats = {
                'total_transactions': total_count,
                'total_amount': str(total_amount),
                'income_count': len(income_transactions),
                'income_amount': str(income_amount),
                'expense_count': len(expense_transactions),
                'expense_amount': str(expense_amount),
                'net_amount': str(income_amount + expense_amount),  # expense_amount is negative
                'category_breakdown': {k: {'count': v['count'], 'amount': str(v['amount'])} 
                                    for k, v in category_breakdown.items()}
            }
            
            self.logger.debug("Transaction stats retrieved", 
                           tenant_id=tenant_id,
                           user_id=user_id,
                           stats=stats)
            
            return stats
            
        except Exception as e:
            self.logger.error("Failed to get transaction stats", 
                            error=str(e),
                            tenant_id=tenant_id,
                            user_id=user_id)
            raise
    
    def _update_account_balance(self, account_id: int, tenant_id: str, 
                               transaction: Transaction, old_amount: Decimal = None,
                               old_status: str = None) -> None:
        """
        Update account balance based on transaction.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            transaction: Transaction object
            old_amount: Previous transaction amount (for updates)
            old_status: Previous transaction status (for updates)
        """
        try:
            # Get account
            account = self.db.query(Account).filter(
                Account.id == account_id,
                Account.tenant_id == tenant_id
            ).first()
            
            if not account:
                self.logger.warning("Account not found for balance update", 
                                  account_id=account_id,
                                  tenant_id=tenant_id)
                return
            
            # If this is an update, reverse the old amount first
            if old_amount is not None and old_status == 'posted':
                old_impact = -old_amount if transaction.is_debit else old_amount
                account.add_to_balance(old_impact)
            
            # Apply new transaction impact
            if transaction.status == 'posted':
                impact = transaction.get_balance_impact()
                account.add_to_balance(impact)
            
            self.logger.debug("Account balance updated", 
                           account_id=account_id,
                           transaction_id=transaction.id,
                           impact=str(transaction.get_balance_impact()))
            
        except Exception as e:
            self.logger.error("Failed to update account balance", 
                            error=str(e),
                            account_id=account_id,
                            transaction_id=transaction.id)
            raise
    
    def _reverse_account_balance(self, account_id: int, tenant_id: str, 
                                transaction: Transaction) -> None:
        """
        Reverse account balance for a deleted transaction.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            transaction: Transaction object
        """
        try:
            # Get account
            account = self.db.query(Account).filter(
                Account.id == account_id,
                Account.tenant_id == tenant_id
            ).first()
            
            if not account:
                self.logger.warning("Account not found for balance reversal", 
                                  account_id=account_id,
                                  tenant_id=tenant_id)
                return
            
            # Reverse transaction impact
            if transaction.status == 'posted':
                impact = -transaction.get_balance_impact()
                account.add_to_balance(impact)
            
            self.logger.debug("Account balance reversed", 
                           account_id=account_id,
                           transaction_id=transaction.id,
                           impact=str(-transaction.get_balance_impact()))
            
        except Exception as e:
            self.logger.error("Failed to reverse account balance", 
                            error=str(e),
                            account_id=account_id,
                            transaction_id=transaction.id)
            raise
