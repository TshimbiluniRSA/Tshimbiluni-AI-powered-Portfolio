# GitHub Secrets Setup Guide

This guide explains how to securely store API keys and tokens as GitHub Secrets for use in your repository.

## Overview

**Important:** Never commit API keys, tokens, or other sensitive information directly to your repository. Always use environment variables and GitHub Secrets to keep your credentials secure.

## Required Secrets

This application requires the following secrets to be configured:

> **⚠️ IMPORTANT**: The API keys provided in the issue have been documented. For security:
> - These keys have been added to this repository's GitHub Secrets
> - They are NOT committed to the source code
> - Local developers should add them to their local `.env` file
> - Consider rotating these keys periodically for enhanced security

### 1. GEMINI_API_KEY
- **Purpose:** API key for Google Gemini AI model
- **Provider:** Google AI Studio / Google Cloud
- **Free Tier:** Available with usage limits
- **How to obtain:**
  1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
  2. Sign in with your Google account
  3. Click "Create API Key"
  4. Copy the generated API key

### 2. GITHUB_TOKEN
- **Purpose:** Personal Access Token for GitHub API access
- **Provider:** GitHub
- **How to obtain:**
  1. Go to [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
  2. Click "Generate new token (classic)"
  3. Give it a descriptive name (e.g., "Portfolio App Access")
  4. Select the following scopes:
     - `repo` (Full control of private repositories) - if you need private repo access
     - `read:user` (Read user profile data)
     - `user:email` (Access user email addresses)
  5. Click "Generate token"
  6. Copy the token immediately (you won't be able to see it again)

## Setting Up GitHub Secrets

### For Repository Secrets (Recommended for Deployment)

1. **Navigate to your repository on GitHub**
2. **Go to Settings > Secrets and variables > Actions**
3. **Click "New repository secret"**
4. **Add each secret:**

   **GEMINI_API_KEY:**
   - Name: `GEMINI_API_KEY`
   - Secret: `[paste your Gemini API key here]`
   - Click "Add secret"

   **GITHUB_TOKEN:**
   - Name: `GITHUB_TOKEN`
   - Secret: `[paste your GitHub Personal Access Token here]`
   - Click "Add secret"

### For Local Development

1. **Copy the example environment file:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit the `.env` file:**
   ```bash
   nano .env  # or use your preferred text editor
   ```

3. **Add your API keys:**
   ```env
   # Google Gemini Configuration
   GEMINI_API_KEY=AIzaSy...your_actual_key_here

   # GitHub API Configuration
   GITHUB_TOKEN=ghp_...your_actual_token_here
   ```

4. **Save and close the file**

5. **Verify `.env` is in `.gitignore`** (it should already be there):
   ```bash
   # Check if .env is ignored
   git check-ignore .env
   # Should output: .env
   ```

## Using Secrets in GitHub Actions

If you need to use these secrets in GitHub Actions workflows, reference them like this:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy with secrets
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Your deployment commands here
          echo "Deploying with secrets configured"
```

## Using Secrets in Docker

### Docker Compose with .env file

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    env_file:
      - ./backend/.env
    # Or explicitly pass environment variables
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
```

### Docker Run

```bash
docker run -d \
  -e GEMINI_API_KEY=${GEMINI_API_KEY} \
  -e GITHUB_TOKEN=${GITHUB_TOKEN} \
  your-image-name
```

## Security Best Practices

### ✅ DO:
- Use GitHub Secrets for production deployments
- Use `.env` files for local development (and ensure they're in `.gitignore`)
- Rotate your API keys periodically
- Use the minimum required permissions for tokens
- Store secrets in a secure password manager
- Review and revoke unused tokens regularly

### ❌ DON'T:
- Never commit `.env` files to git
- Never hardcode API keys in source code
- Never share API keys in issues, pull requests, or comments
- Never commit secrets to public repositories
- Don't use the same API key across multiple environments

## Verifying Your Setup

### Local Development

Test that your environment variables are loaded correctly:

```bash
cd backend

# Check if environment variables are set (without revealing values)
python -c "import os; print('GEMINI_API_KEY:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
python -c "import os; print('GITHUB_TOKEN:', 'SET' if os.getenv('GITHUB_TOKEN') else 'NOT SET')"
```

### In Docker

```bash
docker-compose exec backend env | grep -E "GEMINI|GITHUB"
```

## Troubleshooting

### "API key not configured" errors

1. **Check if the secret is set:**
   - For local: Verify `.env` file exists and contains the key
   - For GitHub Actions: Check Settings > Secrets and variables > Actions

2. **Verify the environment variable name:**
   - Must be exactly `GEMINI_API_KEY` (not `GEMINI_KEY` or `GOOGLE_API_KEY`)
   - Must be exactly `GITHUB_TOKEN` (not `GITHUB_API_TOKEN` or `GH_TOKEN`)

3. **Check for extra spaces:**
   - Ensure no spaces around the `=` sign in `.env` files
   - Ensure no trailing spaces after the value

4. **Restart your application:**
   - Environment variables are loaded at startup
   - After changing `.env`, restart the backend server

### Rate Limiting Issues

If you're hitting rate limits:
- **Gemini:** Free tier has daily quotas. Consider upgrading or implementing caching
- **GitHub:** Authenticated requests have higher rate limits (5000/hour vs 60/hour)
- Check current limits: https://api.github.com/rate_limit

## Additional Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Google AI Studio](https://makersuite.google.com/)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Best Practices for Using Secrets](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

## Emergency: If Your Secrets Are Exposed

If you accidentally commit a secret to your repository:

1. **Immediately revoke the exposed key/token:**
   - Gemini: Regenerate at Google AI Studio
   - GitHub: Revoke at GitHub Settings > Developer Settings > Personal Access Tokens

2. **Remove from git history:**
   ```bash
   # Consider using tools like BFG Repo-Cleaner or git-filter-repo
   # Or contact GitHub support for private repos
   ```

3. **Generate new keys/tokens and update your secrets**

4. **Review your git history to ensure no other secrets are exposed**

5. **Consider enabling secret scanning:**
   - GitHub provides automatic secret scanning for public repositories
   - Enable it for private repos in Settings > Security > Code security and analysis

## Support

For additional help:
- Review the main [README.md](README.md)
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment-specific setup
- Open an issue if you encounter problems
