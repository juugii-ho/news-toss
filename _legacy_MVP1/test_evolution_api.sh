#!/bin/bash

# Topic Evolution API 테스트 스크립트
# Next.js dev 서버가 실행 중이어야 합니다

echo "🧪 Topic Evolution API 테스트"
echo ""
echo "⚠️  먼저 Next.js dev 서버를 재시작하세요:"
echo "   cd app/frontend && npm run dev"
echo ""
read -p "Dev 서버가 실행 중입니까? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Dev 서버를 먼저 시작해주세요"
    exit 1
fi

BASE_URL="http://localhost:3000"

echo ""
echo "1️⃣ /api/topics/evolution 테스트..."
echo "   URL: ${BASE_URL}/api/topics/evolution"
echo ""

RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "${BASE_URL}/api/topics/evolution")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 상태: 200 OK"
    echo ""
    echo "📊 응답 데이터:"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"

    # 토픽 ID 추출 (timeline 테스트용)
    TOPIC_ID=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['topics'][0]['id'] if data.get('topics') else '')" 2>/dev/null)

    if [ -n "$TOPIC_ID" ]; then
        echo ""
        echo "2️⃣ /api/topics/${TOPIC_ID}/timeline 테스트..."
        TIMELINE=$(curl -s "${BASE_URL}/api/topics/${TOPIC_ID}/timeline")
        echo "$TIMELINE" | python3 -m json.tool 2>/dev/null || echo "$TIMELINE"
    fi
else
    echo "❌ 상태: $HTTP_CODE"
    echo ""
    echo "응답:"
    echo "$BODY"
    echo ""
    echo "💡 문제 해결:"
    echo "   1. Next.js dev 서버 재시작 (ctrl+C 후 npm run dev)"
    echo "   2. 파이프라인 실행: python data/pipelines/match_topics_across_days.py"
    echo "   3. Supabase에서 mvp_topic_history 테이블 확인"
fi

echo ""
echo "✅ 테스트 완료"
