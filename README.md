# Tshimbiluni AI-powered Portfolio

A React portfolio backed by FastAPI, PostgreSQL-compatible SQLAlchemy persistence, the OpenAI Responses API, official GitHub APIs, and private Amazon S3 storage.

## Supported architecture

The React frontend currently runs on Render. The backend is prepared for a later AWS phase consisting of an ALB, ECS Fargate, RDS PostgreSQL, private S3, and Secrets Manager; this repository intentionally does not provision infrastructure.

## Local development

```bash
cd backend/src
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

```bash
cd frontend
npm ci
npm run dev
```

SQLite is suitable locally. Set `DATABASE_URL=postgresql+asyncpg://...` in deployment. The liveness endpoint is `GET /health`; database readiness is `GET /ready`.

## GitHub statistics

`GET /github/stats` returns the configured owner's cached profile, repository aggregates, top languages, recent repositories, and 12-month contributions. It never calls GitHub for a public visitor. Run `POST /github/sync` with `X-GitHub-Sync-Token`; the value must match `GITHUB_SYNC_TOKEN`. Sync uses paginated GitHub REST repositories/languages and GraphQL `contributionsCollection`.

## Private S3 CV storage

Place the portfolio PDF at `S3_PUBLIC_CV_KEY` in the private `S3_BUCKET_NAME`. `GET /cv/download` checks the object and returns a short-lived presigned URL with a PDF attachment filename. `POST /cv/upload` validates a visitor PDF, writes a UUID-based temporary S3 object, parses it through OpenAI, persists structured data, and deletes the temporary object when `CV_DELETE_AFTER_PROCESSING=true`. The standard AWS credential provider chain is used; do not configure public bucket ACLs.

## Database and container

Production schema changes are explicit:

```bash
cd backend/src && alembic upgrade head
docker build -t portfolio-backend:aws-ready .
```

The image runs as a non-root user on port 8000 and has no browser runtime. ECS will need task-role permissions for `s3:HeadObject`, `s3:GetObject`, `s3:PutObject`, and `s3:DeleteObject`, restricted to the configured bucket keys.

See [`backend/src/.env.example`](backend/src/.env.example) and [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).
