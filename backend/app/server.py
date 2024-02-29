"""
Server module for the Star Retriever API.

This module defines a function to create and configure an instance of the FastAPI application, incorporating various components such as API routers, middleware, and exception handlers to create a fully functional API server. The server is designed to enable users to authenticate via GitHub OAuth and retrieve a list of starred repositories.

Functions:
    create_app() -> FastAPI: Creates and returns a configured FastAPI application instance.
"""
import os
from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse

from app.dependencies import get_settings
from .api.endpoints.starred_repos import starred_repos_router as starred_repos_router
import httpx
from .middleware import ErrorLoggingMiddleware, SecurityHeadersMiddleware
import logging
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

def create_app() -> FastAPI:
    """
    Creates and configures an instance of the FastAPI application.

    Sets up CORS middleware, security headers, error logging, rate limiting, and includes API routers for handling specific paths. Additionally, defines a route for serving the favicon.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    # Determine if the app is running in production mode
    is_prod = get_settings().environment

    app = FastAPI(
        title="Star Retriever API",
        description="This API allows users to reach for the stars ie fetch starred Github repositories.",
        version="1.0.0",
        openapi_tags=[{
            "name": "Starred Repos",
            "description": "Endpoints related to fetching starred repositories",
        }],
        docs_url=None if is_prod else "/docs",
        redoc_url=None if is_prod else "/redoc",
    )

    # Configure CORS. This app is for demonstration only, so everything is allowed.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # Register the rate limit exceeded exception handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Add error logging middleware to the application
    app.add_middleware(ErrorLoggingMiddleware)

    # Include API routers
    app.include_router(starred_repos_router, prefix="/api")

    # Define favicon route
    @app.get('/favicon.ico', include_in_schema=False)
    async def favicon():
        """
        Serves the favicon.ico file.

        Returns:
            FileResponse: A response containing the favicon.ico file.
        """
        # Get the directory of the current file
        current_file_directory = os.path.dirname(os.path.realpath(__file__))
        # Construct the absolute path to the favicon
        favicon_path = os.path.join(current_file_directory, "favicon.ico")
        return FileResponse(favicon_path)

    return app
