import pytest
from fastapi.testclient import TestClient
from main import app
from routers.cv import storage
from services.github_stats import GitHubStatsService


def test_linkedin_routes_removed():
    assert all("linkedin" not in route.path.lower() for route in app.routes)


def test_health_is_independent():
    assert TestClient(app).get("/health").status_code == 200


def test_sync_requires_token(monkeypatch):
    monkeypatch.delenv("GITHUB_SYNC_TOKEN", raising=False)
    assert TestClient(app).post("/github/sync").status_code == 403


@pytest.mark.asyncio
async def test_repository_aggregation_and_forks_excluded(monkeypatch):
    service = GitHubStatsService("")

    async def get(client, path, params=None):
        if path.startswith("/users/") and not path.endswith("/repos"):
            return {"name": "A", "public_repos": 2, "followers": 3, "following": 4}
        if path.endswith("/repos"):
            return [
                {
                    "name": "owned",
                    "fork": False,
                    "owner": {"login": "me"},
                    "stargazers_count": 2,
                    "forks_count": 3,
                    "watchers_count": 4,
                    "open_issues_count": 5,
                    "size": 6,
                },
                {
                    "name": "fork",
                    "fork": True,
                    "owner": {"login": "me"},
                    "stargazers_count": 100,
                },
            ]
        if path.endswith("/languages"):
            return {"Python": 75, "TypeScript": 25}

    monkeypatch.setattr(service, "_get", get)
    data = await service.collect("me")
    assert data["repository_stats"] == {
        "total_stars": 2,
        "total_forks": 3,
        "total_watchers": 4,
        "total_open_issues": 5,
        "total_repository_size_kb": 6,
    }
    assert sum(x["percentage"] for x in data["top_languages"]) == 100


class FakeS3:
    async def exists(self, key):
        return True

    async def presigned_download(self, key, filename, expiry):
        return "https://signed.example/?secret=temporary"


def test_cv_download_presigned(monkeypatch):
    monkeypatch.setenv("S3_PRESIGNED_URL_EXPIRY_SECONDS", "300")
    app.dependency_overrides[storage] = lambda: FakeS3()
    try:
        response = TestClient(app).get("/cv/download")
        assert response.status_code == 200
        assert response.json()["expires_in"] == 300
        assert response.json()["filename"].endswith(".pdf")
    finally:
        app.dependency_overrides.clear()
