"""
Defines dependencies used across the FastAPI application.
"""

import httpx
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import Settings

# Setup for application rate limiting
limiter = Limiter(key_func=get_remote_address)
"""
Rate limiter instance leveraging client IP addresses for limiting request rates.
Utilizes `slowapi` for FastAPI compatibility.
"""

def get_settings() -> Settings:
    """
    Fetches application settings from environment variables.

    Returns a Pydantic `Settings` model instance from `app.config`, encapsulating 
    configuration settings in a type-safe manner.

    Returns:
        An instance of `Settings` with application configuration.
    """
    return Settings()

def get_http_client() -> httpx.AsyncClient:
    """
    Provides a factory for `httpx.AsyncClient` instances.

    Facilitates asynchronous HTTP requests within the application using `httpx`.

    Returns:
        An instance of `httpx.AsyncClient`.
    """
    return httpx.AsyncClient()
