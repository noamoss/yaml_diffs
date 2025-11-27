#!/bin/bash
# Verification script for Railway deployment
# Usage: ./scripts/verify_railway_deployment.sh [BASE_URL]
# Example: ./scripts/verify_railway_deployment.sh https://yaml-diffs.up.railway.app
# Or for internal: ./scripts/verify_railway_deployment.sh http://yaml_diffs.railway.internal

# Source .env file if it exists (for local development)
# This allows the script to use YAML_DIFFS_API_URL from .env as default
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -f "$PROJECT_ROOT/.env" ]; then
    # Export variables from .env file
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Get BASE_URL from command-line argument, environment variable, or error
BASE_URL="${1:-}"

# If no command-line argument, try to use YAML_DIFFS_API_URL from environment
if [ -z "$BASE_URL" ]; then
    if [ -n "$YAML_DIFFS_API_URL" ]; then
        BASE_URL="$YAML_DIFFS_API_URL"
        echo "Using API URL from environment: $BASE_URL"
        echo ""
    else
        echo "Error: No URL provided"
        echo ""
        echo "Usage: $0 [BASE_URL]"
        echo ""
        echo "Arguments:"
        echo "  BASE_URL   Optional. Base URL of the Railway deployment."
        echo "             If not provided, uses YAML_DIFFS_API_URL from .env file"
        echo "             or environment variable"
        echo ""
        echo "Examples:"
        echo "  $0"
        echo "    (uses YAML_DIFFS_API_URL from .env or environment)"
        echo "  $0 https://yaml-diffs.up.railway.app"
        echo "    (uses provided URL)"
        echo "  $0 http://yaml_diffs.railway.internal  # Internal Railway URL"
        echo "  $0 your-app.up.railway.app              # Protocol will be auto-detected (HTTPS for Railway)"
        echo ""
        echo "Environment Variables:"
        echo "  YAML_DIFFS_API_URL  Base URL of the API (can be set in .env file)"
        echo ""
        echo "To get your Railway public URL:"
        echo "  1. Go to Railway dashboard → Your service → Settings → Domains"
        echo "  2. Or check the service URL in Railway dashboard"
        echo ""
        echo "Note: Create a .env file from .env.example to configure the API URL."
        echo ""
        exit 1
    fi
fi

# Auto-detect protocol if not provided
if [[ ! "$BASE_URL" =~ ^https?:// ]]; then
    # If it's a Railway domain, default to HTTPS
    if [[ "$BASE_URL" =~ \.railway\.(app|internal)$ ]] || [[ "$BASE_URL" =~ railway\.internal$ ]]; then
        if [[ "$BASE_URL" =~ railway\.internal$ ]]; then
            BASE_URL="http://$BASE_URL"
        else
            BASE_URL="https://$BASE_URL"
        fi
    else
        # For other domains, default to HTTPS
        BASE_URL="https://$BASE_URL"
    fi
    echo "Auto-detected protocol: $BASE_URL"
fi

echo "Verifying Railway deployment at: $BASE_URL"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check Endpoint (/health)..."
HEALTH_RESPONSE=$(curl -s -L -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL/health")
HTTP_STATUS=$(echo "$HEALTH_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Health check passed (HTTP $HTTP_STATUS)"
    echo "Response: $HEALTH_BODY"
else
    echo "❌ Health check failed (HTTP $HTTP_STATUS)"
    echo "Response: $HEALTH_BODY"
    exit 1
fi
echo ""

# Test 2: Root Endpoint
echo "2. Testing Root Endpoint (/)..."
ROOT_RESPONSE=$(curl -s -L -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL/")
HTTP_STATUS=$(echo "$ROOT_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
ROOT_BODY=$(echo "$ROOT_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Root endpoint passed (HTTP $HTTP_STATUS)"
    echo "Response: $ROOT_BODY"
else
    echo "❌ Root endpoint failed (HTTP $HTTP_STATUS)"
    echo "Response: $ROOT_BODY"
    exit 1
fi
echo ""

# Test 3: OpenAPI Documentation
echo "3. Testing OpenAPI Documentation (/openapi.json)..."
OPENAPI_RESPONSE=$(curl -s -L -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL/openapi.json")
HTTP_STATUS=$(echo "$OPENAPI_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ OpenAPI documentation accessible (HTTP $HTTP_STATUS)"
else
    echo "❌ OpenAPI documentation failed (HTTP $HTTP_STATUS)"
    exit 1
fi
echo ""

# Test 4: Validate Endpoint
echo "4. Testing Validate Endpoint (/api/v1/validate)..."
MINIMAL_YAML='document:
  id: "test-123"
  title: "חוק בדיקה"
  type: "law"
  language: "hebrew"
  version:
    number: "2024-01-01"
  source:
    url: "https://example.com/test"
    fetched_at: "2025-01-20T09:50:00Z"
  sections: []'

VALIDATE_RESPONSE=$(curl -s -L -w "\nHTTP_STATUS:%{http_code}" \
    -X POST "$BASE_URL/api/v1/validate" \
    -H "Content-Type: application/json" \
    -d "{\"yaml\": $(echo "$MINIMAL_YAML" | jq -Rs .)}")
HTTP_STATUS=$(echo "$VALIDATE_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
VALIDATE_BODY=$(echo "$VALIDATE_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Validate endpoint passed (HTTP $HTTP_STATUS)"
    VALID=$(echo "$VALIDATE_BODY" | jq -r '.valid // false')
    if [ "$VALID" = "true" ]; then
        echo "✅ Document validation successful"
    else
        echo "⚠️  Document validation returned valid=false"
        echo "Response: $VALIDATE_BODY"
    fi
else
    echo "❌ Validate endpoint failed (HTTP $HTTP_STATUS)"
    echo "Response: $VALIDATE_BODY"
    exit 1
fi
echo ""

# Test 5: Swagger UI
echo "5. Testing Swagger UI (/docs)..."
DOCS_RESPONSE=$(curl -s -L -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL/docs")
HTTP_STATUS=$(echo "$DOCS_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Swagger UI accessible (HTTP $HTTP_STATUS)"
else
    echo "⚠️  Swagger UI not accessible (HTTP $HTTP_STATUS) - may require browser"
fi
echo ""

echo "=========================================="
echo "✅ All critical endpoints verified!"
echo "=========================================="
echo ""
echo "Deployment is working correctly. You can access:"
echo "  - API: $BASE_URL"
echo "  - Health: $BASE_URL/health"
echo "  - Swagger UI: $BASE_URL/docs"
echo "  - ReDoc: $BASE_URL/redoc"
echo "  - OpenAPI: $BASE_URL/openapi.json"
