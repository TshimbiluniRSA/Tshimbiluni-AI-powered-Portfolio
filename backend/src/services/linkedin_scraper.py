from crawl4ai import AsyncWebCrawler
from sqlalchemy.orm import Session
from db.models import LinkedInProfile
from datetime import datetime

async def scrape_linkedin_public_profile(url: str) -> dict:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)

    return {
        "username": result.get("title", "").split(" ")[0].lower() if result.get("title") else "",
        "headline": result.get("meta_title"),
        "summary": result.get("meta_description"),
        "profile_url": url,
        "updated_at": datetime.utcnow()
    }

def save_linkedin_profile(db: Session, profile_data: dict):
    existing = db.query(LinkedInProfile).filter_by(username=profile_data["username"]).first()
    
    if existing:
        for key, value in profile_data.items():
            setattr(existing, key, value)
    else:
        existing = LinkedInProfile(**profile_data)
        db.add(existing)

    db.commit()
    db.refresh(existing)
    return existing