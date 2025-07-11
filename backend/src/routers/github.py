import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from db.database import get_async_db, get_db
from db.models import GitHubProfile
from schemas import (
    GitHubProfileResponse,
    GitHubProfileCreate,
    GitHubProfileUpdate,
    GitHubSyncRequest,
    SyncResponse,
    ErrorResponse,
    PaginatedResponse,
    HealthCheckResponse
)
from services.github_fetcher import fetch_github_data, save_github_profile

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/github",
    tags=["GitHub"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Profile Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)

# Dependency for backward compatibility
def get_db():
    db = get_db()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/sync",
    response_model=SyncResponse,
    summary="Sync GitHub profile",
    description="Sync a GitHub profile from the GitHub API by username"
)
async def sync_github_profile(
    request: GitHubSyncRequest,
    session: AsyncSession = Depends(get_async_db)
) -> SyncResponse:
    """Sync GitHub profile data for a username."""
    try:
        username = request.username
        # Optionally, check for staleness if not force_refresh (not implemented here)
        logger.info(f"Starting GitHub sync for username: {username}")
        profile_data = await fetch_github_data(username)
        saved_profile = await save_github_profile(session, profile_data)
        logger.info(f"Successfully synced GitHub profile for: {username}")

        return SyncResponse(
            success=True,
            message=f"GitHub profile for {username} synced successfully",
            data=GitHubProfileResponse.from_orm(saved_profile).__dict__,
            timestamp=datetime.now(timezone.utc)
        )
    except Exception as e:
        logger.error(f"GitHub sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to sync GitHub profile: {str(e)}")


@router.get(
    "/profiles/{username}",
    response_model=GitHubProfileResponse,
    summary="Get GitHub profile",
    description="Retrieve a GitHub profile by username"
)
async def get_github_profile(
    username: str,
    session: AsyncSession = Depends(get_async_db)
) -> GitHubProfileResponse:
    """Get GitHub profile by username."""
    try:
        stmt = select(GitHubProfile).where(GitHubProfile.username == username)
        result = await session.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"GitHub profile not found for username: {username}"
            )
        return GitHubProfileResponse.from_orm(profile)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting GitHub profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")


@router.get(
    "/profiles",
    response_model=PaginatedResponse,
    summary="List GitHub profiles",
    description="Get a paginated list of all GitHub profiles"
)
async def list_github_profiles(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in usernames, names, and bios"),
    session: AsyncSession = Depends(get_async_db)
) -> PaginatedResponse:
    """List GitHub profiles with pagination and search."""
    try:
        offset = (page - 1) * size
        stmt = select(GitHubProfile).order_by(desc(GitHubProfile.updated_at))
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                (GitHubProfile.username.ilike(search_term)) |
                (GitHubProfile.name.ilike(search_term)) |
                (GitHubProfile.bio.ilike(search_term))
            )
        # Get total count
        count_stmt = select(func.count(GitHubProfile.username))
        if search:
            search_term = f"%{search}%"
            count_stmt = count_stmt.where(
                (GitHubProfile.username.ilike(search_term)) |
                (GitHubProfile.name.ilike(search_term)) |
                (GitHubProfile.bio.ilike(search_term))
            )
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0
        stmt = stmt.offset(offset).limit(size)
        result = await session.execute(stmt)
        profiles = result.scalars().all()
        profile_items = [
            GitHubProfileResponse.from_orm(profile).__dict__
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
        logger.error(f"Error listing GitHub profiles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list profiles")


@router.delete(
    "/profiles/{username}",
    summary="Delete GitHub profile",
    description="Delete a GitHub profile from the database"
)
async def delete_github_profile(
    username: str,
    session: AsyncSession = Depends(get_async_db)
):
    """Delete GitHub profile."""
    try:
        stmt = select(GitHubProfile).where(GitHubProfile.username == username)
        result = await session.execute(stmt)
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"GitHub profile not found for username: {username}"
            )
        await session.delete(profile)
        await session.commit()
        logger.info(f"Deleted GitHub profile for: {username}")
        return {"message": f"GitHub profile for {username} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting GitHub profile: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete profile")


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="GitHub service health check",
    description="Check the health of the GitHub sync and storage service"
)
async def health_check(
    session: AsyncSession = Depends(get_async_db)
) -> HealthCheckResponse:
    """Check the health of the GitHub profile service."""
    try:
        await session.execute(select(1))
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_healthy = False

    # Check GitHub API (could be improved with a real ping)
    external_apis = {
        "github": True  # Assume GitHub is reachable if configured
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
    response_model=GitHubProfileResponse,
    summary="Sync GitHub profile (deprecated)",
    description="Sync GitHub profile - deprecated, use POST /github/sync instead",
    deprecated=True
)
async def sync_github_profile_deprecated(
    username: str = "TshimbiluniRSA",
    session: AsyncSession = Depends(get_async_db)
) -> GitHubProfileResponse:
    try:
        profile_data = await fetch_github_data(username, session=session)
        saved = await save_github_profile(session, profile_data)
        return GitHubProfileResponse.from_orm(saved)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))