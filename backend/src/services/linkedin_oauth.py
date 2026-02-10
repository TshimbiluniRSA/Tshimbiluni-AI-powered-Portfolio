import logging
import os
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from urllib.parse import urlencode

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from db.models import LinkedInProfile, APIUsageLog

logger = logging.getLogger(__name__)


class LinkedInOAuthError(Exception):
    """Custom exception for LinkedIn OAuth errors."""
    pass


class LinkedInOAuthService:
    """Service for LinkedIn OAuth 2.0 authentication and data fetching."""
    
    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/api/linkedin/oauth/callback")
        self.base_url = "https://api.linkedin.com/v2"
        self.oauth_url = "https://www.linkedin.com/oauth/v2"
        
        if not self.client_id or not self.client_secret:
            logger.warning("LinkedIn OAuth credentials not configured")
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate LinkedIn OAuth authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL for user to visit
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile email",
        }
        
        if state:
            params["state"] = state
        
        return f"{self.oauth_url}/authorization?{urlencode(params)}"
    
    async def exchange_code_for_token(
        self, 
        code: str,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            session: Optional database session for logging
            
        Returns:
            Token response with access_token
            
        Raises:
            LinkedInOAuthError: If token exchange fails
        """
        if not self.client_id or not self.client_secret:
            raise LinkedInOAuthError("LinkedIn OAuth credentials not configured")
        
        start_time = datetime.now(timezone.utc)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.oauth_url}/accessToken",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                response_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                
                if session:
                    await self._log_api_usage(
                        session=session,
                        endpoint="/oauth/accessToken",
                        status_code=response.status_code,
                        response_time_ms=response_time_ms,
                        success=response.is_success,
                        method="POST"
                    )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {str(e)}")
            raise LinkedInOAuthError(f"Token exchange failed: {str(e)}")
    
    async def get_user_profile(
        self, 
        access_token: str,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Fetch user profile data using access token.
        
        Args:
            access_token: LinkedIn access token
            session: Optional database session for logging
            
        Returns:
            User profile data
            
        Raises:
            LinkedInOAuthError: If API request fails
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Fetch profile data
                profile_response = await client.get(
                    f"{self.base_url}/userinfo",
                    headers=headers
                )
                
                response_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                
                if session:
                    await self._log_api_usage(
                        session=session,
                        endpoint="/v2/userinfo",
                        status_code=profile_response.status_code,
                        response_time_ms=response_time_ms,
                        success=profile_response.is_success,
                        method="GET"
                    )
                
                profile_response.raise_for_status()
                profile_data = profile_response.json()
                
                # Parse the response
                return self._parse_profile_data(profile_data)
                
        except Exception as e:
            logger.error(f"Failed to fetch user profile: {str(e)}")
            raise LinkedInOAuthError(f"Profile fetch failed: {str(e)}")
    
    def _parse_profile_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LinkedIn API profile data into our schema."""
        # Use 'sub' (subject identifier) from OAuth as unique username
        # This is a unique identifier provided by LinkedIn OAuth
        username = data.get("sub")
        if not username:
            # Fallback to email if sub not available
            username = data.get("email", "").split("@")[0] if data.get("email") else None
        
        return {
            "username": username,
            "full_name": data.get("name"),
            "profile_url": None,  # Profile URL not available with basic scopes
            "profile_image_url": data.get("picture"),
            "email": data.get("email"),
            "headline": None,  # Not available with basic scopes
            "summary": None,  # Not available with basic scopes
            "location": data.get("locale"),
            "last_fetched_at": datetime.now(timezone.utc),
            "oauth_successful": True,
        }
    
    async def save_linkedin_profile(
        self, 
        session: AsyncSession, 
        profile_data: Dict[str, Any]
    ) -> LinkedInProfile:
        """Save or update LinkedIn profile in database."""
        try:
            username = profile_data.get("username")
            if not username:
                raise LinkedInOAuthError("Username is required")
            
            # Check if profile exists
            stmt = select(LinkedInProfile).where(LinkedInProfile.username == username)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing
                update_stmt = update(LinkedInProfile).where(
                    LinkedInProfile.username == username
                ).values(**profile_data)
                await session.execute(update_stmt)
                await session.commit()
                await session.refresh(existing)
                return existing
            else:
                # Create new
                new_profile = LinkedInProfile(**profile_data)
                session.add(new_profile)
                await session.commit()
                await session.refresh(new_profile)
                return new_profile
                
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to save LinkedIn profile: {str(e)}")
            raise LinkedInOAuthError(f"Database error: {str(e)}")
    
    async def _log_api_usage(
        self,
        session: AsyncSession,
        endpoint: str,
        status_code: int,
        response_time_ms: int,
        success: bool,
        method: str = "GET",
        error_message: Optional[str] = None
    ) -> None:
        """Log API usage for monitoring."""
        try:
            log_entry = APIUsageLog(
                api_provider="linkedin",
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time_ms=response_time_ms,
                error_message=error_message,
                request_metadata={"oauth": True}
            )
            session.add(log_entry)
            await session.commit()
        except Exception as e:
            logger.warning(f"Failed to log API usage: {str(e)}")


# Global service instance
linkedin_oauth_service = LinkedInOAuthService()
