from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, validator, root_validator, HttpUrl
from pydantic.config import ConfigDict


class MessageType(str, Enum):
    """Enumeration for chat message types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class APIProvider(str, Enum):
    """Enumeration for external API providers."""
    GITHUB = "github"
    LINKEDIN = "linkedin"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class BaseResponseModel(BaseModel):
    """Base model for all API responses."""
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


# ---------- GitHub Profile Schemas ----------

class GitHubProfileBase(BaseModel):
    """Base schema for GitHub profile data."""
    username: str = Field(..., min_length=1, max_length=39, description="GitHub username (max 39 characters)", example="TshimbiluniRSA")
    bio: Optional[str] = Field(None, max_length=1000, description="User's GitHub bio")
    public_repos: Optional[int] = Field(None, ge=0, description="Number of public repositories")
    followers: Optional[int] = Field(None, ge=0, description="Number of followers")
    following: Optional[int] = Field(None, ge=0, description="Number of users being followed")
    profile_url: Optional[HttpUrl] = Field(None, description="Full URL to GitHub profile")
    avatar_url: Optional[HttpUrl] = Field(None, description="URL to profile avatar image")
    name: Optional[str] = Field(None, max_length=255, description="Display name on GitHub")
    company: Optional[str] = Field(None, max_length=255, description="Company information")
    location: Optional[str] = Field(None, max_length=255, description="Location information")
    blog: Optional[HttpUrl] = Field(None, description="Blog/website URL")
    twitter_username: Optional[str] = Field(None, max_length=15, description="Twitter username")
    hireable: Optional[bool] = Field(None,description="Whether the user is hireable")

    @validator('username')
    def validate_username(cls, v: str) -> str:
        """Validate GitHub username format."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v.lower().strip()

    @validator('twitter_username')
    def validate_twitter_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate Twitter username format."""
        if v and v.startswith('@'):
            return v[1:]  # Remove @ symbol if present
        return v


class GitHubProfileCreate(GitHubProfileBase):
    """Schema for creating a new GitHub profile."""
    pass


class GitHubProfileUpdate(BaseModel):
    """Schema for updating an existing GitHub profile."""
    bio: Optional[str] = Field(None, max_length=1000)
    public_repos: Optional[int] = Field(None, ge=0)
    followers: Optional[int] = Field(None, ge=0)
    following: Optional[int] = Field(None, ge=0)
    profile_url: Optional[HttpUrl] = None
    avatar_url: Optional[HttpUrl] = None
    name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    blog: Optional[HttpUrl] = None
    twitter_username: Optional[str] = Field(None, max_length=15)
    hireable: Optional[bool] = None


class GitHubProfileResponse(GitHubProfileBase, BaseResponseModel):
    """Schema for GitHub profile API responses."""
    created_at: datetime = Field(description="When the record was created")
    updated_at: datetime = Field(description="When the record was last updated")
    last_fetched_at: Optional[datetime] = Field(
        None,
        description="When the data was last fetched from GitHub API"
    )
    is_data_stale: bool = Field(
        description="Whether the GitHub data is older than 24 hours"
    )


# ---------- LinkedIn Profile Schemas ----------

class LinkedInProfileBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=100, description="LinkedIn username or profile identifier", example="tshimbiluni-nedambale")
    headline: Optional[str] = Field(None, max_length=500, description="Professional headline")
    summary: Optional[str] = Field(None,description="Professional summary/about section")
    profile_url: HttpUrl = Field(..., description="Full URL to LinkedIn profile")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name as displayed on LinkedIn")
    location: Optional[str] = Field(None, max_length=255, description="Location information")
    industry: Optional[str] = Field(None, max_length=255, description="Industry information")
    connections_count: Optional[str] = Field(None, max_length=50, description="Number of connections (often shown as '500+' etc.)")
    profile_image_url: Optional[HttpUrl] = Field(None,description="URL to profile image")

    @validator('profile_url')
    def validate_profile_url(cls, v: HttpUrl) -> HttpUrl:
        """Validate LinkedIn profile URL format."""
        url_str = str(v)
        if not url_str.startswith(('https://linkedin.com', 'https://www.linkedin.com')):
            raise ValueError("Invalid LinkedIn profile URL")
        return v


class LinkedInProfileCreate(LinkedInProfileBase):
    """Schema for creating a new LinkedIn profile."""
    pass


class LinkedInProfileUpdate(BaseModel):
    """Schema for updating an existing LinkedIn profile."""
    headline: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = None
    full_name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=255)
    connections_count: Optional[str] = Field(None, max_length=50)
    profile_image_url: Optional[HttpUrl] = None


class LinkedInProfileResponse(LinkedInProfileBase, BaseResponseModel):
    """Schema for LinkedIn profile API responses."""
    created_at: datetime = Field(description="When the record was created")
    updated_at: datetime = Field(description="When the record was last updated")
    last_scraped_at: Optional[datetime] = Field(
        None,
        description="When the data was last scraped from LinkedIn"
    )
    scraping_successful: bool = Field(
        True,
        description="Whether the last scraping attempt was successful"
    )
    scraping_error: Optional[str] = Field(
        None,
        description="Error message if scraping failed"
    )
    is_data_stale: bool = Field(
        description="Whether the LinkedIn data is older than 7 days"
    )
    @validator('last_scraped_at', pre=True, always=True)
    def patch_last_scraped_at_tz(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            v = datetime.fromisoformat(v)
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            return v.replace(tzinfo=timezone.utc)
        return v


# ---------- CV Metadata Schemas ----------

class CVMetadataBase(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename of the CV", example="Tshimbiluni_Nedambale_CV.pdf")
    filepath: str = Field(..., min_length=1, max_length=500, description="Storage path of the CV file")
    file_size: Optional[int] = Field(None, ge=0, le=10*1024*1024, description="File size in bytes")
    file_type: Optional[str] = Field(None, max_length=50, description="MIME type of the file")
    version: int = Field(1, ge=1, description="Version number of the CV")
    is_active: bool = Field(True, description="Whether this CV version is currently active")
    description: Optional[str] = Field(None, description="Description or notes about this CV version")

    @validator('filename')
    def validate_filename(cls, v: str) -> str:
        """Validate filename format."""
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")
        # Check for valid file extensions
        valid_extensions = ['.pdf', '.doc', '.docx']
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"File must have one of these extensions: {valid_extensions}")
        return v.strip()


class CVMetadataCreate(CVMetadataBase):
    """Schema for creating new CV metadata."""
    pass


class CVMetadataUpdate(BaseModel):
    """Schema for updating existing CV metadata."""
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    filepath: Optional[str] = Field(None, min_length=1, max_length=500)
    file_size: Optional[int] = Field(None, ge=0, le=10*1024*1024)
    file_type: Optional[str] = Field(None, max_length=50)
    version: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None
    description: Optional[str] = None


class CVMetadataResponse(CVMetadataBase, BaseResponseModel):
    """Schema for CV metadata API responses."""
    id: int = Field(description="Unique identifier for the CV record")
    created_at: datetime = Field(description="When the record was created")
    updated_at: datetime = Field(description="When the record was last updated")
    download_count: int = Field(0,ge=0,description="Number of times this CV has been downloaded")


# ---------- Chat History Schemas ----------

class ChatMessageBase(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=255, description="Chat session identifier")
    message_type: MessageType = Field(..., description="Type of message: 'user', 'assistant', or 'system'")
    content: str = Field(..., min_length=1, description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata like tokens used, model info, etc.")


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a new chat message."""
    pass


class ChatMessageResponse(ChatMessageBase, BaseResponseModel):
    """Schema for chat message API responses."""
    id: int = Field(description="Unique identifier for the chat message")
    created_at: datetime = Field(description="When the message was created")
    updated_at: datetime = Field(description="When the message was last updated")
    response_time_ms: Optional[int] = Field(None, ge=0, description="Response time in milliseconds for assistant messages")
    tokens_used: Optional[int] = Field(None,ge=0,description="Number of tokens used for this message")
    model_used: Optional[str] = Field(None,max_length=100,description="AI model used for generating the response")
    rating: Optional[int] = Field(None, ge=1, le=5, description="User rating for the response (1-5)")


class ChatSessionResponse(BaseResponseModel):
    """Schema for chat session information."""
    session_id: str = Field(description="Chat session identifier")
    messages: List[ChatMessageResponse] = Field(default_factory=list, description="List of messages in the session")
    message_count: int = Field(ge=0,description="Total number of messages in the session")
    created_at: datetime = Field(description="When the session was created")
    last_activity: datetime = Field(description="Last activity in the session")


# ---------- API Usage Log Schemas ----------

class APIUsageLogBase(BaseModel):
    """Base schema for API usage logging."""
    api_provider: APIProvider = Field(..., description="API provider (github, linkedin, openai, etc.)")
    endpoint: Optional[str] = Field(None, max_length=255, description="API endpoint called")
    method: Optional[str] = Field(None, max_length=10, description="HTTP method used")
    status_code: Optional[int] = Field(None, ge=100, le=599, description="HTTP status code returned")
    response_time_ms: Optional[int] = Field(None, ge=0, description="Response time in milliseconds")
    tokens_used: Optional[int] = Field(None, ge=0, description="Tokens used (for LLM APIs)")
    cost_usd: Optional[float] = Field(None, ge=0, description="Cost in USD (if applicable)")
    error_message: Optional[str] = Field(None, description="Error message if the call failed")
    request_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional request metadata")


class APIUsageLogCreate(APIUsageLogBase):
    """Schema for creating API usage log entries."""
    pass


class APIUsageLogResponse(APIUsageLogBase, BaseResponseModel):
    """Schema for API usage log responses."""
    id: int = Field(description="Unique identifier for the API call log")
    created_at: datetime = Field(description="When the API call was logged")


# ---------- Common Response Schemas ----------

class HealthCheckResponse(BaseModel):
    """Schema for health check responses."""
    status: str = Field(description="Health status")
    timestamp: datetime = Field(description="Health check timestamp")
    database: bool = Field(description="Database connectivity status")
    external_apis: Dict[str, bool] = Field(default_factory=dict,description="External API connectivity status")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(None,description="Additional error details")
    timestamp: datetime = Field(description="Error timestamp")


class PaginatedResponse(BaseModel):
    """Schema for paginated responses."""
    items: List[Any] = Field(description="List of items")
    total: int = Field(ge=0, description="Total number of items")
    page: int = Field(ge=1, description="Current page number")
    size: int = Field(ge=1, description="Items per page")
    pages: int = Field(ge=0, description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


class SyncResponse(BaseModel):
    """Schema for sync operation responses."""
    success: bool = Field(description="Whether the sync was successful")
    message: str = Field(description="Sync status message")
    data: Optional[Dict[str, Any]] = Field(None,description="Synced data")
    errors: Optional[List[str]] = Field(None,description="List of errors that occurred during sync")
    timestamp: datetime = Field(description="Sync timestamp")


# ---------- Request Schemas ----------

class ChatRequest(BaseModel):
    """Schema for chat API requests."""
    message: str = Field(...,min_length=1,max_length=10000,description="User message content")
    session_id: Optional[str] = Field(None, description="Optional session ID to continue conversation")
    model: Optional[str] = Field(None,description="Optional model to use for the response")
    metadata: Optional[Dict[str, Any]] = Field(None,description="Optional metadata for the request")


class GitHubSyncRequest(BaseModel):
    """Schema for GitHub sync requests."""
    username: str = Field(...,min_length=1,max_length=39,description="GitHub username to sync")
    force_refresh: bool = Field(False,description="Force refresh even if data is not stale")


class LinkedInSyncRequest(BaseModel):
    """Schema for LinkedIn sync requests."""
    profile_url: HttpUrl = Field(...,description="LinkedIn profile URL to scrape")
    force_refresh: bool = Field(False,description="Force refresh even if data is not stale")


class CVUploadResponse(BaseModel):
    """Schema for CV upload responses."""
    success: bool = Field(description="Whether the upload was successful")
    message: str = Field(description="Upload status message")
    cv_metadata: Optional[CVMetadataResponse] = Field(None,description="CV metadata if upload was successful")
    file_url: Optional[str] = Field(None,description="URL to access the uploaded file")