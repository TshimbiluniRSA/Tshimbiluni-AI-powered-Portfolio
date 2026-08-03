# Deployment readiness

The frontend remains on Render. A future AWS phase may add a public ALB, ECS Fargate FastAPI tasks, private RDS PostgreSQL, a private S3 bucket, and Secrets Manager. No AWS infrastructure is created here.

1. Configure the variables in `backend/src/.env.example` through the deployment secret/configuration system.
2. Run `alembic upgrade head` against PostgreSQL before application rollout.
3. Upload the owner PDF to the private object named by `S3_PUBLIC_CV_KEY`.
4. Give the future ECS task role least-privilege object access (`HeadObject`, `GetObject`, `PutObject`, `DeleteObject`) only for the public key and upload prefix.
5. Build with `docker build -t portfolio-backend:aws-ready backend/src`.
6. Configure load-balancer liveness as `/health`; use `/ready` for database-aware readiness.

The public frontend calls `GET /github/stats` and `GET /cv/download`. Only an internal operator or scheduler should call `POST /github/sync` with `X-GitHub-Sync-Token`.
