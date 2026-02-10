import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, text

from db.database import get_async_db, get_db
from db.models import LinkedInProfile
from schemas import (
    LinkedInProfileResponse,
    LinkedInProfileCreate,
    LinkedInProfileUpdate,
    LinkedInSyncRequest,
    SyncResponse,
    ErrorResponse,
    PaginatedResponse,
    HealthCheckResponse
)
from services.linkedin_scraper import (
    linkedin_service,
    linkedin_service_sync,
    LinkedInScrapingError
)
from services.linkedin_oauth import linkedin_oauth_service, LinkedInOAuthError

# Configure logging
logger = logging.getLogger(__name__)

# Router configuration
router = APIRouter(
    prefix="/linkedin",
    tags=["LinkedIn"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Profile Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)


@router.post(
    "/sync",
    response_model=SyncResponse,
    summary="Sync LinkedIn profile (deprecated)",
    description="LinkedIn scraping is deprecated. Use OAuth endpoints instead: /linkedin/oauth/authorize",
    deprecated=True,
    responses={
        200: {"description": "Deprecation notice"},
        400: {"description": "Invalid LinkedIn URL"},
        422: {"description": "Validation Error"},
        500: {"description": "Scraping failed"}
    }
)
async def sync_linkedin_profile(
    request: LinkedInSyncRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_db)
) -> SyncResponse:
    """
    Sync LinkedIn profile - now requires OAuth authentication.
    Use /oauth/authorize to connect your LinkedIn account first.
    
    **DEPRECATED**: This endpoint uses web scraping which violates LinkedIn's Terms of Service.
    Please use the OAuth endpoints instead.
    """
    logger.warning("Deprecated /sync endpoint called. Returning OAuth instructions.")
    return SyncResponse(
        success=False,
        message="LinkedIn sync now requires OAuth. Please use /linkedin/oauth/authorize to connect your account.",
        errors=["Web scraping is deprecated and violates LinkedIn ToS"],
        data={"authorization_endpoint": "/api/linkedin/oauth/authorize"},
        timestamp=datetime.now(timezone.utc)
    )


@router.get(
    "/oauth/authorize",
    summary="Start LinkedIn OAuth flow",
    description="Redirect user to LinkedIn authorization page",
    responses={
        200: {"description": "Authorization URL generated"},
        500: {"description": "OAuth configuration error"}
    }
)
async def linkedin_oauth_authorize():
    """Initiate LinkedIn OAuth 2.0 authorization flow."""
    try:
        import secrets
        state = secrets.token_urlsafe(32)
        # In production, store state in session/database for verification
        auth_url = linkedin_oauth_service.get_authorization_url(state=state)
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "message": "Visit the authorization_url to grant access"
        }
    except Exception as e:
        logger.error(f"OAuth authorization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/oauth/callback",
    summary="LinkedIn OAuth callback",
    description="Handle OAuth callback and exchange code for token",
    responses={
        200: {"description": "Profile connected successfully"},
        400: {"description": "OAuth error"},
        500: {"description": "Authentication failed"}
    }
)
async def linkedin_oauth_callback(
    code: str,
    state: Optional[str] = None,
    session: AsyncSession = Depends(get_async_db)
):
    """Handle LinkedIn OAuth callback and fetch profile."""
    try:
        # Exchange code for access token
        token_data = await linkedin_oauth_service.exchange_code_for_token(code, session=session)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")
        
        # Fetch user profile
        profile_data = await linkedin_oauth_service.get_user_profile(access_token, session=session)
        
        # Save to database
        saved_profile = await linkedin_oauth_service.save_linkedin_profile(session, profile_data)
        
        return {
            "success": True,
            "message": "LinkedIn profile connected successfully",
            "profile": LinkedInProfileResponse.from_orm(saved_profile).__dict__
        }
        
    except LinkedInOAuthError as e:
        logger.error(f"LinkedIn OAuth error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        raise HTTPException(status_code=500, detail="OAuth authentication failed")


@router.get(
    "/profiles/{username}",
    response_model=LinkedInProfileResponse,
    summary="Get LinkedIn profile",
    description="Retrieve a LinkedIn profile by username"
)
async def get_linkedin_profile(
    username: str,
    session: AsyncSession = Depends(get_async_db)
) -> LinkedInProfileResponse:
    """
    Get LinkedIn profile by username.
    
    - **username**: LinkedIn username to retrieve
    """
    try:
        profile = await linkedin_service.get_linkedin_profile(session, username)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"LinkedIn profile not found for username: {username}"
            )
        
        return LinkedInProfileResponse.from_orm(profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting LinkedIn profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")


@router.get(
    "/profiles",
    response_model=PaginatedResponse,
    summary="List LinkedIn profiles",
    description="Get a paginated list of all LinkedIn profiles"
)
async def list_linkedin_profiles(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in names and headlines"),
    session: AsyncSession = Depends(get_async_db)
) -> PaginatedResponse:
    """
    List LinkedIn profiles with pagination and search.
    
    - **page**: Page number (starts from 1)
    - **size**: Number of profiles per page (max: 100)
    - **search**: Optional search term for names and headlines
    """
    try:
        offset = (page - 1) * size
        
        # Build query
        stmt = select(LinkedInProfile).order_by(desc(LinkedInProfile.updated_at))
        
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                (LinkedInProfile.full_name.ilike(search_term)) |
                (LinkedInProfile.headline.ilike(search_term)) |
                (LinkedInProfile.username.ilike(search_term))
            )
        
        # Get total count
        from sqlalchemy import func
        count_stmt = select(func.count(LinkedInProfile.username))
        if search:
            search_term = f"%{search}%"
            count_stmt = count_stmt.where(
                (LinkedInProfile.full_name.ilike(search_term)) |
                (LinkedInProfile.headline.ilike(search_term)) |
                (LinkedInProfile.username.ilike(search_term))
            )
        
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Get profiles
        stmt = stmt.offset(offset).limit(size)
        result = await session.execute(stmt)
        profiles = result.scalars().all()
        
        # Convert to response format
        profile_items = [
            LinkedInProfileResponse.from_orm(profile).__dict__
            for profile in profiles
        ]
        
        return PaginatedResponse(
            items=profile_items,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
            has_next=page * size < total,
            has_prev=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error listing LinkedIn profiles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list profiles")


@router.put(
    "/profiles/{username}",
    response_model=LinkedInProfileResponse,
    summary="Update LinkedIn profile",
    description="Update LinkedIn profile information"
)
async def update_linkedin_profile(
    username: str,
    update_data: LinkedInProfileUpdate,
    session: AsyncSession = Depends(get_async_db)
) -> LinkedInProfileResponse:
    """
    Update LinkedIn profile information.
    
    - **username**: LinkedIn username to update
    - **update_data**: Profile data to update
    """
    try:
        # Get existing profile
        profile = await linkedin_service.get_linkedin_profile(session, username)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"LinkedIn profile not found for username: {username}"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(profile, field, value)
        
        profile.updated_at = datetime.now(timezone.utc)
        
        await session.commit()
        await session.refresh(profile)
        
        logger.info(f"Updated LinkedIn profile for: {username}")
        
        return LinkedInProfileResponse.from_orm(profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating LinkedIn profile: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.delete(
    "/profiles/{username}",
    summary="Delete LinkedIn profile",
    description="Delete a LinkedIn profile from the database"
)
async def delete_linkedin_profile(
    username: str,
    session: AsyncSession = Depends(get_async_db)
):
    """
    Delete LinkedIn profile.
    
    - **username**: LinkedIn username to delete
    """
    try:
        # Get existing profile
        profile = await linkedin_service.get_linkedin_profile(session, username)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"LinkedIn profile not found for username: {username}"
            )
        
        # Delete profile
        await session.delete(profile)
        await session.commit()
        
        logger.info(f"Deleted LinkedIn profile for: {username}")
        
        return {"message": f"LinkedIn profile for {username} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting LinkedIn profile: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete profile")


@router.post(
    "/profiles/{username}/refresh",
    response_model=SyncResponse,
    summary="Refresh LinkedIn profile",
    description="Force refresh a LinkedIn profile from the original URL"
)
async def refresh_linkedin_profile(
    username: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_db)
) -> SyncResponse:
    """
    Force refresh LinkedIn profile data.
    
    - **username**: LinkedIn username to refresh
    """
    try:
        # Get existing profile to get the URL
        profile = await linkedin_service.get_linkedin_profile(session, username)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"LinkedIn profile not found for username: {username}"
            )
        
        if not profile.profile_url:
            raise HTTPException(
                status_code=400,
                detail="Profile URL not available for refresh"
            )
        
        logger.info(f"Force refreshing LinkedIn profile for: {username}")
        
        # Scrape fresh data
        profile_data = await linkedin_service.scrape_linkedin_public_profile(
            url=profile.profile_url,
            session=session
        )
        
        # Update existing profile
        saved_profile = await linkedin_service.save_linkedin_profile(session, profile_data)
        
        return SyncResponse(
            success=True,
            message=f"LinkedIn profile for {username} refreshed successfully",
            data=LinkedInProfileResponse.from_orm(saved_profile).__dict__,
            timestamp=datetime.now(timezone.utc)
        )
        
    except HTTPException:
        raise
    except LinkedInScrapingError as e:
        logger.error(f"LinkedIn scraping error during refresh: {str(e)}")
        return SyncResponse(
            success=False,
            message="Failed to refresh LinkedIn profile",
            errors=[str(e)],
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"Error refreshing LinkedIn profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to refresh profile")


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="LinkedIn service health check",
    description="Check the health of the LinkedIn service"
)
async def health_check(
    session: AsyncSession = Depends(get_async_db)
) -> HealthCheckResponse:
    """
    Check the health of the LinkedIn service.
    
    Returns the status of the database and scraping capabilities.
    """
    try:
        # Check database connectivity
        await session.execute(text("SELECT 1"))
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_healthy = False
    
    # Check external dependencies
    external_apis = {
        "crawl4ai": True,  # Assume crawl4ai is available
        "httpx": True,     # HTTP client for requests
    }
    
    return HealthCheckResponse(
        status="healthy" if db_healthy else "unhealthy",
        timestamp=datetime.now(timezone.utc),
        database=db_healthy,
        external_apis=external_apis
    )


# Backward compatibility endpoint
@router.get(
    "/sync",
    response_model=LinkedInProfileResponse,
    summary="Sync LinkedIn profile (deprecated)",
    description="Sync LinkedIn profile - deprecated, use POST /linkedin/sync instead",
    deprecated=True
)
def sync_linkedin_profile_deprecated(
    url: str,
    db: Session = Depends(get_db)
) -> LinkedInProfileResponse:
    """
    Sync LinkedIn profile (backward compatibility).
    
    **Deprecated**: Use POST /linkedin/sync instead.
    """
    try:
        logger.warning("Using deprecated LinkedIn sync endpoint")
        
        # Use synchronous service for backward compatibility
        from services.linkedin_scraper import scrape_linkedin_public_profile, save_linkedin_profile
        
        profile_data = scrape_linkedin_public_profile(url)
        saved_profile = save_linkedin_profile(db, profile_data)
        
        return LinkedInProfileResponse.from_orm(saved_profile)
        
    except Exception as e:
        logger.error(f"Error in deprecated sync endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))