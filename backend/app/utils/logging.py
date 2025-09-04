"""
Logging utilities for TheTally backend.

This module provides structured logging utilities following the three-tier logging strategy:
1. Audit logs - Track who accesses information and what actions are taken
2. Functional logs - Record application usage actions
3. Debug logs - Record errors and internal system behavior

All logs are in JSON format with consistent field names and timestamps.
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import structlog
from structlog.stdlib import LoggerFactory
from app.core.config import settings

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


class LoggingUtils:
    """
    Logging utilities class providing structured logging with security context.
    """
    
    # Log retention periods (in days)
    AUDIT_RETENTION_DAYS = 2555  # 7 years
    FUNCTIONAL_RETENTION_DAYS = 365  # 1 year
    DEBUG_RETENTION_DAYS = 30  # 30 days
    
    @classmethod
    def get_audit_logger(cls, service_name: str = "audit") -> structlog.BoundLogger:
        """
        Get audit logger for security and compliance logging.
        
        Audit logs track:
        - User authentication events
        - Data access and modifications
        - Security events and violations
        - Administrative actions
        - Compliance-related activities
        
        Args:
            service_name: Name of the service for context
            
        Returns:
            Configured audit logger
        """
        return structlog.get_logger(service_name).bind(
            log_type="audit",
            retention_days=cls.AUDIT_RETENTION_DAYS,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @classmethod
    def get_functional_logger(cls, service_name: str = "functional") -> structlog.BoundLogger:
        """
        Get functional logger for business analytics logging.
        
        Functional logs track:
        - User actions and workflows
        - Business process execution
        - Feature usage and adoption
        - Performance metrics
        - User journey tracking
        
        Args:
            service_name: Name of the service for context
            
        Returns:
            Configured functional logger
        """
        return structlog.get_logger(service_name).bind(
            log_type="functional",
            retention_days=cls.FUNCTIONAL_RETENTION_DAYS,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @classmethod
    def get_debug_logger(cls, service_name: str = "debug") -> structlog.BoundLogger:
        """
        Get debug logger for development and AI context logging.
        
        Debug logs track:
        - Application errors and exceptions
        - Internal system behavior
        - AI assistant reasoning steps
        - Development and debugging information
        - Performance bottlenecks
        
        Args:
            service_name: Name of the service for context
            
        Returns:
            Configured debug logger
        """
        return structlog.get_logger(service_name).bind(
            log_type="debug",
            retention_days=cls.DEBUG_RETENTION_DAYS,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @classmethod
    def log_security_event(cls, event_type: str, user_id: Optional[str] = None,
                          tenant_id: Optional[str] = None, ip_address: Optional[str] = None,
                          user_agent: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a security event with comprehensive context.
        
        Args:
            event_type: Type of security event (login, logout, access_denied, etc.)
            user_id: ID of the user involved
            tenant_id: ID of the tenant
            ip_address: IP address of the request
            user_agent: User agent string
            details: Additional event details
        """
        audit_logger = cls.get_audit_logger("security")
        
        log_data = {
            "event_type": event_type,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
            "severity": cls._get_security_severity(event_type)
        }
        
        audit_logger.info("Security event", **log_data)
    
    @classmethod
    def log_user_action(cls, action: str, user_id: str, tenant_id: str,
                       resource_type: Optional[str] = None, resource_id: Optional[str] = None,
                       details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a user action for business analytics.
        
        Args:
            action: Action performed by the user
            user_id: ID of the user
            tenant_id: ID of the tenant
            resource_type: Type of resource affected
            resource_id: ID of the resource affected
            details: Additional action details
        """
        functional_logger = cls.get_functional_logger("user_actions")
        
        log_data = {
            "action": action,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {}
        }
        
        functional_logger.info("User action", **log_data)
    
    @classmethod
    def log_ai_context(cls, ai_action: str, reasoning: str, token_usage: Optional[int] = None,
                      decision_points: Optional[list] = None, service_name: str = "ai_assistant") -> None:
        """
        Log AI assistant context for debugging and development.
        
        Args:
            ai_action: Action performed by AI assistant
            reasoning: Reasoning behind the action
            token_usage: Number of tokens used
            decision_points: Key decision points in the process
            service_name: Name of the AI service
        """
        debug_logger = cls.get_debug_logger(service_name)
        
        log_data = {
            "ai_action": ai_action,
            "reasoning": reasoning,
            "token_usage": token_usage,
            "decision_points": decision_points or [],
            "ai_context": True
        }
        
        debug_logger.info("AI assistant context", **log_data)
    
    @classmethod
    def log_error(cls, error: Exception, context: Optional[Dict[str, Any]] = None,
                 service_name: str = "error") -> None:
        """
        Log an error with full context for debugging.
        
        Args:
            error: Exception that occurred
            context: Additional context about the error
            service_name: Name of the service where error occurred
        """
        debug_logger = cls.get_debug_logger(service_name)
        
        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "severity": "error"
        }
        
        debug_logger.error("Application error", **log_data, exc_info=True)
    
    @classmethod
    def log_performance(cls, operation: str, duration_ms: float, service_name: str = "performance",
                       details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log performance metrics for monitoring.
        
        Args:
            operation: Name of the operation
            duration_ms: Duration in milliseconds
            service_name: Name of the service
            details: Additional performance details
        """
        debug_logger = cls.get_debug_logger(service_name)
        
        log_data = {
            "operation": operation,
            "duration_ms": duration_ms,
            "details": details or {},
            "severity": "info"
        }
        
        debug_logger.info("Performance metric", **log_data)
    
    @classmethod
    def _get_security_severity(cls, event_type: str) -> str:
        """
        Determine security event severity based on event type.
        
        Args:
            event_type: Type of security event
            
        Returns:
            Severity level (low, medium, high, critical)
        """
        critical_events = ["brute_force_attack", "privilege_escalation", "data_breach"]
        high_events = ["access_denied", "invalid_token", "suspicious_activity"]
        medium_events = ["login_failed", "password_change", "2fa_failed"]
        low_events = ["login_success", "logout", "password_reset"]
        
        if event_type in critical_events:
            return "critical"
        elif event_type in high_events:
            return "high"
        elif event_type in medium_events:
            return "medium"
        elif event_type in low_events:
            return "low"
        else:
            return "medium"


# Convenience functions for easy access
def get_audit_logger(service_name: str = "audit") -> structlog.BoundLogger:
    """Get audit logger - convenience function."""
    return LoggingUtils.get_audit_logger(service_name)


def get_functional_logger(service_name: str = "functional") -> structlog.BoundLogger:
    """Get functional logger - convenience function."""
    return LoggingUtils.get_functional_logger(service_name)


def get_debug_logger(service_name: str = "debug") -> structlog.BoundLogger:
    """Get debug logger - convenience function."""
    return LoggingUtils.get_debug_logger(service_name)
