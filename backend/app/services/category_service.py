"""
Category service for TheTally backend.

This module provides category management services including CRUD operations,
hierarchy management, and category analytics.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
import structlog
from datetime import datetime

from app.models.category import Category
from app.services.base import BaseService

# Get logger
logger = structlog.get_logger(__name__)


class CategoryService(BaseService):
    """
    Category service providing comprehensive category management operations.
    
    This service extends the base service with category-specific functionality:
    - Category CRUD operations
    - Hierarchy management
    - Category analytics and usage tracking
    - Budget management
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the category service.
        
        Args:
            db_session: Optional database session. If not provided, a new session will be created.
        """
        super().__init__(db_session)
        self.logger = logger.bind(service="CategoryService")
    
    def create_category(self, name: str, category_type: str, tenant_id: str,
                       parent_id: Optional[int] = None, user_id: str = None,
                       **kwargs) -> Category:
        """
        Create a new category.
        
        Args:
            name: Category name
            category_type: Type of category (income, expense, transfer, other)
            tenant_id: Tenant ID for multi-tenant support
            parent_id: Optional parent category ID
            user_id: Owner user ID (optional, for user-specific categories)
            **kwargs: Additional category fields
            
        Returns:
            Created category object
            
        Raises:
            ValueError: If validation fails
            Exception: If category creation fails
        """
        try:
            # Validate category type
            valid_types = ['income', 'expense', 'transfer', 'other']
            if category_type not in valid_types:
                raise ValueError(f"Invalid category type. Must be one of: {valid_types}")
            
            # Generate slug from name
            slug = self._generate_slug(name)
            
            # Check if slug already exists
            existing_category = self.get_category_by_slug(slug, tenant_id)
            if existing_category:
                # Append number to make slug unique
                counter = 1
                while existing_category:
                    new_slug = f"{slug}-{counter}"
                    existing_category = self.get_category_by_slug(new_slug, tenant_id)
                    if not existing_category:
                        slug = new_slug
                        break
                    counter += 1
            
            # Validate parent category if provided
            if parent_id:
                parent_category = self.get_category_by_id(parent_id, tenant_id)
                if not parent_category:
                    raise ValueError("Parent category not found")
                if parent_category.category_type != category_type:
                    raise ValueError("Parent category must have the same type")
            
            # Set default values
            category_data = {
                'name': name,
                'slug': slug,
                'category_type': category_type,
                'parent_id': parent_id,
                'tenant_id': tenant_id,
                'user_id': user_id,
                'is_active': True,
                'is_default': False,
                'is_system': False,
                'usage_count': 0
            }
            
            # Add additional fields
            category_data.update(kwargs)
            
            # Create category
            category = self.create(Category, **category_data)
            
            self.logger.info("Category created successfully", 
                           category_id=str(category.id),
                           name=name,
                           category_type=category_type,
                           tenant_id=tenant_id)
            
            return category
            
        except IntegrityError as e:
            self.logger.error("Category creation failed due to database constraint", 
                            error=str(e),
                            name=name,
                            category_type=category_type)
            raise ValueError("Category creation failed due to constraint violation")
        except Exception as e:
            self.logger.error("Category creation failed", 
                            error=str(e),
                            name=name,
                            category_type=category_type)
            raise
    
    def get_category_by_id(self, category_id: int, tenant_id: str) -> Optional[Category]:
        """
        Get category by ID.
        
        Args:
            category_id: Category ID
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Category object if found, None otherwise
        """
        try:
            category = self.db.query(Category).filter(
                Category.id == category_id,
                Category.tenant_id == tenant_id,
                Category.is_deleted == False
            ).first()
            
            if category:
                self.logger.debug("Category retrieved by ID", 
                               category_id=category_id,
                               tenant_id=tenant_id)
            else:
                self.logger.warning("Category not found by ID", 
                                  category_id=category_id,
                                  tenant_id=tenant_id)
            
            return category
            
        except Exception as e:
            self.logger.error("Failed to get category by ID", 
                            error=str(e),
                            category_id=category_id,
                            tenant_id=tenant_id)
            raise
    
    def get_category_by_slug(self, slug: str, tenant_id: str) -> Optional[Category]:
        """
        Get category by slug.
        
        Args:
            slug: Category slug
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Category object if found, None otherwise
        """
        try:
            category = self.db.query(Category).filter(
                Category.slug == slug,
                Category.tenant_id == tenant_id,
                Category.is_deleted == False
            ).first()
            
            if category:
                self.logger.debug("Category retrieved by slug", 
                               slug=slug,
                               tenant_id=tenant_id)
            else:
                self.logger.warning("Category not found by slug", 
                                  slug=slug,
                                  tenant_id=tenant_id)
            
            return category
            
        except Exception as e:
            self.logger.error("Failed to get category by slug", 
                            error=str(e),
                            slug=slug,
                            tenant_id=tenant_id)
            raise
    
    def get_categories_by_type(self, category_type: str, tenant_id: str,
                              active_only: bool = True) -> List[Category]:
        """
        Get categories by type.
        
        Args:
            category_type: Type of category
            tenant_id: Tenant ID for multi-tenant support
            active_only: Whether to return only active categories
            
        Returns:
            List of category objects
        """
        try:
            query = self.db.query(Category).filter(
                Category.category_type == category_type,
                Category.tenant_id == tenant_id,
                Category.is_deleted == False
            )
            
            if active_only:
                query = query.filter(Category.is_active == True)
            
            categories = query.order_by(Category.name).all()
            
            self.logger.debug("Categories retrieved by type", 
                           category_type=category_type,
                           tenant_id=tenant_id,
                           count=len(categories),
                           active_only=active_only)
            
            return categories
            
        except Exception as e:
            self.logger.error("Failed to get categories by type", 
                            error=str(e),
                            category_type=category_type,
                            tenant_id=tenant_id)
            raise
    
    def get_root_categories(self, tenant_id: str, category_type: str = None,
                           active_only: bool = True) -> List[Category]:
        """
        Get root categories (no parent).
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            category_type: Optional category type filter
            active_only: Whether to return only active categories
            
        Returns:
            List of root category objects
        """
        try:
            query = self.db.query(Category).filter(
                Category.parent_id.is_(None),
                Category.tenant_id == tenant_id,
                Category.is_deleted == False
            )
            
            if category_type:
                query = query.filter(Category.category_type == category_type)
            if active_only:
                query = query.filter(Category.is_active == True)
            
            categories = query.order_by(Category.name).all()
            
            self.logger.debug("Root categories retrieved", 
                           tenant_id=tenant_id,
                           category_type=category_type,
                           count=len(categories),
                           active_only=active_only)
            
            return categories
            
        except Exception as e:
            self.logger.error("Failed to get root categories", 
                            error=str(e),
                            tenant_id=tenant_id,
                            category_type=category_type)
            raise
    
    def get_subcategories(self, parent_id: int, tenant_id: str,
                          active_only: bool = True) -> List[Category]:
        """
        Get subcategories of a parent category.
        
        Args:
            parent_id: Parent category ID
            tenant_id: Tenant ID for multi-tenant support
            active_only: Whether to return only active categories
            
        Returns:
            List of subcategory objects
        """
        try:
            query = self.db.query(Category).filter(
                Category.parent_id == parent_id,
                Category.tenant_id == tenant_id,
                Category.is_deleted == False
            )
            
            if active_only:
                query = query.filter(Category.is_active == True)
            
            categories = query.order_by(Category.name).all()
            
            self.logger.debug("Subcategories retrieved", 
                           parent_id=parent_id,
                           tenant_id=tenant_id,
                           count=len(categories),
                           active_only=active_only)
            
            return categories
            
        except Exception as e:
            self.logger.error("Failed to get subcategories", 
                            error=str(e),
                            parent_id=parent_id,
                            tenant_id=tenant_id)
            raise
    
    def search_categories(self, tenant_id: str, search_term: str,
                          category_type: str = None, limit: Optional[int] = None) -> List[Category]:
        """
        Search categories by name.
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            search_term: Search term
            category_type: Optional category type filter
            limit: Optional limit on number of results
            
        Returns:
            List of matching category objects
        """
        try:
            query = self.db.query(Category).filter(
                Category.tenant_id == tenant_id,
                Category.is_deleted == False,
                Category.is_active == True
            ).filter(
                Category.name.ilike(f"%{search_term}%")
            )
            
            if category_type:
                query = query.filter(Category.category_type == category_type)
            
            query = query.order_by(Category.name)
            
            if limit:
                query = query.limit(limit)
            
            categories = query.all()
            
            self.logger.debug("Categories searched", 
                           tenant_id=tenant_id,
                           search_term=search_term[:10] + "***",
                           category_type=category_type,
                           count=len(categories))
            
            return categories
            
        except Exception as e:
            self.logger.error("Failed to search categories", 
                            error=str(e),
                            tenant_id=tenant_id,
                            search_term=search_term[:10] + "***")
            raise
    
    def update_category(self, category_id: int, tenant_id: str,
                       update_data: Dict[str, Any], updated_by: str = None) -> Category:
        """
        Update category information.
        
        Args:
            category_id: Category ID
            tenant_id: Tenant ID for multi-tenant support
            update_data: Dictionary of fields to update
            updated_by: User ID who updated this category
            
        Returns:
            Updated category object
            
        Raises:
            ValueError: If category not found or validation fails
        """
        try:
            category = self.get_category_by_id(category_id, tenant_id)
            if not category:
                raise ValueError("Category not found")
            
            # Validate category type if being updated
            if 'category_type' in update_data:
                valid_types = ['income', 'expense', 'transfer', 'other']
                if update_data['category_type'] not in valid_types:
                    raise ValueError(f"Invalid category type. Must be one of: {valid_types}")
            
            # Update slug if name is being updated
            if 'name' in update_data and update_data['name'] != category.name:
                new_slug = self._generate_slug(update_data['name'])
                # Check if new slug already exists
                existing_category = self.get_category_by_slug(new_slug, tenant_id)
                if existing_category and existing_category.id != category_id:
                    # Append number to make slug unique
                    counter = 1
                    while existing_category:
                        new_slug_with_counter = f"{new_slug}-{counter}"
                        existing_category = self.get_category_by_slug(new_slug_with_counter, tenant_id)
                        if not existing_category or existing_category.id == category_id:
                            new_slug = new_slug_with_counter
                            break
                        counter += 1
                update_data['slug'] = new_slug
            
            # Update category
            self.update(category, **update_data)
            if updated_by:
                category.updated_by = updated_by
            category.update_audit_fields(updated_by)
            
            self.logger.info("Category updated successfully", 
                           category_id=category_id,
                           tenant_id=tenant_id)
            
            return category
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to update category", 
                            error=str(e),
                            category_id=category_id,
                            tenant_id=tenant_id)
            raise
    
    def increment_usage(self, category_id: int, tenant_id: str) -> Category:
        """
        Increment category usage count.
        
        Args:
            category_id: Category ID
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Updated category object
        """
        try:
            category = self.get_category_by_id(category_id, tenant_id)
            if not category:
                raise ValueError("Category not found")
            
            category.increment_usage()
            
            self.logger.debug("Category usage incremented", 
                           category_id=category_id,
                           tenant_id=tenant_id,
                           new_count=category.usage_count)
            
            return category
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to increment category usage", 
                            error=str(e),
                            category_id=category_id,
                            tenant_id=tenant_id)
            raise
    
    def set_budget(self, category_id: int, tenant_id: str, amount: Decimal,
                   period: str = "monthly", start_date: datetime = None,
                   end_date: datetime = None, updated_by: str = None) -> Category:
        """
        Set budget for a category.
        
        Args:
            category_id: Category ID
            tenant_id: Tenant ID for multi-tenant support
            amount: Budget amount
            period: Budget period (monthly, yearly, etc.)
            start_date: Budget start date
            end_date: Budget end date
            updated_by: User ID who set this budget
            
        Returns:
            Updated category object
        """
        try:
            category = self.get_category_by_id(category_id, tenant_id)
            if not category:
                raise ValueError("Category not found")
            
            category.set_budget(amount, period, start_date, end_date)
            if updated_by:
                category.updated_by = updated_by
            category.update_audit_fields(updated_by)
            
            self.logger.info("Category budget set", 
                           category_id=category_id,
                           tenant_id=tenant_id,
                           amount=str(amount),
                           period=period)
            
            return category
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to set category budget", 
                            error=str(e),
                            category_id=category_id,
                            tenant_id=tenant_id)
            raise
    
    def clear_budget(self, category_id: int, tenant_id: str,
                    updated_by: str = None) -> Category:
        """
        Clear budget for a category.
        
        Args:
            category_id: Category ID
            tenant_id: Tenant ID for multi-tenant support
            updated_by: User ID who cleared this budget
            
        Returns:
            Updated category object
        """
        try:
            category = self.get_category_by_id(category_id, tenant_id)
            if not category:
                raise ValueError("Category not found")
            
            category.clear_budget()
            if updated_by:
                category.updated_by = updated_by
            category.update_audit_fields(updated_by)
            
            self.logger.info("Category budget cleared", 
                           category_id=category_id,
                           tenant_id=tenant_id)
            
            return category
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to clear category budget", 
                            error=str(e),
                            category_id=category_id,
                            tenant_id=tenant_id)
            raise
    
    def archive_category(self, category_id: int, tenant_id: str,
                        archived_by: str = None) -> Category:
        """
        Archive a category.
        
        Args:
            category_id: Category ID
            tenant_id: Tenant ID for multi-tenant support
            archived_by: User ID who archived this category
            
        Returns:
            Archived category object
        """
        try:
            category = self.get_category_by_id(category_id, tenant_id)
            if not category:
                raise ValueError("Category not found")
            
            # Check if category can be deleted (has subcategories)
            if not category.can_be_deleted():
                raise ValueError("Category cannot be archived because it has subcategories or high usage")
            
            category.archive(archived_by)
            
            self.logger.info("Category archived", 
                           category_id=category_id,
                           tenant_id=tenant_id)
            
            return category
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to archive category", 
                            error=str(e),
                            category_id=category_id,
                            tenant_id=tenant_id)
            raise
    
    def delete_category(self, category_id: int, tenant_id: str,
                       deleted_by: str = None) -> None:
        """
        Soft delete a category.
        
        Args:
            category_id: Category ID
            tenant_id: Tenant ID for multi-tenant support
            deleted_by: User ID who deleted this category
        """
        try:
            category = self.get_category_by_id(category_id, tenant_id)
            if not category:
                raise ValueError("Category not found")
            
            # Check if category can be deleted
            if not category.can_be_deleted():
                raise ValueError("Category cannot be deleted because it has subcategories or high usage")
            
            category.soft_delete(deleted_by)
            
            self.logger.info("Category deleted", 
                           category_id=category_id,
                           tenant_id=tenant_id)
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error("Failed to delete category", 
                            error=str(e),
                            category_id=category_id,
                            tenant_id=tenant_id)
            raise
    
    def get_category_stats(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get category statistics for a tenant.
        
        Args:
            tenant_id: Tenant ID for multi-tenant support
            
        Returns:
            Dictionary with category statistics
        """
        try:
            total_categories = self.db.query(Category).filter(
                Category.tenant_id == tenant_id,
                Category.is_deleted == False
            ).count()
            
            active_categories = self.db.query(Category).filter(
                Category.tenant_id == tenant_id,
                Category.is_deleted == False,
                Category.is_active == True
            ).count()
            
            system_categories = self.db.query(Category).filter(
                Category.tenant_id == tenant_id,
                Category.is_deleted == False,
                Category.is_system == True
            ).count()
            
            # Get type breakdown
            type_breakdown = {}
            for category_type in ['income', 'expense', 'transfer', 'other']:
                count = self.db.query(Category).filter(
                    Category.tenant_id == tenant_id,
                    Category.is_deleted == False,
                    Category.is_active == True,
                    Category.category_type == category_type
                ).count()
                type_breakdown[category_type] = count
            
            # Get most used categories
            most_used = self.db.query(Category).filter(
                Category.tenant_id == tenant_id,
                Category.is_deleted == False,
                Category.is_active == True
            ).order_by(Category.usage_count.desc()).limit(5).all()
            
            most_used_data = [
                {
                    'id': cat.id,
                    'name': cat.name,
                    'usage_count': cat.usage_count,
                    'category_type': cat.category_type
                }
                for cat in most_used
            ]
            
            stats = {
                'total_categories': total_categories,
                'active_categories': active_categories,
                'inactive_categories': total_categories - active_categories,
                'system_categories': system_categories,
                'user_categories': total_categories - system_categories,
                'type_breakdown': type_breakdown,
                'most_used_categories': most_used_data
            }
            
            self.logger.debug("Category stats retrieved", 
                           tenant_id=tenant_id,
                           stats=stats)
            
            return stats
            
        except Exception as e:
            self.logger.error("Failed to get category stats", 
                            error=str(e),
                            tenant_id=tenant_id)
            raise
    
    def _generate_slug(self, name: str) -> str:
        """
        Generate a URL-friendly slug from a name.
        
        Args:
            name: Category name
            
        Returns:
            URL-friendly slug
        """
        import re
        
        # Convert to lowercase and replace spaces with hyphens
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = slug.strip('-')
        
        return slug
