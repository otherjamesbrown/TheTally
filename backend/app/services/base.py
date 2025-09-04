"""
Base service class for TheTally backend.

This module provides a base service class that all other services inherit from.
It includes common functionality like database session management, logging,
error handling, and transaction management.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import structlog
from app.db.session import SessionLocal
from app.core.config import settings

# Type variable for service classes
T = TypeVar('T')

logger = structlog.get_logger(__name__)


class BaseService:
    """
    Base service class providing common functionality for all services.
    
    This class provides:
    - Database session management
    - Structured logging
    - Error handling and transaction management
    - Common utility methods
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the base service.
        
        Args:
            db_session: Optional database session. If not provided, a new session will be created.
        """
        self._db_session = db_session
        self._session_owner = db_session is None
        self.logger = logger.bind(service=self.__class__.__name__)
    
    @property
    def db(self) -> Session:
        """
        Get the database session.
        
        Returns:
            Database session instance
        """
        if self._db_session is None:
            self._db_session = SessionLocal()
        return self._db_session
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with proper cleanup."""
        self.close()
    
    def close(self):
        """Close the database session if we own it."""
        if self._session_owner and self._db_session:
            self._db_session.close()
            self._db_session = None
    
    async def commit(self) -> None:
        """
        Commit the current transaction.
        
        Raises:
            SQLAlchemyError: If commit fails
        """
        try:
            self.db.commit()
            self.logger.debug("Transaction committed successfully")
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error("Transaction commit failed", error=str(e))
            raise
    
    async def rollback(self) -> None:
        """
        Rollback the current transaction.
        """
        try:
            self.db.rollback()
            self.logger.debug("Transaction rolled back successfully")
        except SQLAlchemyError as e:
            self.logger.error("Transaction rollback failed", error=str(e))
            raise
    
    def get_by_id(self, model_class: Type[T], id: Any) -> Optional[T]:
        """
        Get a model instance by ID.
        
        Args:
            model_class: The SQLAlchemy model class
            id: The ID to search for
            
        Returns:
            Model instance or None if not found
        """
        try:
            instance = self.db.query(model_class).filter(model_class.id == id).first()
            self.logger.debug("Retrieved model by ID", model=model_class.__name__, id=id, found=instance is not None)
            return instance
        except SQLAlchemyError as e:
            self.logger.error("Failed to get model by ID", model=model_class.__name__, id=id, error=str(e))
            raise
    
    def get_by_field(self, model_class: Type[T], field_name: str, value: Any) -> Optional[T]:
        """
        Get a model instance by a specific field value.
        
        Args:
            model_class: The SQLAlchemy model class
            field_name: The field name to search by
            value: The value to search for
            
        Returns:
            Model instance or None if not found
        """
        try:
            field = getattr(model_class, field_name)
            instance = self.db.query(model_class).filter(field == value).first()
            self.logger.debug("Retrieved model by field", model=model_class.__name__, field=field_name, value=value, found=instance is not None)
            return instance
        except SQLAlchemyError as e:
            self.logger.error("Failed to get model by field", model=model_class.__name__, field=field_name, value=value, error=str(e))
            raise
    
    def get_all(self, model_class: Type[T], limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        Get all instances of a model class.
        
        Args:
            model_class: The SQLAlchemy model class
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            
        Returns:
            List of model instances
        """
        try:
            query = self.db.query(model_class)
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            instances = query.all()
            self.logger.debug("Retrieved all models", model=model_class.__name__, count=len(instances))
            return instances
        except SQLAlchemyError as e:
            self.logger.error("Failed to get all models", model=model_class.__name__, error=str(e))
            raise
    
    def create(self, model_class: Type[T], **kwargs) -> T:
        """
        Create a new model instance.
        
        Args:
            model_class: The SQLAlchemy model class
            **kwargs: Field values for the new instance
            
        Returns:
            Created model instance
        """
        try:
            instance = model_class(**kwargs)
            self.db.add(instance)
            self.db.flush()  # Flush to get the ID without committing
            self.logger.debug("Created new model", model=model_class.__name__, id=getattr(instance, 'id', None))
            return instance
        except SQLAlchemyError as e:
            self.logger.error("Failed to create model", model=model_class.__name__, error=str(e))
            raise
    
    def update(self, instance: T, **kwargs) -> T:
        """
        Update an existing model instance.
        
        Args:
            instance: The model instance to update
            **kwargs: Field values to update
            
        Returns:
            Updated model instance
        """
        try:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            self.db.flush()
            self.logger.debug("Updated model", model=instance.__class__.__name__, id=getattr(instance, 'id', None))
            return instance
        except SQLAlchemyError as e:
            self.logger.error("Failed to update model", model=instance.__class__.__name__, error=str(e))
            raise
    
    def delete(self, instance: T) -> None:
        """
        Delete a model instance.
        
        Args:
            instance: The model instance to delete
        """
        try:
            self.db.delete(instance)
            self.logger.debug("Deleted model", model=instance.__class__.__name__, id=getattr(instance, 'id', None))
        except SQLAlchemyError as e:
            self.logger.error("Failed to delete model", model=instance.__class__.__name__, error=str(e))
            raise
    
    def exists(self, model_class: Type[T], **filters) -> bool:
        """
        Check if a model instance exists with the given filters.
        
        Args:
            model_class: The SQLAlchemy model class
            **filters: Field filters to check
            
        Returns:
            True if instance exists, False otherwise
        """
        try:
            query = self.db.query(model_class)
            for field_name, value in filters.items():
                field = getattr(model_class, field_name)
                query = query.filter(field == value)
            
            exists = query.first() is not None
            self.logger.debug("Checked model existence", model=model_class.__name__, filters=filters, exists=exists)
            return exists
        except SQLAlchemyError as e:
            self.logger.error("Failed to check model existence", model=model_class.__name__, filters=filters, error=str(e))
            raise
