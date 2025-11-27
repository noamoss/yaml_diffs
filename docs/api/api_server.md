# REST API Server Documentation

The yaml-diffs REST API provides HTTP endpoints for validating and diffing Hebrew legal documents in YAML format. The API is built with FastAPI and designed for Railway deployment.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Request/Response Formats](#requestresponse-formats)
- [Error Handling](#error-handling)
- [Environment Variables](#environment-variables)
- [Railway Deployment](#railway-deployment)
- [Examples](#examples)

## Overview

The REST API exposes three main endpoints:

- `POST /api/v1/validate` - Validate a YAML document
- `POST /api/v1/diff` - Compare two YAML documents
- `GET /health` - Health check endpoint

The API automatically generates OpenAPI/Swagger documentation available at `/docs` and ReDoc documentation at `/redoc`.

## Getting Started

### Local Development

1. **Install dependencies** (if not already installed):
   ```bash
   uv sync --extra dev
   ```

2. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

3. **Start the API server**:
   ```bash
   uvicorn src.yaml_diffs.api_server.main:app --reload --port 8000
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health check: http://localhost:8000/health

### Using the API

The API accepts JSON requests and returns JSON responses. All endpoints support CORS for cross-origin requests.

## API Endpoints

### POST /api/v1/validate

Validates a YAML document against the OpenSpec schema and Pydantic models.

**Request Body:**
```json
{
  "yaml": "document:\n  id: \"law-1234\"\n  title: \"חוק הדוגמה\"\n  ..."
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "document": {
    "id": "law-1234",
    "title": "חוק הדוגמה",
    "type": "law",
    "language": "hebrew",
    "version": {
      "number": "2024-01-01"
    },
    "source": {
      "url": "https://example.gov.il/law1234",
      "fetched_at": "2025-01-20T09:50:00Z"
    },
    "sections": []
  },
  "error": null,
  "message": null,
  "details": null
}
```

**Error Response (400 Bad Request - Invalid YAML):**
```json
{
  "error": "YAMLLoadError",
  "message": "YAML parsing error: ...",
  "details": null
}
```

**Error Response (422 Unprocessable Entity - Validation Failed):**
```json
{
  "error": "PydanticValidationError",
  "message": "Validation failed: ...",
  "details": [
    {
      "field": "document.title",
      "message": "Field required",
      "type": "missing",
      "input": {...}
    }
  ]
}
```

### POST /api/v1/diff

Compares two YAML documents and returns detected changes.

**Request Body:**
```json
{
  "old_yaml": "document:\n  id: \"law-1234\"\n  ...",
  "new_yaml": "document:\n  id: \"law-1234\"\n  ..."
}
```

**Response (200 OK):**
```json
{
  "diff": {
    "changes": [
      {
        "section_id": "sec-1",
        "change_type": "content_changed",
        "marker": "1",
        "old_marker_path": ["1"],
        "new_marker_path": ["1"],
        "old_id_path": ["sec-1"],
        "new_id_path": ["sec-1"],
        "old_content": "Original content",
        "new_content": "Updated content",
        "old_title": "Section Title",
        "new_title": "Section Title"
      }
    ],
    "added_count": 1,
    "deleted_count": 0,
    "modified_count": 1,
    "moved_count": 0
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid YAML in either document
- `422 Unprocessable Entity` - Document validation failed
- `500 Internal Server Error` - Unexpected error

### GET /health

Health check endpoint for monitoring and Railway deployment.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### GET /

Root endpoint with API information.

**Response (200 OK):**
```json
{
  "name": "yaml-diffs API",
  "version": "0.1.0",
  "docs": "/docs",
  "redoc": "/redoc",
  "openapi": "/openapi.json",
  "health": "/health"
}
```

## Request/Response Formats

### Request Format

All POST endpoints accept JSON with the following structure:

- **Validate Request:**
  - `yaml` (string, required): YAML document content as string

- **Diff Request:**
  - `old_yaml` (string, required): Old document version YAML content
  - `new_yaml` (string, required): New document version YAML content

### Response Format

All responses are JSON with the following structure:

- **Success Response:**
  - Contains the requested data (document, diff, etc.)
  - Status code: 200

- **Error Response:**
  - `error` (string): Error type/class name
  - `message` (string): Human-readable error message
  - `details` (array, optional): Detailed error information

## Error Handling

The API uses standard HTTP status codes:

- `200 OK` - Request successful
- `400 Bad Request` - Invalid YAML syntax or malformed request
- `422 Unprocessable Entity` - Document validation failed
- `500 Internal Server Error` - Unexpected server error

### Error Types

1. **YAMLLoadError** (400)
   - YAML syntax errors
   - File encoding issues
   - Invalid YAML structure

2. **OpenSpecValidationError** (422)
   - Document doesn't match OpenSpec schema
   - Missing required fields
   - Invalid field values

3. **PydanticValidationError** (422)
   - Document doesn't match Pydantic models
   - Type validation errors
   - Constraint violations

4. **ValueError** (400)
   - Duplicate markers
   - Invalid document structure
   - Business logic errors

## Environment Variables

The API server can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Port to bind the server to (Railway sets this automatically) |
| `HOST` | `0.0.0.0` | Host to bind the server to |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `CORS_ORIGINS` | `""` (empty) | Comma-separated list of allowed CORS origins. Defaults to empty list (no CORS) for security. Set to `*` to allow all origins (insecure for production). |
| `CORS_ALLOW_CREDENTIALS` | `true` | Allow credentials in CORS requests |
| `CORS_ALLOW_METHODS` | `*` | Comma-separated list of allowed HTTP methods |
| `CORS_ALLOW_HEADERS` | `*` | Comma-separated list of allowed headers |
| `APP_NAME` | `yaml-diffs API` | Application name |
| `APP_VERSION` | `0.1.0` | Application version |

### Example .env file

```bash
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
# For local development with frontend (explicitly set - defaults to empty for security)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
# For production (specific domains only)
# CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CORS_ALLOW_CREDENTIALS=true
```

## Railway Deployment

The API is designed for Railway deployment with the following features:

1. **Port Configuration**: Automatically reads `PORT` environment variable (Railway requirement)
2. **Host Binding**: Binds to `0.0.0.0` for Railway networking
3. **Health Check**: Provides `/health` endpoint for Railway monitoring
4. **Production Logging**: Configurable logging for production environment
5. **CORS Support**: Configurable CORS for cross-origin requests

### Quick Setup

1. **Connect Repository**: Connect your GitHub repository to Railway
2. **Configure Environment Variables**: Set any required environment variables in Railway dashboard
3. **Deploy**: Railway will automatically deploy on push to main branch
4. **Monitor**: Use Railway dashboard to monitor health checks and logs

### Configuration Files

The project includes Railway configuration files:

- **`railway.json`**: Railway platform configuration with build and start commands
- **`.env.example`**: Example environment variables file (see [Environment Variables](#environment-variables))

### Railway Start Command

The start command is configured in `railway.json`:

```bash
uvicorn src.yaml_diffs.api_server.main:app --host 0.0.0.0 --port $PORT
```

Railway automatically sets the `PORT` environment variable, which the application reads at startup.

### Health Checks

Railway automatically monitors the `/health` endpoint (configured in `railway.json`). The endpoint returns `200 OK` with a JSON response when the service is healthy:

```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Detailed Deployment Guide

For comprehensive deployment instructions, environment variable configuration, troubleshooting, and production best practices, see the [Railway Deployment Guide](../operations/deployment.md).

## Examples

### Example 1: Validate a Document

```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "yaml": "document:\n  id: \"law-1234\"\n  title: \"חוק הדוגמה\"\n  type: \"law\"\n  language: \"hebrew\"\n  version:\n    number: \"2024-01-01\"\n  source:\n    url: \"https://example.gov.il/law1234\"\n    fetched_at: \"2025-01-20T09:50:00Z\"\n  sections: []"
  }'
```

### Example 2: Diff Two Documents

```bash
curl -X POST http://localhost:8000/api/v1/diff \
  -H "Content-Type: application/json" \
  -d '{
    "old_yaml": "document:\n  id: \"law-1234\"\n  ...",
    "new_yaml": "document:\n  id: \"law-1234\"\n  ..."
  }'
```

### Example 3: Check Health

```bash
curl http://localhost:8000/health
```

### Example 4: Python Client

```python
import requests

# Validate a document
response = requests.post(
    "http://localhost:8000/api/v1/validate",
    json={
        "yaml": """
document:
  id: "law-1234"
  title: "חוק הדוגמה"
  type: "law"
  language: "hebrew"
  version:
    number: "2024-01-01"
  source:
    url: "https://example.gov.il/law1234"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []
"""
    }
)

if response.status_code == 200:
    data = response.json()
    if data["valid"]:
        print(f"Document is valid: {data['document']['title']}")
    else:
        print(f"Validation failed: {data['message']}")
else:
    print(f"Error: {response.status_code} - {response.json()}")
```

### Example 5: JavaScript/TypeScript Client

```typescript
// Validate a document
const response = await fetch('http://localhost:8000/api/v1/validate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    yaml: `document:
  id: "law-1234"
  title: "חוק הדוגמה"
  type: "law"
  language: "hebrew"
  version:
    number: "2024-01-01"
  source:
    url: "https://example.gov.il/law1234"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []`
  }),
});

const data = await response.json();
if (data.valid) {
  console.log(`Document is valid: ${data.document.title}`);
} else {
  console.error(`Validation failed: ${data.message}`);
}
```

## OpenAPI Documentation

The API automatically generates OpenAPI 3.0 specification available at:

- **Swagger UI**: `/docs` - Interactive API documentation
- **ReDoc**: `/redoc` - Alternative documentation interface
- **OpenAPI JSON**: `/openapi.json` - Machine-readable API specification

## Security Considerations

1. **CORS Configuration**: Configure `CORS_ORIGINS` appropriately for production
2. **Input Validation**: All inputs are validated against schemas
3. **Error Messages**: Error messages don't expose sensitive information
4. **Rate Limiting**: Consider adding rate limiting for production use
5. **Authentication**: Consider adding authentication/authorization for production APIs

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Change the `PORT` environment variable
   - Or stop the process using the port

2. **CORS Errors**
   - Configure `CORS_ORIGINS` environment variable
   - Ensure your frontend origin is in the allowed list

3. **Validation Errors**
   - Check the error `details` field for specific field errors
   - Verify YAML syntax is correct
   - Ensure all required fields are present

4. **Railway Deployment Issues**
   - Verify `PORT` environment variable is set
   - Check Railway logs for errors
   - Ensure health check endpoint returns 200 OK

## Related Documentation

- [API Reference](../developer/api_reference.md) - Library API documentation
- [AGENTS.md](../../AGENTS.md) - Development guide for AI agents
- [README.md](../../README.md) - Project overview and setup
- [Getting Started](../user/getting_started.md) - Quick start guide
