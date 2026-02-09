import asyncio
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import logging

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from db.models import GitHubProfile, APIUsageLog
from schemas import GitHubProfileResponse, APIProvider

# Configure logging
logger = logging.getLogger(__name__)

# Constants
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 60  # seconds


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class GitHubRateLimitError(GitHubAPIError):
    """Exception raised when GitHub API rate limit is exceeded."""
    pass


class GitHubService:
    """Service for interacting with the GitHub API."""
    
    def __init__(self):
        self.api_token = os.getenv("GITHUB_TOKEN")
        self.base_url = GITHUB_API_BASE_URL
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
            "User-Agent": "Tshimbiluni-Portfolio-Bot/1.0"
        }
        
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"
        else:
            logger.warning("GitHub API token not provided. Rate limits will be lower.")
    
    async def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the GitHub API with proper error handling.
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method
            params: Query parameters
            session: Database session for logging
            
        Returns:
            API response data
            
        Raises:
            GitHubAPIError: For API-related errors
            GitHubRateLimitError: For rate limit errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = datetime.now(timezone.utc)
        
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params or {}
                )
                
                # Calculate response time
                response_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                
                # Log API usage
                if session:
                    await self._log_api_usage(
                        session=session,
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status_code,
                        response_time_ms=response_time_ms,
                        error_message=None if response.is_success else response.text
                    )
                
                # Handle rate limiting
                if response.status_code == 403:
                    rate_limit_remaining = response.headers.get("X-RateLimit-Remaining", "0")
                    if rate_limit_remaining == "0":
                        reset_time = response.headers.get("X-RateLimit-Reset", "")
                        raise GitHubRateLimitError(
                            f"GitHub API rate limit exceeded. Reset at: {reset_time}",
                            status_code=response.status_code,
                            response_data=response.json() if response.content else None
                        )
                
                # Handle other HTTP errors
                if not response.is_success:
                    error_data = response.json() if response.content else {}
                    raise GitHubAPIError(
                        f"GitHub API error: {response.status_code} - {error_data.get('message', 'Unknown error')}",
                        status_code=response.status_code,
                        response_data=error_data
                    )
                
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Request error for GitHub API: {e}")
            if session:
                await self._log_api_usage(
                    session=session,
                    endpoint=endpoint,
                    method=method,
                    status_code=None,
                    response_time_ms=int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000),
                    error_message=str(e)
                )
            raise GitHubAPIError(f"Request failed: {e}")
    
    async def _log_api_usage(
        self,
        session: AsyncSession,
        endpoint: str,
        method: str,
        status_code: Optional[int],
        response_time_ms: int,
        error_message: Optional[str] = None
    ) -> None:
        """Log API usage for monitoring and analytics."""
        try:
            log_entry = APIUsageLog(
                api_provider=APIProvider.GITHUB,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time_ms=response_time_ms,
                error_message=error_message,
                request_metadata={
                    "has_token": bool(self.api_token),
                    "user_agent": self.headers.get("User-Agent")
                }
            )
            session.add(log_entry)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to log API usage: {e}")
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.RequestError, GitHubRateLimitError))
    )
    async def fetch_user_profile(
        self,
        username: str,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Fetch user profile data from GitHub API.
        
        Args:
            username: GitHub username
            session: Database session for logging
            
        Returns:
            User profile data
        """
        logger.info(f"Fetching GitHub profile for user: {username}")
        
        profile_data = await self._make_request(
            endpoint=f"users/{username}",
            session=session
        )
        
        # Transform API response to our schema
        return {
            "username": username.lower(),
            "bio": profile_data.get("bio"),
            "public_repos": profile_data.get("public_repos", 0),
            "followers": profile_data.get("followers", 0),
            "following": profile_data.get("following", 0),
            "profile_url": profile_data.get("html_url"),
            "avatar_url": profile_data.get("avatar_url"),
            "name": profile_data.get("name"),
            "company": profile_data.get("company"),
            "location": profile_data.get("location"),
            "blog": profile_data.get("blog") if profile_data.get("blog") else None,
            "twitter_username": profile_data.get("twitter_username"),
            "hireable": profile_data.get("hireable"),
            "last_fetched_at": datetime.now(timezone.utc)
        }
    
    async def fetch_user_repositories(
        self,
        username: str,
        page: int = 1,
        per_page: int = 30,
        session: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch user repositories from GitHub API.
        
        Args:
            username: GitHub username
            page: Page number for pagination
            per_page: Number of repositories per page
            session: Database session for logging
            
        Returns:
            List of repository data
        """
        logger.info(f"Fetching repositories for user: {username} (page {page})")
        
        repos_data = await self._make_request(
            endpoint=f"users/{username}/repos",
            params={
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc"
            },
            session=session
        )
        
        return repos_data
    
    async def check_rate_limit(self, session: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        Check current rate limit status.
        
        Args:
            session: Database session for logging
            
        Returns:
            Rate limit information
        """
        return await self._make_request(
            endpoint="rate_limit",
            session=session
        )


# Service instance
github_service = GitHubService()


async def fetch_github_data(
    username: str,
    force_refresh: bool = False,
    session: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Fetch GitHub profile data with caching logic.
    
    Args:
        username: GitHub username to fetch
        force_refresh: Force refresh even if data is not stale
        session: Database session
        
    Returns:
        GitHub profile data
        
    Raises:
        GitHubAPIError: For API-related errors
    """
    if not session:
        raise ValueError("Database session is required")
    
    # Check if we have existing data and if it's stale
    if not force_refresh:
        result = await session.execute(
            select(GitHubProfile).where(GitHubProfile.username == username.lower())
        )
        existing_profile = result.scalar_one_or_none()
        
        if existing_profile and not existing_profile.is_data_stale:
            logger.info(f"Using cached GitHub data for {username}")
            return {
                "username": existing_profile.username,
                "bio": existing_profile.bio,
                "public_repos": existing_profile.public_repos,
                "followers": existing_profile.followers,
                "following": existing_profile.following,
                "profile_url": existing_profile.profile_url,
                "avatar_url": existing_profile.avatar_url,
                "name": existing_profile.name,
                "company": existing_profile.company,
                "location": existing_profile.location,
                "blog": existing_profile.blog,
                "twitter_username": existing_profile.twitter_username,
                "hireable": existing_profile.hireable,
                "last_fetched_at": existing_profile.last_fetched_at
            }
    
    # Fetch fresh data from API
    return await github_service.fetch_user_profile(username, session)


async def save_github_profile(
    session: AsyncSession,
    profile_data: Dict[str, Any]
) -> GitHubProfile:
    """
    Save or update GitHub profile data in the database.
    
    Args:
        session: Database session
        profile_data: Profile data to save
        
    Returns:
        Saved GitHubProfile instance
    """
    username = profile_data["username"].lower()
    
    # Check if profile exists
    result = await session.execute(
        select(GitHubProfile).where(GitHubProfile.username == username)
    )
    existing_profile = result.scalar_one_or_none()
    
    if existing_profile:
        # Update existing profile
        await session.execute(
            update(GitHubProfile)
            .where(GitHubProfile.username == username)
            .values(**profile_data)
        )
        await session.commit()
        
        # Fetch updated profile
        result = await session.execute(
            select(GitHubProfile).where(GitHubProfile.username == username)
        )
        updated_profile = result.scalar_one()
        logger.info(f"Updated GitHub profile for {username}")
        return updated_profile
    else:
        # Create new profile
        new_profile = GitHubProfile(**profile_data)
        session.add(new_profile)
        await session.commit()
        await session.refresh(new_profile)
        logger.info(f"Created new GitHub profile for {username}")
        return new_profile


async def get_github_profile(
    session: AsyncSession,
    username: str
) -> Optional[GitHubProfile]:
    """
    Get GitHub profile from database.
    
    Args:
        session: Database session
        username: GitHub username
        
    Returns:
        GitHubProfile instance or None
    """
    result = await session.execute(
        select(GitHubProfile).where(GitHubProfile.username == username.lower())
    )
    return result.scalar_one_or_none()


async def sync_github_profile(
    session: AsyncSession,
    username: str,
    force_refresh: bool = False
) -> GitHubProfileResponse:
    """
    Sync GitHub profile data (fetch and save).
    
    Args:
        session: Database session
        username: GitHub username to sync
        force_refresh: Force refresh even if data is not stale
        
    Returns:
        GitHubProfileResponse with synced data
    """
    try:
        # Fetch data from API
        profile_data = await fetch_github_data(username, force_refresh, session)
        
        # Save to database
        saved_profile = await save_github_profile(session, profile_data)
        
        # Return response schema
        return GitHubProfileResponse.model_validate(saved_profile)
        
    except GitHubAPIError as e:
        logger.error(f"GitHub API error while syncing {username}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while syncing GitHub profile {username}: {e}")
        raise GitHubAPIError(f"Failed to sync GitHub profile: {e}")