"""
API server for the SaaS Cloner system.

This module defines the FastAPI application that serves as the central API
for interacting with the SaaS Cloner system.
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import logging

from api.routes import project, agents

# Create the FastAPI application
app = FastAPI(
    title="SaaS Cloner API",
    description="API for discovering, analyzing, and enhancing SaaS applications",
    version="0.1.0",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(project.router, prefix="/api/projects", tags=["projects"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])

@app.get("/")
async def root():
    """Root endpoint for the API server."""
    return {
        "name": "SaaS Cloner API",
        "version": "0.1.0",
        "description": "API for discovering, analyzing, and enhancing SaaS applications",
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for the API server."""
    return {
        "status": "healthy",
        "version": "0.1.0",
    }

@app.get("/api/info")
async def api_info():
    """Get information about the API endpoints."""
    return {
        "endpoints": {
            "projects": "Manage SaaS clone projects",
            "agents": "Interact with different agents in the system",
            "health": "Health check for the API server",
        },
        "version": "0.1.0",
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return {
        "error": {
            "code": exc.status_code,
            "message": exc.detail,
        }
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": {
            "code": 500,
            "message": "An unexpected error occurred",
        }
    }
