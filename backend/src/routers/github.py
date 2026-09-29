import logging
import os
import secrets
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_db
from db.models import GitHubStatsSnapshot
from schemas import GitHubStatsResponse
from services.github_fetcher import sync_github_repositories
from services.github_stats import (
    GitHubError,
    GitHubStatsService,
    save_snapshot,
    serialize,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/github", tags=["GitHub"])


def configured_username():
    return os.getenv("GITHUB_USERNAME", "TshimbiluniRSA")


async def cached_snapshot(session: AsyncSession):
    return (
        await session.execute(
            select(GitHubStatsSnapshot).where(
                GitHubStatsSnapshot.username == configured_username().lower()
            )
        )
    ).scalar_one_or_none()


@router.get("/stats", response_model=GitHubStatsResponse)
async def stats(session: AsyncSession = Depends(get_async_db)):
    row = await cached_snapshot(session)
    if not row:
        raise HTTPException(404, "GitHub statistics have not been synchronized")
    return serialize(row)


@router.post("/sync", response_model=GitHubStatsResponse)
async def sync(
    x_github_sync_token: str | None = Header(None),
    session: AsyncSession = Depends(get_async_db),
):
    expected = os.getenv("GITHUB_SYNC_TOKEN")
    if (
        not expected
        or not x_github_sync_token
        or not secrets.compare_digest(expected, x_github_sync_token)
    ):
        raise HTTPException(403, "GitHub synchronization is not authorized")
    try:
        data = await GitHubStatsService().collect(configured_username())
        row = await save_snapshot(session, data)
    except GitHubError as exc:
        await session.rollback()
        row = await cached_snapshot(session)
        if row:
            return serialize(row, stale=True)
        raise HTTPException(503, str(exc)) from None

    # Serialize before the repository sync: a rollback there would expire row.
    response = serialize(row)

    # Featured repositories are served from this cache by
    # /api/repositories/featured; a failure here keeps the previous rows and
    # must not discard the statistics saved above.
    try:
        await sync_github_repositories(
            configured_username(), session, force_refresh=True
        )
    except Exception as exc:
        await session.rollback()
        logger.warning("Repository sync failed; keeping cached repositories: %s", exc)
    return response
