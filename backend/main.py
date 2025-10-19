"""
ChainIntel Backend API
Main FastAPI application entry point
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from routes import dimo, analytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting ChainIntel Backend API...")
    logger.info(f"Environment: {settings.dimo_environment}")
    yield
    # Shutdown
    logger.info("Shutting down ChainIntel Backend API...")


# Create FastAPI app
app = FastAPI(
    title="ChainIntel API",
    description="AI-powered analytics platform for DePIN infrastructure",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dimo.router)
app.include_router(analytics.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ChainIntel API",
        "version": "1.0.0",
        "description": "AI-powered analytics platform for DePIN infrastructure",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "dimo": "/api/dimo",
            "analytics": "/api/analytics"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.dimo_environment
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
