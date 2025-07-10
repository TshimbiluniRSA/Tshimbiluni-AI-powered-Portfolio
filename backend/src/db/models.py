from sqlalchemy import Column, String, Integer, Text, DateTime
from datetime import datetime
from .database import Base

class GitHubProfile(Base):
    __tablename__ = "github_profile"

    username = Column(String, primary_key=True, index=True)
    bio = Column(Text)
    public_repos = Column(Integer)
    followers = Column(Integer)
    profile_url = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)

class LinkedInProfile(Base):
    __tablename__ = "linkedin_profile"

    username = Column(String, primary_key=True, index=True)
    headline = Column(String)
    summary = Column(Text)
    profile_url = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)

class CVMetadata(Base):
    __tablename__ = "cv_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
