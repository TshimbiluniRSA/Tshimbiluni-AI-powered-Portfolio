from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (Column, String, Integer, Text, DateTime, Boolean, Index, ForeignKey, JSON, Float, )
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from .database import Base

class TimestampMixin:
    """Mixin to add timestamp fields to models."""
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, doc="When the record was created")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, doc="When the record was last updated")


class GitHubProfile(Base, TimestampMixin):
    __tablename__ = "github_profiles"

    username = Column(String(39), primary_key=True, index=True, doc="GitHub username (max 39 chars as per GitHub rules)")
    bio = Column(Text, doc="User's GitHub bio")
    public_repos = Column(Integer, default=0, doc="Number of public repositories")
    followers = Column(Integer, default=0, doc="Number of followers")
    following = Column(Integer, default=0, doc="Number of users being followed")
    profile_url = Column(String(255), doc="Full URL to GitHub profile")
    avatar_url = Column(String(500), doc="URL to profile avatar image")
    name = Column(String(255), doc="Display name on GitHub")
    company = Column(String(255), doc="Company information")
    location = Column(String(255), doc="Location information")
    blog = Column(String(500), doc="Blog/website URL")
    twitter_username = Column(String(15), doc="Twitter username")
    hireable = Column(Boolean, doc="Whether the user is hireable")
    last_fetched_at = Column(DateTime(timezone=True), server_default=func.now(), doc="When the data was last fetched from GitHub API")

    # Add indexes for commonly queried fields
    __table_args__ = (
        Index('idx_github_last_fetched', 'last_fetched_at'),
        Index('idx_github_public_repos', 'public_repos'),
        Index('idx_github_followers', 'followers'),
    )

    @validates('username')
    def validate_username(self, key: str, username: str) -> str:
        """Validate GitHub username format."""
        if not username:
            raise ValueError("Username cannot be empty")
        if len(username) > 39:
            raise ValueError("Username cannot exceed 39 characters")
        return username.lower().strip()

    @hybrid_property
    def is_data_stale(self) -> bool:
        if not self.last_fetched_at:
            return True
        last_fetched = self.last_fetched_at
        # Make last_fetched timezone-aware if it's naive
        if last_fetched.tzinfo is None or last_fetched.tzinfo.utcoffset(last_fetched) is None:
            last_fetched = last_fetched.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - last_fetched).days >= 1


class LinkedInProfile(Base, TimestampMixin):
    __tablename__ = "linkedin_profiles"

    username = Column(String(100), primary_key=True, index=True, doc="LinkedIn username or profile identifier")
    headline = Column(String(500), doc="Professional headline"
    )
    summary = Column(Text, doc="Professional summary/about section")
    profile_url = Column(String(500), nullable=False, doc="Full URL to LinkedIn profile")
    full_name = Column(String(255), doc="Full name as displayed on LinkedIn")
    location = Column(String(255), doc="Location information")
    industry = Column(String(255), doc="Industry information")
    connections_count = Column(String(50), doc="Number of connections (often shown as '500+' etc.)")
    profile_image_url = Column(String(500), doc="URL to profile image")
    last_scraped_at = Column(DateTime(timezone=True), server_default=func.now(), doc="When the data was last scraped from LinkedIn")
    scraping_successful = Column(Boolean, default=True,doc="Whether the last scraping attempt was successful")
    scraping_error = Column(Text, doc="Error message if scraping failed")

    # Add indexes for commonly queried fields
    __table_args__ = (
        Index('idx_linkedin_last_scraped', 'last_scraped_at'),
        Index('idx_linkedin_successful', 'scraping_successful'),
    )

    @validates('profile_url')
    def validate_profile_url(self, key: str, url: str) -> str:
        """Validate LinkedIn profile URL format."""
        if not url:
            raise ValueError("Profile URL cannot be empty")
        if not url.startswith(('https://linkedin.com', 'https://www.linkedin.com')):
            raise ValueError("Invalid LinkedIn profile URL")
        return url.strip()

    @hybrid_property
    def is_data_stale(self) -> bool:
        print('DEBUG last_scraped_at:', self.last_scraped_at, type(self.last_scraped_at), getattr(self.last_scraped_at, "tzinfo", None))
        if not self.last_scraped_at:
            return True
        last_scraped = self.last_scraped_at
        if isinstance(last_scraped, str):
            last_scraped = datetime.fromisoformat(last_scraped)
        if last_scraped.tzinfo is None or last_scraped.tzinfo.utcoffset(last_scraped) is None:
            last_scraped = last_scraped.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - last_scraped).days >= 1


class CVMetadata(Base, TimestampMixin):
    __tablename__ = "cv_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True, doc="Unique identifier for the CV record")
    filename = Column(String(255), nullable=False, doc="Original filename of the CV")
    filepath = Column(String(500), nullable=False, doc="Storage path of the CV file")
    file_size = Column(Integer, doc="File size in bytes")
    file_type = Column(String(50), doc="MIME type of the file")
    version = Column(Integer, default=1, doc="Version number of the CV")
    is_active = Column(Boolean, default=True, doc="Whether this CV version is currently active")
    download_count = Column(Integer, default=0, doc="Number of times this CV has been downloaded")
    description = Column(Text, doc="Description or notes about this CV version")

    # Add indexes for commonly queried fields
    __table_args__ = (
        Index('idx_cv_active', 'is_active'),
        Index('idx_cv_version', 'version'),
        Index('idx_cv_filename', 'filename'),
    )

    @validates('file_size')
    def validate_file_size(self, key: str, size: Optional[int]) -> Optional[int]:
        """Validate file size is reasonable."""
        if size is not None and size > 10 * 1024 * 1024:  # 10MB
            raise ValueError("CV file size cannot exceed 10MB")
        return size

    def __repr__(self) -> str:
        return f"<CVMetadata(id={self.id}, filename='{self.filename}', version={self.version})>"


class ChatHistory(Base, TimestampMixin):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True, doc="Unique identifier for the chat message")
    session_id = Column(String(255), nullable=False, index=True, doc="Chat session identifier")
    message_type = Column(String(20), nullable=False, doc="Type of message: 'user' or 'assistant'")
    content = Column(Text, nullable=False, doc="Message content")
    msg_metadata = Column(JSON, doc="Additional metadata like tokens used, model info, etc.")
    response_time_ms = Column(Integer, doc="Response time in milliseconds for assistant messages")
    tokens_used = Column(Integer, doc="Number of tokens used for this message")
    model_used = Column(String(100), doc="AI model used for generating the response")
    rating = Column(Integer, doc="User rating for the response (1-5)")

    # Add indexes for commonly queried fields
    __table_args__ = (
        Index('idx_chat_session_created', 'session_id', 'created_at'),
        Index('idx_chat_type', 'message_type'),
        Index('idx_chat_rating', 'rating'),
    )

    @validates('message_type')
    def validate_message_type(self, key: str, message_type: str) -> str:
        """Validate message type."""
        valid_types = ['user', 'assistant', 'system']
        if message_type not in valid_types:
            raise ValueError(f"Message type must be one of: {valid_types}")
        return message_type

    @validates('rating')
    def validate_rating(self, key: str, rating: Optional[int]) -> Optional[int]:
        """Validate rating is between 1 and 5."""
        if rating is not None and (rating < 1 or rating > 5):
            raise ValueError("Rating must be between 1 and 5")
        return rating

    def __repr__(self) -> str:
        return f"<ChatHistory(id={self.id}, session='{self.session_id[:8]}...', type='{self.message_type}')>"


class APIUsageLog(Base, TimestampMixin):
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, doc="Unique identifier for the API call log")
    api_provider = Column(String(50), nullable=False, doc="API provider (github, linkedin, openai, etc.)")
    endpoint = Column(String(255), doc="API endpoint called")
    method = Column(String(10), doc="HTTP method used")
    status_code = Column(Integer, doc="HTTP status code returned")
    response_time_ms = Column(Integer, doc="Response time in milliseconds")
    tokens_used = Column(Integer, doc="Tokens used (for LLM APIs)")
    cost_usd = Column(Float, doc="Cost in USD (if applicable)")
    error_message = Column(Text, doc="Error message if the call failed")
    request_metadata = Column(JSON, doc="Additional request metadata")

    # Add indexes for monitoring and analytics
    __table_args__ = (
        Index('idx_api_provider_created', 'api_provider', 'created_at'),
        Index('idx_api_status', 'status_code'),
        Index('idx_api_cost', 'cost_usd'),
    )

    @validates('api_provider')
    def validate_api_provider(self, key: str, provider: str) -> str:
        """Validate and normalize API provider name."""
        return provider.lower().strip()

    def __repr__(self) -> str:
        return f"<APIUsageLog(id={self.id}, provider='{self.api_provider}', status={self.status_code})>"