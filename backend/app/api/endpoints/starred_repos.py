"""
This module defines the routes used for retrieving starred repositories.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import httpx
from pydantic import ValidationError
from fastapi import Query
from app.schemas import Repository, StarredRepositoriesResponse
from app.dependencies import get_http_client, limiter, get_settings
from app.config import Settings

logger = logging.getLogger("uvicorn.error")

starred_repos_router = APIRouter()

@starred_repos_router.get("/getStarredRepos",
    summary="Start OAuth Flow",
    description="Redirects the user to GitHub for OAuth authorization. This is the initial step in the OAuth flow, where the user is asked to authorize the application. Upon authorization, GitHub redirects back to the `/callback` endpoint with an authorization code.",
    tags=["Starred Repos"])
@limiter.limit("30/minute")
async def getStarredRepos(request: Request, settings: Settings = Depends(get_settings)):
    """
    Redirects the user to GitHub for authorization.

    This endpoint initiates the OAuth flow by redirecting the user to GitHub, 
    asking them to authorize the application. After authorization, GitHub redirects 
    back to the `/callback` endpoint with an authorization code.
    """
    client_id = settings.client_id
    # TODO: should be https if in real use
    redirect_uri = settings.redirect_uri
    
    scope = "read:user,user:email"
    return RedirectResponse(url=f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}")

@starred_repos_router.get("/callback",
    summary="GitHub OAuth callback",
    description="Handles the callback from GitHub after user authorization. Exchanges the code for a token and fetches starred repos.",
    response_model=StarredRepositoriesResponse,
    responses={
    500: {
        "description": "Failed to connect to GitHub for access token or to fetch starred repositories."
    },
    502: {
        "description": "Error parsing GitHub response."
    },
    400: {
        "description": "Bad Request - issues with the request parameters."
    },
    },
    tags=["Starred Repos"])
@limiter.limit("30/minute")
async def callback(request: Request, settings: Settings = Depends(get_settings), client: httpx.AsyncClient = Depends(get_http_client), code: str = Query(..., description="Authorization code for GitHub api")):
    """
    Handles the callback from GitHub OAuth flow.

    This endpoint is where GitHub redirects the user after they authorize the application. 
    It uses the provided `code` to obtain an access token from GitHub, which is then used to 
    fetch and return the user's starred repositories. These starred repos are then parsed into
    StarredRepositoriesResponse form and returned.
    """
    client_id = settings.client_id
    client_secret = settings.client_secret
    # Attempt to get access token
    try:
        response = await client.post(
            'https://github.com/login/oauth/access_token',
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code
            },
            headers={'Accept': 'application/json'}
        )
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to get access token from GitHub: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to GitHub for access token.")
    
    access_token = response.json()['access_token']

    # Attempt to fetch starred repositories
    try:
        starred_repos_response = await client.get(
            'https://api.github.com/user/starred',
            headers={'Authorization': f'token {access_token}'}
        )
        print(starred_repos_response)
        starred_repos_response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch starred repositories from GitHub: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch starred repositories from GitHub.")

    starred_repos_data = starred_repos_response.json()

    # Parse and transform the response data
    try:
        repositories = [
            Repository(
                name=repo['name'],
                description=repo.get('description'),
                url=repo['html_url'],
                license=repo['license']['name'] if repo.get('license') else None,
                topics=repo.get('topics', [])
            ) for repo in starred_repos_data
        ]
        response_model = StarredRepositoriesResponse(
            count=len(repositories),
            repositories=repositories
        )
        return response_model
    except ValidationError as e:
        logger.error(f"Error parsing GitHub response: {e}")
        raise HTTPException(status_code=502, detail=f"Error parsing GitHub response: {e}")
