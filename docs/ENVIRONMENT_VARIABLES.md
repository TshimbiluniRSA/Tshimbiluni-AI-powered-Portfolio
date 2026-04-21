# Environment Variables Configuration

This document lists all environment variables required for the Tshimbiluni AI-powered Portfolio application.

## Database Configuration

```bash
# Database URL for SQLAlchemy
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/portfolio_db
# Or for SQLite (development only)
DATABASE_URL=sqlite+aiosqlite:///./portfolio.db
```

## LLM Configuration

```bash
# Default LLM provider (llama, openai, anthropic, gemini, ollama)
DEFAULT_LLM_PROVIDER=gemini

# Gemini API Key (recommended)
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LLaMA/Hugging Face Configuration (optional)
LLAMA_API_URL=your_llama_endpoint_here
HUGGINGFACE_TOKEN=your_huggingface_token_here

# Ollama Configuration (optional)
OLLAMA_BASE_URL=http://localhost:11434

# General LLM Settings
DEFAULT_LLM_MODEL=llama
MAX_TOKENS=2048
TEMPERATURE=0.7
LLM_TIMEOUT=60
```

## GitHub Integration

```bash
# GitHub Personal Access Token (for higher API rate limits)
GITHUB_TOKEN=ghp_your_github_token_here
```

## LinkedIn Integration

### OAuth Configuration (for user authentication)
```bash
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
LINKEDIN_REDIRECT_URI=https://your-domain.com/api/linkedin/oauth/callback
```

### Scraping Configuration (optional - for profile scraping)
```bash
# If you're using LinkedIn profile scraping, configure these as needed
# Note: LinkedIn scraping may be subject to rate limits and ToS restrictions
```

## Server Configuration

```bash
# Server host and port
HOST=0.0.0.0
PORT=8000

# CORS configuration (comma-separated list of allowed origins)
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com

# Environment (development, staging, production)
ENVIRONMENT=production
```

## Logging Configuration

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log file path (optional)
LOG_FILE=logs/app.log
```

## Security Configuration

```bash
# Secret key for session management (generate a secure random string)
SECRET_KEY=your_secure_secret_key_here

# JWT configuration (if implementing JWT authentication)
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

## Feature Flags (optional)

```bash
# Enable/disable specific features
ENABLE_CV_UPLOAD=true
ENABLE_GITHUB_SYNC=true
ENABLE_LINKEDIN_OAUTH=true
ENABLE_CHAT=true
```

## Development Configuration

For development, create a `.env` file in the root directory with the following minimal configuration:

```bash
# Development Environment Variables
DATABASE_URL=sqlite+aiosqlite:///./portfolio.db
DEFAULT_LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/linkedin/oauth/callback
LOG_LEVEL=DEBUG
```

## Production Configuration (Render.com)

For deployment on Render.com, configure these environment variables in the Render dashboard:

### Required Variables
- `DATABASE_URL` - Provided by Render PostgreSQL service
- `DEFAULT_LLM_PROVIDER=gemini`
- `GEMINI_API_KEY` - Your Gemini API key

### Recommended Variables
- `GITHUB_TOKEN` - For higher API rate limits
- `LINKEDIN_CLIENT_ID` - For OAuth
- `LINKEDIN_CLIENT_SECRET` - For OAuth
- `LINKEDIN_REDIRECT_URI` - Your production callback URL
- `LOG_LEVEL=INFO`
- `ENVIRONMENT=production`

### Optional Variables
- Additional LLM provider keys if you want to support multiple providers
- Custom CORS origins
- Feature flags

## Verification

After setting up environment variables, you can verify the configuration by:

1. Starting the application: `uvicorn backend.src.main:app --reload`
2. Visiting the health check endpoint: `http://localhost:8000/api/chat/health`
3. Checking the logs for "LLM Client initialized with default provider: gemini"

## Security Notes

⚠️ **IMPORTANT**: 
- Never commit `.env` files or any files containing secrets to version control
- Rotate API keys and secrets regularly
- Use environment-specific configurations
- Keep secrets in secure credential stores in production
- The LinkedIn credentials shown above are examples - use your own credentials
