# Secrets Setup

## Required OpenAI secret

Create an API key in the OpenAI platform and store it only as the backend
`OPENAI_API_KEY` environment variable. Never put the real value in source,
Docker images, frontend variables, documentation, or test fixtures.

The backend also accepts these non-secret settings:

```env
OPENAI_MODEL=gpt-5-mini
OPENAI_MAX_OUTPUT_TOKENS=800
OPENAI_REASONING_EFFORT=low
OPENAI_TIMEOUT_SECONDS=60
OPENAI_CONTEXT_MESSAGE_LIMIT=10
```

For Render, open the backend web service, choose **Environment**, add
`OPENAI_API_KEY` as a secret plus the five settings above, save, and manually
redeploy. For Docker Compose, export the same variables in the shell or place
them in the ignored `backend/src/.env` file before running `docker compose up`.

Confirm configuration without printing the key:

```bash
python -c "import os; print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
curl http://localhost:8000/api/chat/health
```

Rotate the OpenAI key immediately if it is ever disclosed.
