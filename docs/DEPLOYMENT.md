# Deployment Guide

This guide covers different deployment options for the Tshimbiluni AI-powered Portfolio.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Deployment Options](#deployment-options)
  - [Docker Compose (Simple)](#docker-compose-simple)
  - [Cloud Platforms](#cloud-platforms)
  - [Kubernetes](#kubernetes)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required
- Docker and Docker Compose
- Domain name (for production)
- SSL certificate (Let's Encrypt recommended)

### Optional but Recommended
- PostgreSQL database (for production)
- Redis (for caching)
- Reverse proxy (Nginx/Traefik)
- Monitoring tools (Prometheus, Grafana)

## Environment Configuration

### Backend Configuration

Create `backend/.env` with production values:

```env
# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database (PostgreSQL for production)
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/portfolio

# LLM Provider (configure at least one)
LLAMA_API_URL=https://api-inference.huggingface.co/models/...
HUGGINGFACE_TOKEN=your_production_token

# OR use OpenAI
OPENAI_API_KEY=your_openai_key

# Security
SESSION_SECRET_KEY=your_very_long_random_secret_key_here_min_32_chars

# CORS (restrict to your domain)
CORS_ORIGINS=https://yourdomain.com

# GitHub
GITHUB_TOKEN=your_github_token
```

### Frontend Configuration

Create `frontend/.env.production`:

```env
VITE_API_URL=https://api.yourdomain.com
VITE_GITHUB_USERNAME=TshimbiluniRSA
```

## Deployment Options

### Docker Compose (Simple)

Best for: Small to medium deployments, VPS hosting

#### 1. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    restart: always
    env_file: backend/.env
    depends_on:
      - db
    networks:
      - app-network

  frontend:
    build: ./frontend
    restart: always
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: portfolio
      POSTGRES_USER: portfolio_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    restart: always
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

#### 2. Deploy

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### Cloud Platforms

#### AWS (Elastic Beanstalk)

1. Install AWS CLI and EB CLI
2. Initialize:
   ```bash
   eb init -p docker portfolio-app
   ```
3. Create environment:
   ```bash
   eb create portfolio-prod
   ```
4. Deploy:
   ```bash
   eb deploy
   ```

#### Google Cloud Platform (Cloud Run)

```bash
# Backend
gcloud builds submit --tag gcr.io/PROJECT_ID/backend ./backend
gcloud run deploy backend --image gcr.io/PROJECT_ID/backend

# Frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/frontend ./frontend
gcloud run deploy frontend --image gcr.io/PROJECT_ID/frontend
```

#### Heroku

```bash
# Backend
cd backend
heroku create portfolio-backend
git push heroku main

# Frontend
cd frontend
heroku create portfolio-frontend
heroku buildpacks:set heroku/nodejs
git push heroku main
```

#### DigitalOcean App Platform

1. Create App via dashboard
2. Connect GitHub repository
3. Configure:
   - Backend: Python/Dockerfile
   - Frontend: Node.js/Static Site
4. Set environment variables
5. Deploy

### Kubernetes

#### 1. Create Kubernetes manifests

`k8s/backend-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/your-username/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
```

#### 2. Deploy to Kubernetes

```bash
kubectl apply -f k8s/
kubectl get pods
kubectl get services
```

## Post-Deployment

### 1. SSL/TLS Setup

Using Let's Encrypt with Certbot:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 2. Set up Monitoring

#### Health Checks

- Backend: `https://api.yourdomain.com/docs`
- Frontend: `https://yourdomain.com/health`

#### Logging

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Export logs
docker-compose logs > logs.txt
```

### 3. Database Migrations

```bash
# Access backend container
docker exec -it portfolio-backend bash

# Run migrations (if applicable)
alembic upgrade head
```

### 4. Backup Strategy

```bash
# Database backup
docker exec portfolio-db pg_dump -U user portfolio > backup.sql

# Restore
docker exec -i portfolio-db psql -U user portfolio < backup.sql
```

## Performance Optimization

### 1. Enable Caching

Configure Redis in `backend/.env`:
```env
CACHE_TYPE=redis
REDIS_URL=redis://redis:6379/0
```

### 2. CDN for Static Assets

- Use CloudFlare, AWS CloudFront, or similar
- Configure in frontend build

### 3. Database Optimization

- Add indexes for frequently queried fields
- Set up connection pooling
- Use read replicas for scaling

## Security Checklist

- [ ] Use HTTPS/SSL everywhere
- [ ] Set secure CORS origins
- [ ] Use strong SECRET_KEY
- [ ] Keep dependencies updated
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Use environment-specific configs
- [ ] Implement proper logging
- [ ] Regular security audits
- [ ] Backup database regularly

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
```

### Load Balancing

Use Nginx or cloud load balancers:

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

## Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker exec backend env

# Test database connection
docker exec backend python -c "from db.database import init_db; init_db()"
```

#### Frontend can't reach backend
- Verify CORS settings in backend
- Check VITE_API_URL in frontend
- Ensure both services are on same network

#### Database connection errors
- Verify DATABASE_URL format
- Check database service is running
- Ensure credentials are correct

### Getting Help

- Check logs first: `docker-compose logs`
- Review environment configuration
- Verify network connectivity
- Check GitHub Issues for similar problems

## Maintenance

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
curl -f https://yourdomain.com/health
```

### Monitoring

Set up:
- Uptime monitoring (UptimeRobot, Pingdom)
- Error tracking (Sentry)
- Performance monitoring (New Relic, DataDog)
- Log aggregation (ELK Stack, Splunk)

## Cost Optimization

- Use spot instances where possible
- Implement auto-scaling
- Optimize database queries
- Cache frequently accessed data
- Use CDN for static assets
- Monitor and optimize API calls to LLM providers

## Conclusion

This guide covers the essentials of deploying the portfolio. For specific issues or advanced configurations, refer to:

- Docker documentation
- Cloud provider documentation
- FastAPI deployment guide
- Nginx configuration guide
