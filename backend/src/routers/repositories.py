import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
import logging

from db.database import get_async_db
from db.models import GitHubRepository
from services.github_fetcher import sync_github_repositories

logger = logging.getLogger(__name__)


def sanitize_for_log(value: str) -> str:
    """
    Remove newline characters from values before logging to prevent log injection.
    """
    if value is None:
        return ""
    return value.replace("\r", "").replace("\n", "")


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
    featured_stmt = select(GitHubRepository).where(
        GitHubRepository.is_featured
    ).order_by(GitHubRepository.display_order.asc(), desc(GitHubRepository.stargazers_count))

    result = await session.execute(featured_stmt)
    repos = result.scalars().all()

    # Auto-sync portfolio username if no repositories exist yet.
    if not repos:
        portfolio_username = os.getenv("PORTFOLIO_GITHUB_USERNAME", "tshimbilunirsa")
        try:
            await sync_github_repositories(portfolio_username, session)
            result = await session.execute(featured_stmt)
            repos = result.scalars().all()
        except Exception as exc:
            logger.warning("Failed to auto-sync featured repositories: %s", str(exc))

    # Fallback: if nothing is manually featured yet, return top repositories.
    if not repos:
        fallback_stmt = (
            select(GitHubRepository)
            .where(
                GitHubRepository.owner_username == os.getenv("PORTFOLIO_GITHUB_USERNAME", "tshimbilunirsa").lower(),
                GitHubRepository.is_private.is_(False),
                GitHubRepository.is_archived.is_(False),
                GitHubRepository.is_fork.is_(False),
            )
            .order_by(desc(GitHubRepository.stargazers_count), desc(GitHubRepository.github_pushed_at))
            .limit(6)
        )
        fallback_result = await session.execute(fallback_stmt)
        repos = fallback_result.scalars().all()
    
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

    # Ensure we have data on first request.
    if page == 1:
        existing_stmt = select(func.count(GitHubRepository.id)).where(
            GitHubRepository.owner_username == username.lower()
        )
        existing_result = await session.execute(existing_stmt)
        if (existing_result.scalar() or 0) == 0:
            try:
                await sync_github_repositories(username, session)
            except Exception as exc:
                logger.warning(
                    "Unable to auto-sync repositories for %s: %s",
                    sanitize_for_log(username),
                    str(exc),
                )
    
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
