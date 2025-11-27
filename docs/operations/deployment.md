# Railway Deployment Guide

This guide provides step-by-step instructions for deploying the yaml-diffs REST API service to Railway.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Deployment](#initial-deployment)
- [Environment Configuration](#environment-configuration)
- [Health Checks](#health-checks)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)
- [Production Best Practices](#production-best-practices)

## Prerequisites

Before deploying to Railway, ensure you have:

1. **Railway Account**: Sign up at [railway.app](https://railway.app) if you don't have an account
2. **GitHub Repository**: Your code must be in a GitHub repository
3. **Railway CLI** (Optional): Install for local testing and management
   ```bash
   npm install -g @railway/cli
   # Or using Homebrew (macOS)
   brew install railway
   ```

## Initial Deployment

### Step 1: Connect Repository to Railway

1. Log in to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account (if not already done)
5. Select the `yaml_diffs` repository
6. Railway will automatically detect it as a Python project

### Step 2: Configure Environment Variables

1. In your Railway project, go to the **Variables** tab
2. Add the following environment variables as needed:

   **Required for Production:**
   - `CORS_ORIGINS`: Set to your production domain(s), e.g., `https://yourdomain.com,https://app.yourdomain.com`
   - `LOG_LEVEL`: Set to `INFO` or `WARNING` for production

   **Optional (have defaults):**
   - `HOST`: Defaults to `0.0.0.0` (required for Railway, do not change)
   - `CORS_ALLOW_CREDENTIALS`: Defaults to `true`
   - `CORS_ALLOW_METHODS`: Defaults to `*`
   - `CORS_ALLOW_HEADERS`: Defaults to `*`
   - `APP_NAME`: Defaults to `yaml-diffs API`
   - `APP_VERSION`: Defaults to `0.1.0`

   **Note**: Railway automatically sets `PORT` - do not override it.

3. See [Environment Configuration](#environment-configuration) for detailed variable descriptions

### Step 3: Deploy

Railway will automatically:
1. Detect the Python project from `pyproject.toml`
2. Install the package using the build configuration from `railway.json`
3. Run the start command: `uvicorn yaml_diffs.api_server.main:app --host 0.0.0.0 --port $PORT`
   - Note: Uses the installed package name `yaml_diffs` (not `src.yaml_diffs`) since Railway installs the package
4. Monitor the `/health` endpoint for health checks

### Step 4: Verify Deployment

1. Wait for the deployment to complete (check the **Deployments** tab)
2. Railway will provide a public URL (e.g., `https://yaml-diffs.up.railway.app`)
3. Test the health endpoint:
   ```bash
   curl https://yaml-diffs.up.railway.app/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "version": "0.1.0"
   }
   ```
4. Test the API endpoints:
   ```bash
   # Validate endpoint
   curl -X POST https://yaml-diffs.up.railway.app/api/v1/validate \
     -H "Content-Type: application/json" \
     -d '{"yaml": "document:\n  id: \"test\"\n  title: \"Test\"\n  type: \"law\"\n  language: \"hebrew\"\n  version:\n    number: \"2024-01-01\"\n  source:\n    url: \"https://example.com\"\n    fetched_at: \"2024-01-01T00:00:00Z\"\n  sections: []"}'
   ```

**Production API URL**: The deployed API is available at **https://yaml-diffs.up.railway.app**

You can also use the verification script:
```bash
# Using the production URL from .env.example
./scripts/verify_railway_deployment.sh

# Or specify the URL directly
./scripts/verify_railway_deployment.sh https://yaml-diffs.up.railway.app
```

## Environment Configuration

### Local Development

For local development, use a `.env` file based on `.env.example`:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your local settings
# The .env.example includes the production API URL (https://yaml-diffs.up.railway.app)
# by default for API client scripts
```

**Note**: The `.env` file is for local development only. Railway deployments use environment variables set in the Railway dashboard.

### Required Variables

**None** - The API will run with defaults, but production deployments should configure:

- `CORS_ORIGINS`: **Required for production** - Set to your frontend domain(s)

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | **Railway sets this automatically** - Do not override |
| `HOST` | `0.0.0.0` | Host to bind to (required for Railway, do not change) |
| `LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `CORS_ORIGINS` | `""` (empty) | Comma-separated list of allowed origins. Empty = no CORS (most secure) |
| `CORS_ALLOW_CREDENTIALS` | `true` | Allow credentials in CORS requests |
| `CORS_ALLOW_METHODS` | `*` | Comma-separated list of allowed HTTP methods |
| `CORS_ALLOW_HEADERS` | `*` | Comma-separated list of allowed headers |
| `APP_NAME` | `yaml-diffs API` | Application name |
| `APP_VERSION` | `0.1.0` | Application version |

### Production Security Settings

For production deployments, configure:

```bash
# Production CORS (specific domains only)
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Production logging (less verbose)
LOG_LEVEL=INFO

# Optional: Restrict CORS methods and headers
CORS_ALLOW_METHODS=GET,POST,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Authorization
```

**Security Warning**: Never set `CORS_ORIGINS=*` in production - this allows any website to make requests to your API.

### Railway-Set Variables

Railway automatically sets these variables (do not override):

- `PORT`: Port number for the service
- `RAILWAY_ENVIRONMENT`: `production` or `development`
- `RAILWAY_PROJECT_ID`: Project identifier
- `RAILWAY_SERVICE_ID`: Service identifier

## Health Checks

### Configuration

The health check is configured in `railway.json`:

```json
{
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30
  }
}
```

**Note:** The health check timeout is set to 30 seconds, which is sufficient for most applications. Railway will consider the service unhealthy if the health endpoint doesn't respond within this time. If your service requires a longer startup time, you can increase this value, but 30 seconds is recommended for most FastAPI applications.

### Health Endpoint

The `/health` endpoint returns:

```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

**Status Codes:**
- `200 OK`: Service is healthy
- `500 Internal Server Error`: Service is unhealthy (Railway will restart)

### Monitoring

Railway automatically:
1. Monitors the `/health` endpoint
2. Restarts the service if health checks fail
3. Shows health status in the dashboard

### Troubleshooting Health Checks

If health checks are failing:

1. **Check Logs**: View logs in Railway dashboard to see errors
2. **Verify Endpoint**: Test `/health` endpoint manually:
   ```bash
   curl https://yaml-diffs.up.railway.app/health
   ```
3. **Check Port Binding**: Ensure the service binds to `0.0.0.0` and uses `$PORT`
4. **Check Startup Time**: Increase `healthcheckTimeout` if service takes longer to start

## CI/CD Integration

### Automatic Deployments

Railway automatically deploys when you push to your connected branch (typically `main`):

1. Push code to GitHub
2. Railway detects the push
3. Builds and deploys automatically
4. Updates the service URL (if using a custom domain)

### Branch-Based Deployments

To deploy different branches:

1. In Railway dashboard, go to **Settings** → **Source**
2. Change the **Branch** to your desired branch
3. Railway will deploy from that branch

### Environment Promotion

For staging → production workflows:

1. Create separate Railway projects for staging and production
2. Connect staging to a `staging` branch
3. Connect production to `main` branch
4. Test in staging, then merge to `main` for production

### GitHub Actions Integration (Optional)

You can trigger Railway deployments from GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: bervProject/railway-deploy@v1.0.0
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: your-service-name
```

**Note**: Railway's automatic Git integration is usually sufficient and recommended.

## Troubleshooting

### Common Issues

#### 1. Port Binding Errors

**Error**: `Address already in use` or service won't start

**Solution**:
- Ensure you're using `$PORT` (not a hardcoded port)
- Verify `HOST=0.0.0.0` (required for Railway)
- Check that no other process is using the port

#### 2. Health Check Failures

**Error**: Health checks timing out or failing

**Solutions**:
- Check service logs for startup errors
- Verify `/health` endpoint is accessible
- Increase `healthcheckTimeout` in `railway.json` if startup is slow
- Ensure service binds to `0.0.0.0` (not `127.0.0.1`)

#### 3. CORS Errors

**Error**: CORS policy blocking requests from frontend

**Solution**:
- Set `CORS_ORIGINS` to include your frontend domain
- Verify domain format: `https://yourdomain.com` (include protocol)
- Check that `CORS_ALLOW_CREDENTIALS=true` if using credentials

#### 4. Build Failures

**Error**: Build fails during deployment

**Solutions**:
- Check build logs in Railway dashboard
- Verify `pyproject.toml` is valid
- Ensure all dependencies are listed in `pyproject.toml`
- Check Python version compatibility (requires Python 3.10+)

#### 5. Environment Variable Issues

**Error**: Service not reading environment variables correctly

**Solutions**:
- Verify variables are set in Railway dashboard (Variables tab)
- Check variable names match exactly (case-sensitive)
- Restart the service after changing variables
- Check logs to see what values are being used

### Accessing Logs

1. **Railway Dashboard**:
   - Go to your project → Service → **Logs** tab
   - View real-time logs and filter by level

2. **Railway CLI**:
   ```bash
   railway logs
   ```

3. **Log Levels**:
   - Set `LOG_LEVEL=DEBUG` for detailed logs (development only)
   - Use `LOG_LEVEL=INFO` for production

### Debugging Tips

1. **Test Locally with Railway Environment**:
   ```bash
   # For local testing (from project root, package not installed)
   PORT=8000 uvicorn src.yaml_diffs.api_server.main:app --host 0.0.0.0 --port $PORT

   # For production-like testing (with package installed)
   PORT=8000 uvicorn yaml_diffs.api_server.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Check Service Status**:
   - Railway dashboard shows service status
   - Green = healthy, Red = unhealthy

3. **Verify Configuration**:
   - Check `railway.json` syntax is valid JSON
   - Verify start command matches your application structure
   - Ensure health check path is correct

## Production Best Practices

### Security

1. **CORS Configuration**:
   - Never use `CORS_ORIGINS=*` in production
   - Specify exact domains: `https://yourdomain.com`
   - Use HTTPS for all production domains

2. **Environment Variables**:
   - Never commit `.env` files to git
   - Use Railway's secure variable storage
   - Rotate secrets regularly

3. **Logging**:
   - Use `LOG_LEVEL=INFO` or `WARNING` in production
   - Avoid logging sensitive information
   - Monitor logs for security issues

### Performance

1. **Resource Allocation**:
   - Monitor resource usage in Railway dashboard
   - Scale up if needed (Railway auto-scales, but you can set limits)

2. **Caching**:
   - Consider adding response caching for frequently accessed endpoints
   - Use Railway's CDN for static assets (if applicable)

3. **Database Connections** (if added later):
   - Use connection pooling
   - Monitor connection limits

### Monitoring

1. **Health Checks**:
   - Monitor health check status in Railway dashboard
   - Set up alerts for health check failures

2. **Logs**:
   - Regularly review logs for errors
   - Set up log aggregation if needed

3. **Metrics**:
   - Monitor request rates and response times
   - Track error rates and types

### Backup and Recovery

1. **Code**:
   - All code is in Git (backed up automatically)
   - Tag releases for easy rollback

2. **Configuration**:
   - Document all environment variables
   - Keep `.env.example` up to date

3. **Rollback**:
   - Railway keeps deployment history
   - You can rollback to previous deployments from the dashboard

## Related Documentation

- [API Server Documentation](../api/api_server.md) - Complete API reference
- [CI/CD Documentation](ci_cd.md) - GitHub Actions workflows
- [README.md](../../README.md) - Project overview
- [Railway Documentation](https://docs.railway.app) - Official Railway docs

## Getting Help

If you encounter issues not covered in this guide:

1. Check [Railway Documentation](https://docs.railway.app)
2. Review service logs in Railway dashboard
3. Test locally with Railway environment variables
4. Open an issue on [GitHub](https://github.com/noamoss/yaml_diffs/issues)
