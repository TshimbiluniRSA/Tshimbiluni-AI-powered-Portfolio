import requests
from sqlalchemy.orm import Session
from db.models import GitHubProfile
from datetime import datetime

GITHUB_API_URL = "https://api.github.com/TshimbiluniRSA/"

def fetch_github_data(username: str) -> dict:
    url = f"{GITHUB_API_URL}{username}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code}")

    data = response.json()
    return {
        "username": username,
        "bio": data.get("bio"),
        "public_repos": data.get("public_repos"),
        "followers": data.get("followers"),
        "profile_url": data.get("html_url"),
        "updated_at": datetime.utcnow()
    }

def save_github_profile(db: Session, profile_data: dict):
    existing = db.query(GitHubProfile).filter_by(username=profile_data["username"]).first()
    
    if existing:
        # Update existing record
        for key, value in profile_data.items():
            setattr(existing, key, value)
    else:
        # Create new record
        existing = GitHubProfile(**profile_data)
        db.add(existing)

    db.commit()
    db.refresh(existing)
    return existing
