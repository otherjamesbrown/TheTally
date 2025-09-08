"""
Account service for TheTally backend.

This module provides account management services including CRUD operations,
balance calculations, account relationships, and account validation.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
import structlog
from datetime import datetime

from app.models.account import Account
from app.services.base import BaseService

# Get logger
logger = structlog.get_logger(__name__)


class AccountService(BaseService):
    """
    Account service providing comprehensive account management operations.
    
    This service extends the base service with account-specific functionality:
    - Account CRUD operations
    - Balance calculations and updates
    - Account relationships and hierarchies
    - Account validation and integrity checks
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the account service.
        
        Args:
            db_session: Optional database session. If not provided, a new session will be created.
        """
        super().__init__(db_session)
        self.logger = logger.bind(service="AccountService")
    
    def create_account(self, name: str, account_type: str, user_id: str, 
                      tenant_id: str, **kwargs) -> Account:
        """
        Create a new account.
        
        Args:
            name: Account name
            account_type: Type of account (current, savings, credit, etc.)
            user_id: Owner user ID
            tenant_id: Tenant ID for multi-tenant support
            **kwargs: Additional account fields
            
        Returns:
            Created account object
            
        Raises:
            ValueError: If validation fails
            Exception: If account creation fails
        """
        try:
            # Validate account type
            valid_types = ['current', 'savings', 'credit', 'credit_card', 'investment', 
                          'pension', 'isa', 'retirement', 'loan', 'mortgage']
            if account_type not in valid_types:
                raise ValueError(f"Invalid account type. Must be one of: {valid_types}")
            
            # Set default values
            account_data = {
                'name': name,
                'account_type': account_type,
                'user_id': user_id,
                'tenant_id': tenant_id,
                'current_balance': Decimal('0.00'),
                'pending_balance': Decimal('0.00'),
                'currency': kwargs.get('currency', 'USD'),
                'is_active': True,
                'is_archived': False
            }
            
            # Add additional fields
            account_data.update(kwargs)
            
            # Create account
            account = self.create(Account, **account_data)
            
            self.logger.info("Account created successfully", 
                           account_id=str(account.id),
                           name=name,
                           account_type=account_type,
                           user_id=user_id,
                           tenant_id=tenant_id)
            
            return account
            
        except IntegrityError as e:
            self.logger.error("Account creation failed due to database constraint", 
                            error=str(e),
                            name=name,
                            account_type=account_type)
            raise ValueError("Account creation failed due to constraint violation")
        except Exception as e:
            self.logger.error("Account creation failed", 
                            error=str(e),
                            name=name,
                            account_type=account_type)
            raise
    
    def get_account_by_id(self, account_id: int, tenant_id: str) -> Optional[Account]:
        """
        Get account by ID.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Account object if found, None otherwise
        """
        try:
            account = self.db.query(Account).filter(
                Account.id == account_id,
                Account.tenant_id == tenant_id,
                Account.is_deleted == False
            ).first()
            
            if account:
                self.logger.debug("Account retrieved by ID", 
                               account_id=account_id,
                               tenant_id=tenant_id)
            else:
                self.logger.warning("Account not found by ID", 
                                  account_id=account_id,
                                  tenant_id=tenant_id)
            
            return account
            
        except Exception as e:
            self.logger.error("Failed to get account by ID", 
                            error=str(e),
                            account_id=account_id,
                            tenant_id=tenant_id)
            raise
    
    def get_accounts_by_user(self, user_id: str, tenant_id: str, 
                            active_only: bool = True) -> List[Account]:
        """
        Get accounts for a user.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID for multi-tenant support
            active_only: Whether to return only active accounts
            
        Returns:
            List of account objects
        """
        try:
            query = self.db.query(Account).filter(
                Account.user_id == user_id,
                Account.tenant_id == tenant_id,
                Account.is_deleted == False
            )
            
            if active_only:
                query = query.filter(Account.is_active == True, Account.is_archived == False)
            
            accounts = query.all()
            
            self.logger.debug("Accounts retrieved for user", 
                           user_id=user_id,
                           tenant_id=tenant_id,
                           count=len(accounts),
                           active_only=active_only)
            
            return accounts
            
        except Exception as e:
            self.logger.error("Failed to get accounts by user", 
                            error=str(e),
                            user_id=user_id,
                            tenant_id=tenant_id)
            raise
    
    def get_accounts_by_type(self, account_type: str, tenant_id: str, 
                            active_only: bool = True) -> List[Account]:
        """
        Get accounts by type.
        
        Args:
            account_type: Type of account
            tenant_id: Tenant ID for multi-tenant support
            active_only: Whether to return only active accounts
            
        Returns:
            List of account objects
        """
        try:
            query = self.db.query(Account).filter(
                Account.account_type == account_type,
                Account.tenant_id == tenant_id,
                Account.is_deleted == False
            )
            
            if active_only:
                query = query.filter(Account.is_active == True, Account.is_archived == False)
            
            accounts = query.all()
            
            self.logger.debug("Accounts retrieved by type", 
                           account_type=account_type,
                           tenant_id=tenant_id,
                           count=len(accounts),
                           active_only=active_only)
            
            return accounts
            
        except Exception as e:
            self.logger.error("Failed to get accounts by type", 
                            error=str(e),
                            account_type=account_type,
                            tenant_id=tenant_id)
            raise
    
    def search_accounts(self, tenant_id: str, search_term: str, 
                       limit: Optional[int] = None) -> List[Account]:
        """
        Search accounts by name or account number.
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            search_term: Search term
            limit: Optional limit on number of results
            
        Returns:
            List of matching account objects
        """
        try:
            query = self.db.query(Account).filter(
                Account.tenant_id == tenant_id,
                Account.is_deleted == False,
                Account.is_active == True
            ).filter(
                (Account.name.ilike(f"%{search_term}%")) |
                (Account.account_number.ilike(f"%{search_term}%"))
            )
            
            if limit:
                query = query.limit(limit)
            
            accounts = query.all()
            
            self.logger.debug("Accounts searched", 
                           tenant_id=tenant_id,
                           search_term=search_term[:10] + "***",
                           count=len(accounts))
            
            return accounts
            
        except Exception as e:
            self.logger.error("Failed to search accounts", 
                            error=str(e),
                            tenant_id=tenant_id,
                            search_term=search_term[:10] + "***")
            raise
    
    def update_account(self, account_id: int, tenant_id: str, 
                      update_data: Dict[str, Any], updated_by: str = None) -> Account:
        """
        Update account information.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            update_data: Dictionary of fields to update
            updated_by: User ID who updated this account
            
        Returns:
            Updated account object
            
        Raises:
            ValueError: If account not found or validation fails
        """
        try:
            account = self.get_account_by_id(account_id, tenant_id)
            if not account:
                raise ValueError("Account not found")
            
            # Validate account type if being updated
            if 'account_type' in update_data:
                valid_types = ['current', 'savings', 'credit', 'credit_card', 'investment', 
                              'pension', 'isa', 'retirement', 'loan', 'mortgage']
                if update_data['account_type'] not in valid_types:
                    raise ValueError(f"Invalid account type. Must be one of: {valid_types}")
            
            # Update account
            self.update(account, **update_data)
            if updated_by:
                account.updated_by = updated_by
            account.update_audit_fields(updated_by)
            
            self.logger.info("Account updated successfully", 
                           account_id=account_id,
                           tenant_id=tenant_id)
            
            return account
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to update account", 
                            error=str(e),
                            account_id=account_id,
                            tenant_id=tenant_id)
            raise
    
    def update_balance(self, account_id: int, tenant_id: str, 
                      new_balance: Decimal, balance_type: str = "current", 
                      updated_by: str = None) -> Account:
        """
        Update account balance.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            new_balance: New balance amount
            balance_type: Type of balance to update (current, available, pending)
            updated_by: User ID who updated this account
            
        Returns:
            Updated account object
        """
        try:
            account = self.get_account_by_id(account_id, tenant_id)
            if not account:
                raise ValueError("Account not found")
            
            # Update balance
            account.update_balance(new_balance, balance_type)
            if updated_by:
                account.updated_by = updated_by
            account.update_audit_fields(updated_by)
            
            self.logger.info("Account balance updated", 
                           account_id=account_id,
                           tenant_id=tenant_id,
                           new_balance=str(new_balance),
                           balance_type=balance_type)
            
            return account
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to update account balance", 
                            error=str(e),
                            account_id=account_id,
                            tenant_id=tenant_id)
            raise
    
    def add_to_balance(self, account_id: int, tenant_id: str, 
                      amount: Decimal, balance_type: str = "current", 
                      updated_by: str = None) -> Account:
        """
        Add amount to account balance.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            amount: Amount to add (can be negative for deductions)
            balance_type: Type of balance to update
            updated_by: User ID who updated this account
            
        Returns:
            Updated account object
        """
        try:
            account = self.get_account_by_id(account_id, tenant_id)
            if not account:
                raise ValueError("Account not found")
            
            # Add to balance
            account.add_to_balance(amount, balance_type)
            if updated_by:
                account.updated_by = updated_by
            account.update_audit_fields(updated_by)
            
            self.logger.info("Amount added to account balance", 
                           account_id=account_id,
                           tenant_id=tenant_id,
                           amount=str(amount),
                           balance_type=balance_type)
            
            return account
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to add to account balance", 
                            error=str(e),
                            account_id=account_id,
                            tenant_id=tenant_id)
            raise
    
    def archive_account(self, account_id: int, tenant_id: str, 
                       archived_by: str = None) -> Account:
        """
        Archive an account.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            archived_by: User ID who archived this account
            
        Returns:
            Archived account object
        """
        try:
            account = self.get_account_by_id(account_id, tenant_id)
            if not account:
                raise ValueError("Account not found")
            
            account.archive(archived_by)
            
            self.logger.info("Account archived", 
                           account_id=account_id,
                           tenant_id=tenant_id)
            
            return account
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to archive account", 
                            error=str(e),
                            account_id=account_id,
                            tenant_id=tenant_id)
            raise
    
    def unarchive_account(self, account_id: int, tenant_id: str, 
                         unarchived_by: str = None) -> Account:
        """
        Unarchive an account.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            unarchived_by: User ID who unarchived this account
            
        Returns:
            Unarchived account object
        """
        try:
            account = self.get_account_by_id(account_id, tenant_id)
            if not account:
                raise ValueError("Account not found")
            
            account.unarchive(unarchived_by)
            
            self.logger.info("Account unarchived", 
                           account_id=account_id,
                           tenant_id=tenant_id)
            
            return account
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to unarchive account", 
                            error=str(e),
                            account_id=account_id,
                            tenant_id=tenant_id)
            raise
    
    def delete_account(self, account_id: int, tenant_id: str, 
                      deleted_by: str = None) -> None:
        """
        Soft delete an account.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            deleted_by: User ID who deleted this account
        """
        try:
            account = self.get_account_by_id(account_id, tenant_id)
            if not account:
                raise ValueError("Account not found")
            
            account.soft_delete(deleted_by)
            
            self.logger.info("Account deleted", 
                           account_id=account_id,
                           tenant_id=tenant_id)
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to delete account", 
                            error=str(e),
                            account_id=account_id,
                            tenant_id=tenant_id)
            raise
    
    def get_account_balance(self, account_id: int, tenant_id: str) -> Decimal:
        """
        Get current account balance.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Current account balance
        """
        try:
            account = self.get_account_by_id(account_id, tenant_id)
            if not account:
                raise ValueError("Account not found")
            
            balance = account.effective_balance
            
            self.logger.debug("Account balance retrieved", 
                           account_id=account_id,
                           tenant_id=tenant_id,
                           balance=str(balance))
            
            return balance
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to get account balance", 
                            error=str(e),
                            account_id=account_id,
                            tenant_id=tenant_id)
            raise
    
    def validate_account_balance(self, account_id: int, tenant_id: str) -> bool:
        """
        Validate account balance consistency.
        
        Args:
            account_id: Account ID
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            True if balance is consistent, False otherwise
        """
        try:
            account = self.get_account_by_id(account_id, tenant_id)
            if not account:
                raise ValueError("Account not found")
            
            is_consistent = account.validate_balance_consistency()
            
            self.logger.debug("Account balance validation", 
                           account_id=account_id,
                           tenant_id=tenant_id,
                           is_consistent=is_consistent)
            
            return is_consistent
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to validate account balance", 
                            error=str(e),
                            account_id=account_id,
                            tenant_id=tenant_id)
            raise
    
    def get_account_stats(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get account statistics for a tenant.
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Dictionary with account statistics
        """
        try:
            total_accounts = self.db.query(Account).filter(
                Account.tenant_id == tenant_id,
                Account.is_deleted == False
            ).count()
            
            active_accounts = self.db.query(Account).filter(
                Account.tenant_id == tenant_id,
                Account.is_deleted == False,
                Account.is_active == True,
                Account.is_archived == False
            ).count()
            
            archived_accounts = self.db.query(Account).filter(
                Account.tenant_id == tenant_id,
                Account.is_deleted == False,
                Account.is_archived == True
            ).count()
            
            # Get total balance across all active accounts
            active_accounts_query = self.db.query(Account).filter(
                Account.tenant_id == tenant_id,
                Account.is_deleted == False,
                Account.is_active == True,
                Account.is_archived == False
            )
            
            total_balance = sum(account.effective_balance for account in active_accounts_query)
            
            # Get account type breakdown
            type_breakdown = {}
            for account_type in ['current', 'savings', 'credit', 'investment']:
                count = self.db.query(Account).filter(
                    Account.tenant_id == tenant_id,
                    Account.is_deleted == False,
                    Account.is_active == True,
                    Account.is_archived == False,
                    Account.account_type == account_type
                ).count()
                type_breakdown[account_type] = count
            
            stats = {
                'total_accounts': total_accounts,
                'active_accounts': active_accounts,
                'archived_accounts': archived_accounts,
                'total_balance': str(total_balance),
                'type_breakdown': type_breakdown
            }
            
            self.logger.debug("Account stats retrieved", 
                           tenant_id=tenant_id,
                           stats=stats)
            
            return stats
            
        except Exception as e:
            self.logger.error("Failed to get account stats", 
                            error=str(e),
                            tenant_id=tenant_id)
            raise
