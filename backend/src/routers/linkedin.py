from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from services.linkedin_scraper import scrape_linkedin_public_profile, save_linkedin_profile
from schemas import LinkedInProfileResponse

router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sync", response_model=LinkedInProfileResponse)
def sync_linkedin_profile(url: str, db: Session = Depends(get_db)):
    try:
        profile_data = scrape_linkedin_public_profile(url)
        saved = save_linkedin_profile(db, profile_data)
        return saved
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
