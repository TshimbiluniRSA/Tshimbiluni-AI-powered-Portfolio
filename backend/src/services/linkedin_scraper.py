import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from urllib.parse import urlparse

import httpx
from crawl4ai import AsyncWebCrawler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from db.models import LinkedInProfile, APIUsageLog
from schemas import LinkedInProfileCreate, LinkedInProfileResponse

# Configure logging
logger = logging.getLogger(__name__)


class LinkedInScrapingError(Exception):
    """Custom exception for LinkedIn scraping errors."""
    pass


class LinkedInProfileService:
    """Service class for LinkedIn profile operations."""

    def __init__(self):
        self.crawler_config = {
            "headless": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "delay": 2,  # Delay between requests to be respectful
            "timeout": 30,
        }

    async def scrape_linkedin_public_profile(
        self, 
        url: str, 
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Scrape LinkedIn public profile data.
        
        Args:
            url: LinkedIn profile URL to scrape
            session: Optional database session for logging
            
        Returns:
            Dict containing scraped profile data
            
        Raises:
            LinkedInScrapingError: If scraping fails
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Validate URL
            self._validate_linkedin_url(url)
            
            # Extract username from URL
            username = self._extract_username_from_url(url)
            
            logger.info(f"Starting LinkedIn scrape for username: {username}")
            
            async with AsyncWebCrawler(**self.crawler_config) as crawler:
                result = await crawler.arun(url=url)
                
                if not result or not result.success:
                    raise LinkedInScrapingError(f"Failed to crawl URL: {url}")
                
                # Parse the scraped data
                profile_data = self._parse_scraped_data(result, url, username)
                
                # Log successful API usage
                if session:
                    await self._log_api_usage(
                        session=session,
                        url=url,
                        success=True,
                        response_time=(datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    )
                
                logger.info(f"Successfully scraped LinkedIn profile for: {username}")
                return profile_data
                
        except Exception as e:
            # Log failed API usage
            if session:
                await self._log_api_usage(
                    session=session,
                    url=url,
                    success=False,
                    error_message=str(e),
                    response_time=(datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                )
            
            logger.error(f"LinkedIn scraping failed for {url}: {str(e)}")
            raise LinkedInScrapingError(f"Failed to scrape LinkedIn profile: {str(e)}")

    def _validate_linkedin_url(self, url: str) -> None:
        """
        Validate LinkedIn profile URL format.
        
        Args:
            url: URL to validate
            
        Raises:
            LinkedInScrapingError: If URL is invalid
        """
        if not url:
            raise LinkedInScrapingError("URL cannot be empty")
        
        parsed = urlparse(url)
        if not parsed.netloc or 'linkedin.com' not in parsed.netloc:
            raise LinkedInScrapingError("Invalid LinkedIn URL")
        
        if '/in/' not in url:
            raise LinkedInScrapingError("URL must be a LinkedIn profile URL (contains /in/)")

    def _extract_username_from_url(self, url: str) -> str:
        """
        Extract username from LinkedIn profile URL.
        
        Args:
            url: LinkedIn profile URL
            
        Returns:
            Extracted username
        """
        try:
            # LinkedIn profile URLs have format: https://linkedin.com/in/username
            parts = url.split('/in/')
            if len(parts) < 2:
                raise ValueError("Invalid LinkedIn profile URL format")
            
            username = parts[1].split('/')[0].split('?')[0]  # Remove trailing params
            return username.lower().strip()
        except Exception:
            # Fallback: use domain extraction
            parsed = urlparse(url)
            return parsed.path.replace('/in/', '').strip('/').split('/')[0].lower()

    def _parse_scraped_data(
        self, 
        crawl_result: Any, 
        url: str, 
        username: str
    ) -> Dict[str, Any]:
        """
        Parse scraped data from crawl result.
        
        Args:
            crawl_result: Result from web crawler
            url: Original URL
            username: Extracted username
            
        Returns:
            Parsed profile data dictionary
        """
        # Extract basic information
        title = crawl_result.metadata.get("title", "") if crawl_result.metadata else ""
        description = crawl_result.metadata.get("description", "") if crawl_result.metadata else ""
        
        # Try to extract name from title
        full_name = None
        if title:
            # LinkedIn titles often have format "Name | Professional Title"
            name_parts = title.split("|")
            if name_parts:
                full_name = name_parts[0].strip()
        
        # Extract headline from title or description
        headline = None
        if title and "|" in title:
            headline_parts = title.split("|")
            if len(headline_parts) > 1:
                headline = headline_parts[1].strip()
        
        # Try to extract additional info from the page content
        additional_data = self._extract_additional_profile_data(crawl_result)
        
        return {
            "username": username,
            "headline": headline or additional_data.get("headline"),
            "summary": description or additional_data.get("summary"),
            "profile_url": url,
            "full_name": full_name or additional_data.get("full_name"),
            "location": additional_data.get("location"),
            "industry": additional_data.get("industry"),
            "connections_count": additional_data.get("connections_count"),
            "profile_image_url": additional_data.get("profile_image_url"),
            "last_scraped_at": datetime.now(timezone.utc),
            "scraping_successful": True,
            "scraping_error": None
        }

    def _extract_additional_profile_data(self, crawl_result: Any) -> Dict[str, Optional[str]]:
        """
        Extract additional profile data from crawled content.
        
        Args:
            crawl_result: Result from web crawler
            
        Returns:
            Dictionary with additional profile data
        """
        additional_data = {
            "headline": None,
            "summary": None,
            "full_name": None,
            "location": None,
            "industry": None,
            "connections_count": None,
            "profile_image_url": None
        }
        
        try:
            # This would need to be implemented based on actual LinkedIn HTML structure
            # For now, return empty data as LinkedIn actively blocks scraping
            # In a real implementation, you might use:
            # - Selenium with stealth mode
            # - LinkedIn API (requires authentication)
            # - Third-party services
            pass
        except Exception as e:
            logger.warning(f"Failed to extract additional profile data: {str(e)}")
        
        return additional_data

    async def save_linkedin_profile(
        self, 
        session: AsyncSession, 
        profile_data: Dict[str, Any]
    ) -> LinkedInProfile:
        """
        Save LinkedIn profile data to database.
        
        Args:
            session: Database session
            profile_data: Profile data dictionary
            
        Returns:
            Saved LinkedIn profile instance
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Check if profile already exists
            stmt = select(LinkedInProfile).where(
                LinkedInProfile.username == profile_data["username"]
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing record
                update_stmt = update(LinkedInProfile).where(
                    LinkedInProfile.username == profile_data["username"]
                ).values(**profile_data)
                
                await session.execute(update_stmt)
                await session.commit()
                
                # Refresh the instance
                await session.refresh(existing)
                logger.info(f"Updated LinkedIn profile for username: {profile_data['username']}")
                return existing
            else:
                # Create new record
                new_profile = LinkedInProfile(**profile_data)
                session.add(new_profile)
                await session.commit()
                await session.refresh(new_profile)
                
                logger.info(f"Created new LinkedIn profile for username: {profile_data['username']}")
                return new_profile
                
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to save LinkedIn profile: {str(e)}")
            raise

    async def get_linkedin_profile(
        self, 
        session: AsyncSession, 
        username: str
    ) -> Optional[LinkedInProfile]:
        """
        Get LinkedIn profile from database.
        
        Args:
            session: Database session
            username: LinkedIn username
            
        Returns:
            LinkedIn profile if found, None otherwise
        """
        try:
            stmt = select(LinkedInProfile).where(LinkedInProfile.username == username)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get LinkedIn profile for {username}: {str(e)}")
            return None

    async def is_profile_stale(
        self, 
        session: AsyncSession, 
        username: str, 
        max_age_days: int = 7
    ) -> bool:
        """
        Check if LinkedIn profile data is stale.
        
        Args:
            session: Database session
            username: LinkedIn username
            max_age_days: Maximum age in days before considering stale
            
        Returns:
            True if profile is stale or doesn't exist
        """
        profile = await self.get_linkedin_profile(session, username)
        if not profile or not profile.last_scraped_at:
            return True
        
        age_days = (datetime.now(timezone.utc) - profile.last_scraped_at).days
        return age_days >= max_age_days

    async def _log_api_usage(
        self,
        session: AsyncSession,
        url: str,
        success: bool,
        response_time: float,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log API usage for monitoring.
        
        Args:
            session: Database session
            url: LinkedIn URL accessed
            success: Whether the operation was successful
            response_time: Response time in milliseconds
            error_message: Error message if failed
        """
        try:
            log_entry = APIUsageLog(
                api_provider="linkedin",
                endpoint=url,
                method="GET",
                status_code=200 if success else 500,
                response_time_ms=int(response_time),
                error_message=error_message,
                request_metadata={"scraping_url": url}
            )
            
            session.add(log_entry)
            await session.commit()
        except Exception as e:
            logger.warning(f"Failed to log API usage: {str(e)}")


# Sync versions for backward compatibility
class LinkedInProfileServiceSync:
    """Synchronous version of LinkedIn profile service."""
    
    def __init__(self):
        self.service = LinkedInProfileService()
    
    def save_linkedin_profile(self, db: Session, profile_data: Dict[str, Any]) -> LinkedInProfile:
        """
        Synchronous version of save_linkedin_profile.
        
        Args:
            db: Synchronous database session
            profile_data: Profile data dictionary
            
        Returns:
            Saved LinkedIn profile instance
        """
        try:
            # Check if profile already exists
            existing = db.query(LinkedInProfile).filter_by(
                username=profile_data["username"]
            ).first()
            
            if existing:
                # Update existing record
                for key, value in profile_data.items():
                    setattr(existing, key, value)
            else:
                # Create new record
                existing = LinkedInProfile(**profile_data)
                db.add(existing)
            
            db.commit()
            db.refresh(existing)
            return existing
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save LinkedIn profile (sync): {str(e)}")
            raise


# Global service instances
linkedin_service = LinkedInProfileService()
linkedin_service_sync = LinkedInProfileServiceSync()

# Backward compatibility functions
async def scrape_linkedin_public_profile(url: str) -> Dict[str, Any]:
    """
    Backward compatibility function for scraping LinkedIn profiles.
    
    Args:
        url: LinkedIn profile URL
        
    Returns:
        Profile data dictionary
    """
    return await linkedin_service.scrape_linkedin_public_profile(url)


def save_linkedin_profile(db: Session, profile_data: Dict[str, Any]) -> LinkedInProfile:
    """
    Backward compatibility function for saving LinkedIn profiles.
    
    Args:
        db: Database session
        profile_data: Profile data dictionary
        
    Returns:
        Saved LinkedIn profile instance
    """
    return linkedin_service_sync.save_linkedin_profile(db, profile_data)