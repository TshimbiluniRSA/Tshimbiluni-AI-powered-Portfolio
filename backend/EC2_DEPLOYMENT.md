# EC2 backend deployment

This runbook deploys only the FastAPI backend to the existing EC2 host. The frontend remains on Render. Nginx is installed on EC2 but will be configured as the public reverse proxy in a later step.

## Prerequisites

- Docker Engine and the Docker Compose plugin are installed on EC2.
- The EC2 instance can reach the private PostgreSQL RDS instance.
- The EC2 IAM instance role grants the required access to the private S3 bucket. Do not configure AWS access keys on the host or in the environment file.
- The EC2 security group does not expose port `8000`.
- The deployment user can write under `/opt/portfolio` and run Docker commands.

## 1. Clone the repository

```bash
cd /opt/portfolio
git clone https://github.com/TshimbiluniRSA/Tshimbiluni-AI-powered-Portfolio.git backend
```

The command works when `/opt/portfolio/backend` does not exist or already exists as an empty directory. If that path exists and is not empty, do not clone over it; verify that it is the intended checkout and use the update procedure below instead. Never put a GitHub token in the clone URL.

## 2. Create the production environment file

Copy the safe template, restrict access, and open it in an editor:

```bash
cd /opt/portfolio/backend
mkdir -p /opt/portfolio/config
chmod 700 /opt/portfolio/config
cp backend/src/.env.production.example /opt/portfolio/config/backend.env
chmod 600 /opt/portfolio/config/backend.env
vi /opt/portfolio/config/backend.env
```

Replace every placeholder in `backend.env` with the production value. Enter secrets in the editor; do not use `echo` or command-line arguments that would save secret values in shell history.

The RDS password in `DATABASE_URL` must be URL-encoded. Characters such as `@`, `:`, `/`, `?`, `#`, and `%` cannot appear literally in the password portion of the URL. Keep the `postgresql+asyncpg` driver and use this structure:

```text
postgresql+asyncpg://portfolio_admin:<URL_ENCODED_PASSWORD>@<RDS_HOST>:5432/portfolio
```

The repository's `.env.production.example` contains placeholders only and is safe to commit. Actual `.env` and `backend.env` files match the repository's `*.env` ignore rule and must remain untracked.

## 3. Build the backend image

```bash
cd /opt/portfolio/backend/backend/src
docker compose -f compose.production.yml build
```

## 4. Run database migrations

```bash
docker compose -f compose.production.yml run --rm backend alembic upgrade head
```

The migration must finish successfully before the backend is started. If it fails, inspect the error and correct the database configuration or connectivity; do not continue to the next step.

## 5. Start the backend

```bash
docker compose -f compose.production.yml up -d backend
```

The Compose service uses `restart: unless-stopped`, so Docker restarts it after a host reboot unless an operator explicitly stopped it.

## 6. Verify the deployment

```bash
docker compose -f compose.production.yml ps
docker compose -f compose.production.yml logs --tail=100 backend
curl -f http://127.0.0.1:8000/health
curl -f http://127.0.0.1:8000/ready
```

`/health` is the container liveness endpoint. `/ready` also checks PostgreSQL connectivity. Both commands must succeed for a healthy, ready deployment.

## 7. Stop, restart, or remove the service

Run these commands from `/opt/portfolio/backend/backend/src` as needed:

```bash
docker compose -f compose.production.yml stop backend
docker compose -f compose.production.yml restart backend
docker compose -f compose.production.yml down
```

`down` removes the Compose container and network but does not remove the built image or production environment file.

## 8. Update the backend later

```bash
cd /opt/portfolio/backend
git pull
cd backend/src
docker compose -f compose.production.yml build
docker compose -f compose.production.yml run --rm backend alembic upgrade head
docker compose -f compose.production.yml up -d backend
```

As during the initial deployment, migrations must succeed before starting the updated backend. Re-run the verification commands afterward.

## Security notes

- Compose publishes FastAPI only as `127.0.0.1:8000:8000`; it is not reachable directly through an EC2 public interface.
- Port `8000` must remain closed in the EC2 security group.
- Do not commit `/opt/portfolio/config/backend.env`, `.env` files, credentials, or real database URLs.
- Do not use AWS access keys. The EC2 IAM instance role supplies AWS authentication for S3.
- The frontend remains hosted on Render.
- Nginx will become the backend's public entry point in a later deployment step.
- The Dockerfile's existing health check calls `/health`; Compose intentionally inherits it rather than defining a competing health check.
- Production PostgreSQL does not use the local `/app/data` directory. That path is only used by the application's SQLite development fallback, and no source or data directory is mounted into the production container.
