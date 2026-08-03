"""GitHub REST/GraphQL collection and snapshot persistence."""

import logging
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import GitHubStatsSnapshot

log = logging.getLogger(__name__)
API = "https://api.github.com"


class GitHubError(Exception):
    pass


class GitHubStatsService:
    def __init__(self, token: str | None = None):
        self.token = token if token is not None else os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "portfolio-backend",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def _get(self, client, path, params=None):
        try:
            response = await client.get(
                f"{API}{path}", headers=self.headers, params=params
            )
        except httpx.TimeoutException as exc:
            raise GitHubError("GitHub request timed out") from exc
        if response.status_code == 401:
            raise GitHubError("GitHub authentication failed")
        if (
            response.status_code == 403
            and response.headers.get("X-RateLimit-Remaining") == "0"
        ):
            raise GitHubError("GitHub rate limit exceeded")
        if not response.is_success:
            raise GitHubError("GitHub service request failed")
        return response.json()

    async def repositories(self, client, username):
        result = []
        page = 1
        while True:
            batch = await self._get(
                client,
                f"/users/{username}/repos",
                {"per_page": 100, "page": page, "sort": "updated"},
            )
            result.extend(batch)
            if len(batch) < 100:
                return result
            page += 1

    async def contributions(self, client, username):
        if not self.token:
            return {
                "total": 0,
                "commits": 0,
                "pull_requests": 0,
                "issues": 0,
                "pull_request_reviews": 0,
                "period_start": None,
                "period_end": None,
            }
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=365)
        query = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){contributionCalendar{totalContributions} totalCommitContributions totalPullRequestContributions totalIssueContributions totalPullRequestReviewContributions startedAt endedAt}}}"""
        try:
            response = await client.post(
                f"{API}/graphql",
                headers=self.headers,
                json={
                    "query": query,
                    "variables": {
                        "login": username,
                        "from": start.isoformat(),
                        "to": end.isoformat(),
                    },
                },
            )
        except httpx.TimeoutException as exc:
            raise GitHubError("GitHub request timed out") from exc
        if response.status_code == 401:
            raise GitHubError("GitHub authentication failed")
        if not response.is_success:
            raise GitHubError("GitHub contribution request failed")
        payload = response.json()
        if payload.get("errors") or not payload.get("data", {}).get("user"):
            raise GitHubError("GitHub contribution data unavailable")
        c = payload["data"]["user"]["contributionsCollection"]
        return {
            "total": c["contributionCalendar"]["totalContributions"],
            "commits": c["totalCommitContributions"],
            "pull_requests": c["totalPullRequestContributions"],
            "issues": c["totalIssueContributions"],
            "pull_request_reviews": c["totalPullRequestReviewContributions"],
            "period_start": c["startedAt"][:10],
            "period_end": c["endedAt"][:10],
        }

    async def collect(self, username):
        async with httpx.AsyncClient(timeout=30) as client:
            profile = await self._get(client, f"/users/{username}")
            repos = await self.repositories(client, username)
            owned = [
                r
                for r in repos
                if not r.get("fork")
                and r.get("owner", {}).get("login", "").lower() == username.lower()
            ]
            languages = defaultdict(int)
            for repo in owned:
                try:
                    for name, count in (
                        await self._get(
                            client, f"/repos/{username}/{repo['name']}/languages"
                        )
                    ).items():
                        languages[name] += count
                except GitHubError:
                    log.warning(
                        "GitHub language data unavailable for %s", repo.get("name")
                    )
            contributions = await self.contributions(client, username)
        total = sum(languages.values())
        top = [
            {
                "name": n,
                "bytes": b,
                "percentage": round(b * 100 / total, 2) if total else 0.0,
            }
            for n, b in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:8]
        ]
        return {
            "username": username,
            "profile": {
                "name": profile.get("name"),
                "avatar_url": profile.get("avatar_url"),
                "profile_url": profile.get("html_url"),
                "bio": profile.get("bio"),
                "company": profile.get("company"),
                "location": profile.get("location"),
                "followers": profile.get("followers", 0),
                "following": profile.get("following", 0),
                "public_repositories": profile.get("public_repos", 0),
            },
            "repository_stats": {
                "total_stars": sum(r.get("stargazers_count", 0) for r in owned),
                "total_forks": sum(r.get("forks_count", 0) for r in owned),
                "total_watchers": sum(r.get("watchers_count", 0) for r in owned),
                "total_open_issues": sum(r.get("open_issues_count", 0) for r in owned),
                "total_repository_size_kb": sum(r.get("size", 0) for r in owned),
            },
            "contributions": contributions,
            "top_languages": top,
            "recent_repositories": [
                {
                    "name": r["name"],
                    "description": r.get("description"),
                    "url": r.get("html_url"),
                    "updated_at": r.get("updated_at"),
                    "stars": r.get("stargazers_count", 0),
                    "forks": r.get("forks_count", 0),
                }
                for r in owned[:6]
            ],
            "last_synced_at": datetime.now(timezone.utc),
        }


async def save_snapshot(session: AsyncSession, data: dict):
    row = (
        await session.execute(
            select(GitHubStatsSnapshot).where(
                GitHubStatsSnapshot.username == data["username"].lower()
            )
        )
    ).scalar_one_or_none()
    if not row:
        row = GitHubStatsSnapshot(username=data["username"].lower())
        session.add(row)
    p = data["repository_stats"]
    c = data["contributions"]
    row.profile_json = data["profile"]
    row.total_stars = p["total_stars"]
    row.total_forks = p["total_forks"]
    row.total_watchers = p["total_watchers"]
    row.total_open_issues = p["total_open_issues"]
    row.total_repository_size_kb = p["total_repository_size_kb"]
    row.total_contributions = c["total"]
    row.commit_contributions = c["commits"]
    row.pull_request_contributions = c["pull_requests"]
    row.issue_contributions = c["issues"]
    row.pull_request_review_contributions = c["pull_request_reviews"]
    row.contribution_period_start = c["period_start"]
    row.contribution_period_end = c["period_end"]
    row.language_stats_json = data["top_languages"]
    row.recent_repositories_json = data["recent_repositories"]
    row.synced_at = data["last_synced_at"]
    await session.commit()
    await session.refresh(row)
    return row


def serialize(row):
    return {
        "username": row.username,
        "profile": row.profile_json,
        "repository_stats": {
            "total_stars": row.total_stars,
            "total_forks": row.total_forks,
            "total_watchers": row.total_watchers,
            "total_open_issues": row.total_open_issues,
            "total_repository_size_kb": row.total_repository_size_kb,
        },
        "contributions": {
            "total": row.total_contributions,
            "commits": row.commit_contributions,
            "pull_requests": row.pull_request_contributions,
            "issues": row.issue_contributions,
            "pull_request_reviews": row.pull_request_review_contributions,
            "period_start": row.contribution_period_start,
            "period_end": row.contribution_period_end,
        },
        "top_languages": row.language_stats_json or [],
        "recent_repositories": row.recent_repositories_json or [],
        "last_synced_at": row.synced_at,
    }
