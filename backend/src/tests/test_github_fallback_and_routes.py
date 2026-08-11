from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from main import app
from routers import github
from services.github_stats import GitHubError


class Session:
    def __init__(self):
        self.rolled_back = False

    async def rollback(self):
        self.rolled_back = True


def snapshot():
    return SimpleNamespace(
        username="tshimbilunirsa",
        profile_json={"name": "Tshimbiluni", "avatar_url": "cached.png"},
        total_stars=3,
        total_forks=2,
        total_watchers=3,
        total_open_issues=0,
        total_repository_size_kb=100,
        total_contributions=20,
        commit_contributions=15,
        pull_request_contributions=2,
        issue_contributions=1,
        pull_request_review_contributions=2,
        contribution_period_start=None,
        contribution_period_end=None,
        language_stats_json=[],
        recent_repositories_json=[],
        synced_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_successful_github_refresh_updates_cache(monkeypatch):
    row = snapshot()

    async def collect(_self, _username):
        return {"username": "TshimbiluniRSA"}

    async def save(_session, data):
        assert data["username"] == "TshimbiluniRSA"
        return row

    monkeypatch.setenv("GITHUB_SYNC_TOKEN", "secret")
    monkeypatch.setattr(github.GitHubStatsService, "collect", collect)
    monkeypatch.setattr(github, "save_snapshot", save)
    response = await github.sync("secret", Session())
    assert response["profile"]["avatar_url"] == "cached.png"
    assert response["stale"] is False


@pytest.mark.asyncio
async def test_failed_refresh_returns_stale_cached_snapshot(monkeypatch):
    async def collect(_self, _username):
        raise GitHubError("offline")

    async def cached(_session):
        return snapshot()

    monkeypatch.setenv("GITHUB_SYNC_TOKEN", "secret")
    monkeypatch.setattr(github.GitHubStatsService, "collect", collect)
    monkeypatch.setattr(github, "cached_snapshot", cached)
    session = Session()
    response = await github.sync("secret", session)
    assert response["stale"] is True
    assert response["profile"]["avatar_url"] == "cached.png"
    assert session.rolled_back


@pytest.mark.asyncio
async def test_failed_refresh_without_cache_returns_error(monkeypatch):
    async def collect(_self, _username):
        raise GitHubError("offline")

    async def cached(_session):
        return None

    monkeypatch.setenv("GITHUB_SYNC_TOKEN", "secret")
    monkeypatch.setattr(github.GitHubStatsService, "collect", collect)
    monkeypatch.setattr(github, "cached_snapshot", cached)
    with pytest.raises(HTTPException) as error:
        await github.sync("secret", Session())
    assert error.value.status_code == 503


def test_only_supported_public_routes_are_registered():
    routes = {
        (method, route.path)
        for route in app.routes
        for method in getattr(route, "methods", set())
    }
    expected = {
        ("GET", "/health"),
        ("GET", "/ready"),
        ("POST", "/chat/message"),
        ("GET", "/github/stats"),
        ("POST", "/github/sync"),
        ("GET", "/cv/download"),
        ("GET", "/api/repositories/featured"),
    }
    public = {
        (method, path)
        for method, path in routes
        if path
        not in {"/", "/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"}
    }
    assert public == expected


class Result:
    def __init__(self, rows):
        self.rows = rows

    def scalars(self):
        return self

    def all(self):
        return self.rows


class RepositorySession(Session):
    def __init__(self, results):
        super().__init__()
        self.results = iter(results)

    async def execute(self, _statement):
        return Result(next(self.results))


def repository():
    return SimpleNamespace(
        id=1,
        github_id=10,
        name="portfolio",
        full_name="owner/portfolio",
        description="cached",
        html_url="https://github.com/owner/portfolio",
        language="TypeScript",
        languages_data={},
        topics=[],
        stargazers_count=1,
        forks_count=0,
        is_featured=True,
        last_synced_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
    )


@pytest.mark.asyncio
async def test_repository_refresh_failure_keeps_cached_rows(monkeypatch):
    from routers import repositories

    cached = repository()

    async def fail(*_args, **_kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr(repositories, "sync_github_repositories", fail)
    response = await repositories.get_featured_repositories(
        RepositorySession([[cached]])
    )
    assert response[0]["description"] == "cached"


@pytest.mark.asyncio
async def test_repository_refresh_failure_without_cache_errors(monkeypatch):
    from routers import repositories

    async def fail(*_args, **_kwargs):
        raise RuntimeError("offline")

    monkeypatch.setattr(repositories, "sync_github_repositories", fail)
    with pytest.raises(HTTPException) as error:
        await repositories.get_featured_repositories(RepositorySession([[], []]))
    assert error.value.status_code == 503
