"""
TheTally Backend Application
FastAPI application with health check endpoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import health, auth

# Create FastAPI application
app = FastAPI(
    title="TheTally API",
    description="Personal financial tracking application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to TheTally API",
        "version": "1.0.0",
        "docs": "/docs"
    }
