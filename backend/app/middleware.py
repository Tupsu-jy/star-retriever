"""
This module defines the middlewares for a FastAPI application.

Environment Variables:
    ENVIRONMENT: Determines the mode of operation ('development' or 'production'). In 'development' mode, detailed tracebacks are logged.

"""
import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("uvicorn.error")
is_dev_mode = os.getenv("ENVIRONMENT") == "dev"

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log exceptions and return generic error responses.

    Logs exceptions with detailed tracebacks in development mode and exception messages only in production.
    Returns a JSON response with a 500 status code on unhandled exceptions.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Intercepts exceptions, logs them, and returns a generic error response.

        Args:
            request: The incoming request.
            call_next: Callable for the next request handler.

        Returns:
            A JSONResponse indicating an internal server error for unhandled exceptions.
        """
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(f"Unhandled exception for request {request.method} {request.url.path}: {exc}" +
                        (f"\nTraceback: {traceback.format_exc()}" if is_dev_mode else ""))
            return JSONResponse(
                content={"detail": "An unexpected error occurred.", "error": str(exc)},
                status_code=500
            )
        
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to append security headers to all outgoing responses.

    Enhances security by adding `X-Frame-Options` set to 'DENY' to prevent clickjacking attacks,
    and `X-Content-Type-Options` set to 'nosniff' to prevent MIME type sniffing.

    Args:
        request: The incoming HTTP request.
        call_next: Function that proceeds with the request handling.

    Returns:
        Response object with added security headers.
    """
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response