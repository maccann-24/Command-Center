#!/bin/bash

echo "🧪 Testing Mission Control API Endpoints"
echo ""

# First, get an agent ID from the database (we'll use Agent Alpha)
AGENT_ID="9b6cd666-8771-46c1-a95d-2ced78c630f9"

echo "1️⃣ Creating a new session..."
SESSION_RESPONSE=$(curl -s -X POST http://localhost:3000/api/sessions \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\": \"$AGENT_ID\", \"status\": \"active\"}")

echo $SESSION_RESPONSE | jq .
SESSION_ID=$(echo $SESSION_RESPONSE | jq -r '.session.id')

echo ""
echo "2️⃣ Logging a user message..."
curl -s -X POST http://localhost:3000/api/messages \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"role\": \"user\", \"content\": \"Hello from API test!\"}" | jq .

echo ""
echo "3️⃣ Logging an assistant message..."
curl -s -X POST http://localhost:3000/api/messages \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"role\": \"assistant\", \"content\": \"Hi! I received your message via API.\"}" | jq .

echo ""
echo "4️⃣ Logging metrics..."
curl -s -X POST http://localhost:3000/api/metrics \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"tokens_input\": 150, \"tokens_output\": 320, \"tokens_total\": 470, \"cost\": 0.002, \"duration_ms\": 1250}" | jq .

echo ""
echo "✅ Test complete! Check your dashboard to see the new data."
