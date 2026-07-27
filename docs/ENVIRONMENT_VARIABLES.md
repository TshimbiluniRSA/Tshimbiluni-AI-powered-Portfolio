# Environment Variables Configuration

## OpenAI chatbot configuration

The backend uses the OpenAI Responses API. Configure these variables in local
`backend/src/.env` files and in the Render service dashboard; never commit a
real key.

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
OPENAI_MAX_OUTPUT_TOKENS=800
OPENAI_REASONING_EFFORT=low
OPENAI_TIMEOUT_SECONDS=60
OPENAI_CONTEXT_MESSAGE_LIMIT=10
```

`OPENAI_API_KEY` is required for chat/CV requests. The remaining values are
optional and use the defaults shown. `MAX_TOKENS` remains a compatibility
fallback only when `OPENAI_MAX_OUTPUT_TOKENS` is unset.

## Other backend configuration

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/portfolio_db
CORS_ORIGINS=https://your-frontend-domain.com
GITHUB_TOKEN=
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_REDIRECT_URI=https://your-domain.com/api/linkedin/oauth/callback
LOG_LEVEL=INFO
```

For local development, SQLite may be used:

```env
DATABASE_URL=sqlite+aiosqlite:///./portfolio.db
```

## Render deployment

Add all six OpenAI variables to the backend web service in **Render Dashboard →
Environment**. Mark `OPENAI_API_KEY` secret, save the changes, and manually
redeploy the latest commit. Do not add the key to frontend environment values.
Verify `/api/chat/health` reports the `openai` integration as configured, then
exercise both `/api/chat/message` and `/api/chat/stream`.

## Security

Never commit `.env` files or disclose keys in logs. Rotate a key immediately if
it is exposed, and use Render's secret environment storage in production.
