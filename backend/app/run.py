"""
Launches the FastAPI application with optional debug support.

This script initializes the FastAPI application by importing the application instance 
from `app.server` and then running it with Uvicorn. It checks the application's environment 
setting to determine if it should run in development mode with an attached debugger.

In development mode, the script utilizes `debugpy` to enable debugging support, listening 
on all network interfaces at port 5678. This allows for attaching a remote debugger to 
the process for troubleshooting and development purposes.

Attributes:
    app (FastAPI): The FastAPI application instance, created by calling `create_app()`.

Functions:
    start(): Configures and runs the FastAPI application server. In development mode, 
             it also sets up and waits for a debugger connection.
"""

from fastapi import FastAPI
import uvicorn
from app.config import Settings
from app.server import create_app
from pydantic import ValidationError

app: FastAPI = create_app()

def validate_env_variables():
    """
    Validates that all required environment variables are set.

    Utilizes the Settings model to verify that all environment variables needed
    for the application's configuration are present and valid. If any variables
    are missing or invalid, a ValidationError is raised.

    Raises:
        ValidationError: If any required environment variables are missing or invalid.
    """
    try:
        Settings()
    except ValidationError as e:
        raise RuntimeError("CLIENT_SECRET and CLIENT_ID need to be defined. Environment variable validation error: {e}")

def start():
    """
    Starts the FastAPI application with Uvicorn, with optional debug support.

    Validates required environment variables before starting the server.
    In development mode ('dev'), it also starts a debug server using `debugpy`, 
    which listens for incoming debugger connections. Otherwise, it runs the 
    application in production mode without debug support.
    """
    try:
        validate_env_variables()
    except RuntimeError as e:
        print(e)
        # Stop execution if environment variables are not set correctly
        return  

    settings = Settings()
    if settings.environment == 'dev':
        # Enables debugger
        import debugpy
        debugpy.listen(("0.0.0.0", 5678))

        uvicorn.run("app.run:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
    else:
        # TODO: replace with gunicorn
        uvicorn.run("app.run:app", host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    start()
