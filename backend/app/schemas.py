"""
This module defines the data models used for the Star Retriever API.

These models are built using Pydantic, which provides data validation and settings management using Python type annotations.
"""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class Repository(BaseModel):
    """
    Represents a parsed repository object that is meant to be returned to user.

    Attributes:
        name (str): The name of the repository.
        description (Optional[str]): A brief description of the repository. Defaults to None.
        url (HttpUrl): The URL to the repository, must be a valid HTTP URL.
        license (Optional[str]): The license type under which the repository is released. Defaults to None.
        topics (List[str]): A list of topics associated with the repository. Defaults to an empty list.
    """
    name: str
    description: Optional[str] = None
    url: HttpUrl
    license: Optional[str] = None
    topics: List[str] = []

class StarredRepositoriesResponse(BaseModel):
    """
    A response structure for a list of starred repositories.

    Attributes:
        count (int): The total number of starred repositories.
        repositories (List[Repository]): A list of `Repository` instances representing the starred repositories.
    """
    count: int
    repositories: List[Repository]
