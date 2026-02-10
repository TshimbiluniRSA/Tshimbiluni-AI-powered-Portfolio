from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List
import logging

from db.database import get_async_db
from db.models import GitHubRepository
from services.github_fetcher import sync_github_repositories

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/repositories", tags=["Repositories"])


@router.post("/sync/{username}")
async def sync_repositories(
    username: str,
    force_refresh: bool = Query(False),
    session: AsyncSession = Depends(get_async_db)
):
    """Sync GitHub repositories for a user."""
    try:
        repos = await sync_github_repositories(username, session, force_refresh)
        return {
            "success": True,
            "count": len(repos),
            "message": f"Synced {len(repos)} repositories"
        }
    except Exception as e:
        logger.error(f"Failed to sync repositories: {e}")
        raise HTTPException(500, f"Failed to sync repositories: {str(e)}")


@router.get("/featured")
async def get_featured_repositories(
    session: AsyncSession = Depends(get_async_db)
):
    """Get featured repositories for portfolio."""
    stmt = select(GitHubRepository).where(
        GitHubRepository.is_featured
    ).order_by(GitHubRepository.display_order.asc(), desc(GitHubRepository.stargazers_count))
    
    result = await session.execute(stmt)
    repos = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "html_url": r.html_url,
            "language": r.language,
            "languages": r.languages_data,
            "topics": r.topics,
            "stars": r.stargazers_count,
            "forks": r.forks_count,
        }
        for r in repos
    ]


@router.get("/{username}")
async def get_user_repositories(
    username: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_db)
):
    """Get all repositories for a user."""
    offset = (page - 1) * size
    
    stmt = select(GitHubRepository).where(
        GitHubRepository.owner_username == username.lower()
    ).order_by(desc(GitHubRepository.stargazers_count)).offset(offset).limit(size)
    
    result = await session.execute(stmt)
    repos = result.scalars().all()
    
    # Get total count
    count_stmt = select(func.count(GitHubRepository.id)).where(
        GitHubRepository.owner_username == username.lower()
    )
    count_result = await session.execute(count_stmt)
    total = count_result.scalar()
    
    return {
        "items": [
            {
                "id": r.id,
                "name": r.name,
                "full_name": r.full_name,
                "description": r.description,
                "html_url": r.html_url,
                "language": r.language,
                "topics": r.topics,
                "stars": r.stargazers_count,
                "forks": r.forks_count,
                "is_featured": r.is_featured,
            }
            for r in repos
        ],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.patch("/{repo_id}/feature")
async def toggle_featured(
    repo_id: int,
    is_featured: bool,
    display_order: int = None,
    session: AsyncSession = Depends(get_async_db)
):
    """Mark a repository as featured for portfolio showcase."""
    stmt = select(GitHubRepository).where(GitHubRepository.id == repo_id)
    result = await session.execute(stmt)
    repo = result.scalar_one_or_none()
    
    if not repo:
        raise HTTPException(404, "Repository not found")
    
    repo.is_featured = is_featured
    if display_order is not None:
        repo.display_order = display_order
    
    await session.commit()
    return {"success": True, "message": f"Repository featured status updated"}
