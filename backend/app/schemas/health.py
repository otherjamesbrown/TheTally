"""
Health check schemas
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str
    timestamp: str
    version: str
    environment: str

class DetailedHealthResponse(BaseModel):
    """Detailed health check response schema"""
    status: str
    timestamp: str
    version: str
    environment: str
    system: Optional[dict] = None
