import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_db
from db.models import GitHubRepository
from routers.github import configured_username
from services.github_fetcher import repository_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/repositories", tags=["Repositories"])

# Repositories are refreshed by POST /github/sync; older data is still served
# but flagged as stale.
STALE_AFTER = timedelta(hours=24)


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


def _is_stale(repos) -> bool:
    latest_sync = max(
        (repo.last_synced_at for repo in repos if repo.last_synced_at), default=None
    )
    if latest_sync is None:
        return True
    if latest_sync.tzinfo is None:
        latest_sync = latest_sync.replace(tzinfo=timezone.utc)
    return latest_sync < datetime.now(timezone.utc) - STALE_AFTER


@router.get("/featured")
async def get_featured_repositories(session: AsyncSession = Depends(get_async_db)):
    """Return cached featured repositories without calling GitHub."""
    username = configured_username()
    repos = (await session.execute(_query(username, featured_only=True))).scalars().all()
    if not repos:
        repos = (await session.execute(_query(username))).scalars().all()
    if not repos:
        raise HTTPException(503, "Repository data has not been synchronized yet")

    stale = _is_stale(repos)
    return [repository_response(repo, stale=stale) for repo in repos]
