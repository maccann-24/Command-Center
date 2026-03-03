#!/bin/bash
# Test script for BASED MONEY API

echo "Testing BASED MONEY API..."
echo ""

# Test root endpoint
echo "1. Testing root endpoint (GET /):"
curl -s http://localhost:8000/ | python3 -m json.tool
echo ""

# Test health endpoint
echo "2. Testing health endpoint (GET /health):"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# Test status endpoint
echo "3. Testing status endpoint (GET /api/based-money/status):"
curl -s http://localhost:8000/api/based-money/status | python3 -m json.tool
echo ""

# Test portfolio endpoint
echo "4. Testing portfolio endpoint (GET /api/based-money/portfolio):"
curl -s http://localhost:8000/api/based-money/portfolio | python3 -m json.tool
echo ""

# Test theses endpoint
echo "5. Testing theses endpoint (GET /api/based-money/theses):"
curl -s http://localhost:8000/api/based-money/theses | python3 -m json.tool
echo ""

# Test positions endpoint
echo "6. Testing positions endpoint (GET /api/based-money/positions):"
curl -s http://localhost:8000/api/based-money/positions | python3 -m json.tool
echo ""

echo "✅ All tests complete!"
