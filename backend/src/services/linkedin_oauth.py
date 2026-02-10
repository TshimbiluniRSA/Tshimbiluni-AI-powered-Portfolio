import logging
import os
from typing import Dict, Any, Optional
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)


class LinkedInOAuthError(Exception):
    """Custom exception for LinkedIn OAuth errors."""
    pass


class LinkedInOAuthService:
    """Service for LinkedIn OAuth integration."""
    
    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
        
        if not self.client_id or not self.client_secret:
            logger.warning("LinkedIn OAuth credentials not configured")
        
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.userinfo_url = "https://api.linkedin.com/v2/userinfo"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate LinkedIn OAuth authorization URL.
        
        Args:
            state: Optional state parameter for security
            
        Returns:
            Authorization URL
        """
        if not self.client_id or not self.redirect_uri:
            raise LinkedInOAuthError("LinkedIn OAuth not configured")
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile email",
        }
        
        if state:
            params["state"] = state
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from LinkedIn
            
        Returns:
            Token response including access_token, expires_in, etc.
        """
        if not self.client_id or not self.client_secret or not self.redirect_uri:
            raise LinkedInOAuthError("LinkedIn OAuth not configured")
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"LinkedIn token exchange failed: {e.response.text}")
            raise LinkedInOAuthError(f"Failed to exchange code for token: {e.response.text}")
        except Exception as e:
            logger.error(f"LinkedIn token exchange error: {str(e)}")
            raise LinkedInOAuthError(f"Token exchange error: {str(e)}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from LinkedIn.
        
        Args:
            access_token: LinkedIn access token
            
        Returns:
            User information including name, email, picture
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"LinkedIn userinfo failed: {e.response.text}")
            raise LinkedInOAuthError(f"Failed to get user info: {e.response.text}")
        except Exception as e:
            logger.error(f"LinkedIn userinfo error: {str(e)}")
            raise LinkedInOAuthError(f"User info error: {str(e)}")


# Global service instance - lazily initialized
_linkedin_oauth_service_instance: Optional[LinkedInOAuthService] = None


def get_linkedin_oauth_service() -> LinkedInOAuthService:
    """
    Get or create the global LinkedIn OAuth service instance (lazy initialization).
    
    This ensures the service is only initialized when first needed,
    allowing environment variables to be loaded first on platforms like Render.
    
    Returns:
        LinkedIn OAuth service instance
    """
    global _linkedin_oauth_service_instance
    if _linkedin_oauth_service_instance is None:
        _linkedin_oauth_service_instance = LinkedInOAuthService()
        logger.info("LinkedIn OAuth service initialized lazily")
    return _linkedin_oauth_service_instance


# Backward compatibility - set to None to fail early if old code tries to use it
# This forces migration to get_linkedin_oauth_service() function
linkedin_oauth_service = None  # Deprecated - use get_linkedin_oauth_service() instead
