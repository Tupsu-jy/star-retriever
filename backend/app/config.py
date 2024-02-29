"""
This module defines the configuration settings.
"""
from pydantic import Field, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configuration settings for the application, loaded from environment variables.

    Attributes:
        environment (str): Specifies the application's environment. Possible values are 'dev' for development and 'prod' for production. 
                           This setting determines various runtime behaviors, such as logging levels and database connection details. 
                           It defaults to "dev" but can be overridden by setting the `ENVIRONMENT` environment variable.

        client_id (str): The client ID used for OAuth authentication with GitHub. 
                         It is essential for initiating the OAuth flow and is expected to be provided as the `CLIENT_ID` environment variable.

        client_secret (str): The client secret corresponding to the `client_id`. 
                             Used for OAuth authentication with GitHub to secure the application's OAuth flow. 
                             It expects the `CLIENT_SECRET` environment variable to be set.

        redirect_uri (str): The URI to which GitHub will redirect the user after authorization has been granted. 
                            It defaults to "http://localhost:8000/api/callback" but can be overridden by setting the `REDIRECT_URI` environment variable.
    """
    environment: str = Field(default="dev", env="ENVIRONMENT")
    client_id: str = Field(..., env="CLIENT_ID")
    client_secret: str = Field(..., env="CLIENT_SECRET")
    redirect_uri: str = Field(default="http://localhost:8000/api/callback", env="REDIRECT_URI")

    @validator("client_id", "client_secret", pre=True, always=True)
    def not_empty(cls, v):
        if not v:
            raise ValueError("must not be empty")
        return v