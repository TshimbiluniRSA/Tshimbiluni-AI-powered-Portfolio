import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_db
from db.models import GitHubRepository
from services.github_fetcher import (
    fetch_github_repository_responses,
    repository_response,
    sync_github_repositories,
)

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
    session: AsyncSession = Depends(get_async_db),
):
    """Sync GitHub repositories for a user."""
    try:
        repos = await sync_github_repositories(username, session, force_refresh)
        return {
            "success": True,
            "count": len(repos),
            "message": f"Synced {len(repos)} repositories",
        }
    except Exception as e:
        await session.rollback()
        logger.error("Failed to sync repositories: %s", str(e))
        raise HTTPException(500, f"Failed to sync repositories: {str(e)}")


@router.get("/featured")
async def get_featured_repositories(
    session: AsyncSession = Depends(get_async_db),
):
    """Get featured repositories for portfolio."""
    portfolio_username = os.getenv("PORTFOLIO_GITHUB_USERNAME", "TshimbiluniRSA")
    featured_stmt = select(GitHubRepository).where(
        GitHubRepository.is_featured
    ).order_by(GitHubRepository.display_order.asc(), desc(GitHubRepository.stargazers_count))

    try:
        result = await session.execute(featured_stmt)
        repos = result.scalars().all()

        # Auto-sync portfolio username if no repositories exist yet.
        if not repos:
            try:
                await sync_github_repositories(portfolio_username, session)
                result = await session.execute(featured_stmt)
                repos = result.scalars().all()
            except Exception as exc:
                await session.rollback()
                logger.warning("Failed to auto-sync featured repositories: %s", str(exc))

        # Fallback: if nothing is manually featured yet, return top cached repositories.
        if not repos:
            fallback_stmt = (
                select(GitHubRepository)
                .where(
                    GitHubRepository.owner_username == portfolio_username.lower(),
                    GitHubRepository.is_private.is_(False),
                    GitHubRepository.is_archived.is_(False),
                    GitHubRepository.is_fork.is_(False),
                )
                .order_by(desc(GitHubRepository.stargazers_count), desc(GitHubRepository.github_pushed_at))
                .limit(6)
            )
            fallback_result = await session.execute(fallback_stmt)
            repos = fallback_result.scalars().all()

        if repos:
            return [repository_response(repo) for repo in repos]
    except Exception as exc:
        await session.rollback()
        logger.warning("Repository database lookup failed, using live GitHub fallback: %s", str(exc))

    # Last-resort live GitHub fallback keeps the Projects section working even
    # before repository rows have been migrated or cached in the database.
    try:
        return await fetch_github_repository_responses(portfolio_username, limit=6)
    except Exception as exc:
        logger.error("Failed to fetch live GitHub repositories: %s", str(exc))
        return []


@router.get("/{username}")
async def get_user_repositories(
    username: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_db),
):
    """Get all repositories for a user."""
    offset = (page - 1) * size
    sync_failed = False

    try:
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
                    sync_failed = True
                    await session.rollback()
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
        total = count_result.scalar() or 0

        if repos or not sync_failed:
            return {
                "items": [repository_response(repo) for repo in repos],
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,
            }
    except Exception as exc:
        await session.rollback()
        logger.warning(
            "Repository database lookup failed for %s, using live GitHub fallback: %s",
            sanitize_for_log(username),
            str(exc),
        )

    try:
        live_repos = await fetch_github_repository_responses(username, limit=size)
    except Exception as exc:
        logger.error(
            "Failed to fetch live GitHub repositories for %s: %s",
            sanitize_for_log(username),
            str(exc),
        )
        live_repos = []

    return {
        "items": live_repos,
        "total": len(live_repos),
        "page": page,
        "size": size,
        "pages": 1 if live_repos else 0,
    }


@router.patch("/{repo_id}/feature")
async def toggle_featured(
    repo_id: int,
    is_featured: bool,
    display_order: int = None,
    session: AsyncSession = Depends(get_async_db),
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
    return {"success": True, "message": "Repository featured status updated"}
