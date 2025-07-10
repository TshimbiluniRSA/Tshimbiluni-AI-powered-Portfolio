from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ---------- GitHub Profile ----------

class GitHubProfileBase(BaseModel):
    username: str
    bio: Optional[str] = None
    public_repos: Optional[int] = None
    followers: Optional[int] = None
    profile_url: Optional[str] = None
    updated_at: Optional[datetime] = None

class GitHubProfileResponse(GitHubProfileBase):
    class Config:
        orm_mode = True


# ---------- LinkedIn Profile ----------

class LinkedInProfileBase(BaseModel):
    username: str
    headline: Optional[str] = None
    summary: Optional[str] = None
    profile_url: Optional[str] = None
    updated_at: Optional[datetime] = None

class LinkedInProfileResponse(LinkedInProfileBase):
    class Config:
        orm_mode = True


# ---------- CV Metadata ----------

class CVMetadataBase(BaseModel):
    filename: str
    filepath: str
    uploaded_at: Optional[datetime] = None

class CVMetadataResponse(CVMetadataBase):
    id: int

    class Config:
        orm_mode = True
