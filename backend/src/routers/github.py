from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from services.github_fetcher import fetch_github_data, save_github_profile
from schemas import GitHubProfileResponse

router = APIRouter(prefix="/github", tags=["GitHub"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sync", response_model=GitHubProfileResponse)
def sync_github_profile(username: str = "TshimbiluniRSA", db: Session = Depends(get_db)):
    try:
        profile_data = fetch_github_data(username)
        saved = save_github_profile(db, profile_data)
        return saved
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
