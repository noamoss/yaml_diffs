#!/bin/bash
# Verification script for Railway deployment
# Usage: ./scripts/verify_railway_deployment.sh [BASE_URL]
# Example: ./scripts/verify_railway_deployment.sh https://yaml-diffs-production.up.railway.app
# Or for internal: ./scripts/verify_railway_deployment.sh http://yaml_diffs.railway.internal

BASE_URL="${1:-}"
if [ -z "$BASE_URL" ]; then
    echo "Error: No URL provided"
    echo ""
    echo "Usage: $0 <BASE_URL>"
    echo ""
    echo "Examples:"
    echo "  $0 http://yaml_diffs.railway.internal  # Internal Railway URL (from Railway environment)"
    echo "  $0 https://your-app.up.railway.app      # Public Railway URL"
    echo ""
    echo "To get your Railway public URL:"
    echo "  1. Go to Railway dashboard → Your service → Settings → Domains"
    echo "  2. Or check the service URL in Railway dashboard"
    echo ""
    exit 1
fi

echo "Verifying Railway deployment at: $BASE_URL"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check Endpoint (/health)..."
HEALTH_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL/health")
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
ROOT_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL/")
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
OPENAPI_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL/openapi.json")
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

VALIDATE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
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
DOCS_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL/docs")
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
