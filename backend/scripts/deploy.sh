#!/usr/bin/env bash
# Rebuilds and restarts the production backend on the EC2 host.
#
# Run as ssm-user from the updated checkout; the GitHub Actions deploy
# workflow calls it through SSM Run Command after fast-forwarding to the
# merged commit. It can also be run by hand for a manual redeploy.
set -euo pipefail

cd "$(dirname "$0")/../src"

IMAGE=portfolio-backend:production
PREVIOUS=portfolio-backend:previous

compose() {
  docker compose -f compose.production.yml "$@"
}

wait_until_healthy() {
  for _ in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:8000/health >/dev/null &&
      curl -fsS http://127.0.0.1:8000/ready >/dev/null; then
      return 0
    fi
    sleep 2
  done
  return 1
}

echo "==> Deploying $(git rev-parse --short HEAD): $(git log -1 --format=%s)"

# Keep the running image so a failed health check can fall back to it.
if docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker tag "$IMAGE" "$PREVIOUS"
fi

echo "==> Building image"
compose build

echo "==> Running migrations"
compose run --rm backend alembic upgrade head

echo "==> Starting backend"
compose up -d backend

echo "==> Waiting for /health and /ready"
if wait_until_healthy; then
  echo "==> Backend is healthy"
  docker image prune -f >/dev/null
  exit 0
fi

echo "!! Health checks failed; recent logs:"
compose logs --tail=100 backend

if docker image inspect "$PREVIOUS" >/dev/null 2>&1; then
  echo "==> Rolling back to the previous image"
  docker tag "$PREVIOUS" "$IMAGE"
  compose up -d --no-build backend
  if wait_until_healthy; then
    echo "==> Rolled back; previous version is serving traffic"
  else
    echo "!! Previous image is also unhealthy"
  fi
fi

exit 1
