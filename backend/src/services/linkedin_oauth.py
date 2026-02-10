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
        # Use correct LinkedIn OpenID Connect userinfo endpoint
        self.userinfo_url = "https://api.linkedin.com/v2/userinfo"
        # Also support the profile API v2 endpoint as fallback
        self.profile_url = "https://api.linkedin.com/v2/me"
        self.email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
    
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
        
        # Request appropriate scopes for LinkedIn Sign In with OpenID Connect
        # Note: 'openid', 'profile', and 'email' are the standard OIDC scopes
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
        Get user information from LinkedIn using multiple methods.
        
        This method tries:
        1. OpenID Connect userinfo endpoint (preferred for tokens with 'openid' scope)
        2. Profile API v2 + Email API (fallback for tokens with 'r_liteprofile' or 'r_basicprofile')
        
        Args:
            access_token: LinkedIn access token
            
        Returns:
            User information including name, email, picture
        """
        # Try OpenID Connect userinfo endpoint first (for Sign In with LinkedIn)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                # If successful, return the OpenID Connect userinfo
                if response.status_code == 200:
                    logger.info("Successfully fetched user info via OpenID Connect")
                    return response.json()
                
                # Log the error but try fallback method
                logger.warning(f"OpenID Connect userinfo failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.warning(f"OpenID Connect userinfo error: {str(e)}, trying fallback")
        
        # Fallback: Use LinkedIn Profile API v2
        try:
            logger.info("Attempting to fetch user info via Profile API v2")
            async with httpx.AsyncClient() as client:
                # Get basic profile info
                profile_response = await client.get(
                    self.profile_url,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                profile_response.raise_for_status()
                profile_data = profile_response.json()
                
                # Get email if available
                email = None
                try:
                    email_response = await client.get(
                        self.email_url,
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    if email_response.status_code == 200:
                        email_data = email_response.json()
                        if "elements" in email_data and len(email_data["elements"]) > 0:
                            email = email_data["elements"][0].get("handle~", {}).get("emailAddress")
                except Exception as email_error:
                    logger.warning(f"Could not fetch email: {str(email_error)}")
                
                # Transform v2 profile data to match OpenID Connect format
                given_name = profile_data.get("localizedFirstName") or None
                family_name = profile_data.get("localizedLastName") or None
                
                # Construct full name, or None if both parts are missing
                if given_name or family_name:
                    full_name = f"{given_name or ''} {family_name or ''}".strip()
                else:
                    full_name = None
                
                user_info = {
                    "sub": profile_data.get("id"),
                    "name": full_name,
                    "given_name": given_name,
                    "family_name": family_name,
                    "email": email,
                    "picture": None,  # Would need additional API call for profile picture
                }
                
                logger.info("Successfully fetched user info via Profile API v2")
                return user_info
                
        except httpx.HTTPStatusError as e:
            logger.error(f"LinkedIn Profile API failed: {e.response.text}")
            raise LinkedInOAuthError(f"Failed to get user info: {e.response.text}")
        except Exception as e:
            logger.error(f"LinkedIn Profile API error: {str(e)}")
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
