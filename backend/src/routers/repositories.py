import logging
import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_db
from db.models import GitHubRepository
from services.github_fetcher import repository_response, sync_github_repositories

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/repositories", tags=["Repositories"])


def _query(username: str, featured_only: bool = False):
    stmt = select(GitHubRepository).where(
        GitHubRepository.owner_username == username.lower(),
        GitHubRepository.is_private.is_(False),
        GitHubRepository.is_archived.is_(False),
        GitHubRepository.is_fork.is_(False),
    )
    if featured_only:
        stmt = stmt.where(GitHubRepository.is_featured.is_(True))
    return stmt.order_by(
        GitHubRepository.display_order.asc(), desc(GitHubRepository.stargazers_count)
    ).limit(6)


@router.get("/featured")
async def get_featured_repositories(session: AsyncSession = Depends(get_async_db)):
    """Refresh stale data, but always prefer the last usable repository cache."""
    username = os.getenv("PORTFOLIO_GITHUB_USERNAME", "TshimbiluniRSA")
    result = await session.execute(_query(username, featured_only=True))
    repos = result.scalars().all()
    if not repos:
        result = await session.execute(_query(username))
        repos = result.scalars().all()
    cached_repos = repos
    latest_sync = max(
        (repo.last_synced_at for repo in cached_repos if repo.last_synced_at),
        default=None,
    )
    if latest_sync and latest_sync.tzinfo is None:
        latest_sync = latest_sync.replace(tzinfo=timezone.utc)
    cache_is_fresh = latest_sync and latest_sync > datetime.now(
        timezone.utc
    ) - timedelta(hours=24)
    if cached_repos and cache_is_fresh:
        return [repository_response(repo) for repo in repos]

    try:
        await sync_github_repositories(username, session, force_refresh=True)
        result = await session.execute(_query(username, featured_only=True))
        repos = result.scalars().all()
        if not repos:
            result = await session.execute(_query(username))
            repos = result.scalars().all()
    except Exception as exc:
        await session.rollback()
        if cached_repos:
            logger.warning(
                "GitHub refresh failed; serving cached repositories: %s", exc
            )
            return [repository_response(repo, stale=True) for repo in cached_repos]
        logger.warning("GitHub refresh failed and no repository cache exists: %s", exc)
        raise HTTPException(503, "Repository data is temporarily unavailable") from None

    if not repos:
        raise HTTPException(503, "Repository data is temporarily unavailable")
    return [repository_response(repo) for repo in repos]
