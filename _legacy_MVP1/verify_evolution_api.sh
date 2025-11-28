#!/bin/bash

# Verification script for Topic Evolution API endpoints
# Run this after match_topics_across_days.py has populated mvp_topic_history

echo "🧪 Testing Topic Evolution API Endpoints..."
echo ""

# Base URL (change to production URL when deployed)
BASE_URL="http://localhost:3000"

echo "1️⃣ Testing /api/topics/evolution..."
EVOLUTION_RESPONSE=$(curl -s "${BASE_URL}/api/topics/evolution")
echo "Response:"
echo "$EVOLUTION_RESPONSE" | jq '.'
echo ""

# Extract a topic_id from the response for timeline test
TOPIC_ID=$(echo "$EVOLUTION_RESPONSE" | jq -r '.topics[0].id // empty')

if [ -z "$TOPIC_ID" ]; then
    echo "⚠️  No topics found in evolution response. Skipping timeline test."
    echo "   Run match_topics_across_days.py first to populate history."
else
    echo "2️⃣ Testing /api/topics/${TOPIC_ID}/timeline..."
    TIMELINE_RESPONSE=$(curl -s "${BASE_URL}/api/topics/${TOPIC_ID}/timeline")
    echo "Response:"
    echo "$TIMELINE_RESPONSE" | jq '.'
    echo ""

    # Validate response structure
    echo "3️⃣ Validating response structure..."

    # Check evolution endpoint has required fields
    HAS_SUMMARY=$(echo "$EVOLUTION_RESPONSE" | jq 'has("summary")')
    HAS_TOPICS=$(echo "$EVOLUTION_RESPONSE" | jq 'has("topics")')

    # Check timeline endpoint has required fields
    HAS_TIMELINE=$(echo "$TIMELINE_RESPONSE" | jq 'has("timeline")')
    HAS_INSIGHTS=$(echo "$TIMELINE_RESPONSE" | jq 'has("insights")')

    if [ "$HAS_SUMMARY" = "true" ] && [ "$HAS_TOPICS" = "true" ]; then
        echo "✅ /api/topics/evolution structure valid"
    else
        echo "❌ /api/topics/evolution structure invalid"
    fi

    if [ "$HAS_TIMELINE" = "true" ] && [ "$HAS_INSIGHTS" = "true" ]; then
        echo "✅ /api/topics/[id]/timeline structure valid"
    else
        echo "❌ /api/topics/[id]/timeline structure invalid"
    fi
fi

echo ""
echo "📊 Summary Statistics (if available):"
echo "$EVOLUTION_RESPONSE" | jq '.summary // "No summary available"'

echo ""
echo "✅ Verification complete!"
echo ""
echo "Next steps:"
echo "  1. If no data: Run 'python data/pipelines/match_topics_across_days.py'"
echo "  2. Check frontend integration in /app/topics/[id] page"
echo "  3. Test with different dates: ${BASE_URL}/api/topics/evolution?date=2025-11-26"
