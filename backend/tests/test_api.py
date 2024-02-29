import os
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import json
from httpx import Response
import pytest
# Import client
from app.server import create_app
import respx

# Calculate the path to the root of the project so that imports work (e.g., "backend" directory)
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

def load_mock_data():
    # Get the directory of the current file
    current_file_directory = os.path.dirname(os.path.realpath(__file__))
    # Construct the absolute path to the favicon
    favicon_path = os.path.join(current_file_directory, "mock_test_data.json")
    with open(favicon_path, 'r') as file:
        return json.load(file)

mock_data = load_mock_data()
mock_code = "123456789"

# Define env variables for tests
os.environ['CLIENT_ID'] = '12345'
os.environ['CLIENT_SECRET'] = '67890'
os.environ['ENVIRONMENT'] = 'prod'
os.environ['REDIRECT_URI'] = 'http://localhost:8000/api/callback'

@pytest.fixture
def mock_github_oauth():
    """
    Pytest fixture to mock GitHub OAuth and API responses using RESPX.

    Yields:
        None
    """
    with respx.mock:
        # Mock the GitHub OAuth token endpoint
        respx.post(
            "https://github.com/login/oauth/access_token",
            data={
                'client_id': os.getenv('CLIENT_ID'),
                'client_secret': os.getenv('CLIENT_SECRET'),
                'code': mock_code
            },
            headers={"Accept": "application/json"}
        ).respond(200, json={"access_token": "mock_access_token"})
            
        # Mock the GitHub API call to fetch starred repositories
        respx.get(
            "https://api.github.com/user/starred",
            headers={"Authorization": "token mock_access_token"}
        ).mock(return_value=Response(200, json=load_mock_data()["successful_response"]))
        yield

# This causes a warning that i think is recently fixed for TestClient?
client = TestClient(create_app())

def test_get_starred_repos_redirect():
    """
    Test the redirection to GitHub's OAuth authorization page.
    """
    response = client.get("/api/getStarredRepos")
    assert response.history[0].status_code == 307

    client_id = os.getenv('CLIENT_ID')
    redirect_uri = os.getenv('REDIRECT_URI')
    
    scope = "read:user,user:email"

    assert f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}" in response.history[0].headers["location"]

def test_callback(mock_github_oauth):
    """
    Test the callback endpoint after successful GitHub OAuth authorization.

    Verifies if the endpoint correctly handles the authorization code, exchanges it for an access token,
    fetches starred repositories, and returns the expected response structure.
    """
    response = client.get(f"/api/callback?code={mock_code}")

    assert response.status_code == 200
    # Define the expected response JSON structure
    expected_response = {
        "count": 2,
        "repositories": [
            {
                "name": "delivery-fee-calculator",
                "description": "Calculates delivery fee in 3 different programming languages",
                "url": "https://github.com/Tupsu-jy/delivery-fee-calculator",
                "license": None,
                "topics": ["almost-finished", "repetive"]
            },
            {
                "name": "kanban-exercise",
                "description": None,
                "url": "https://github.com/Tupsu-jy/kanban-exercise",
                "license": "The Unlicense",
                "topics": []
            }
        ]
    }
    # Compare the actual response JSON to the expected structure
    assert response.json() == expected_response