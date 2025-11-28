#!/bin/bash

# 양방향 시각화 프로토타입 실행 스크립트
# Constellation Map + Stream Chart

echo "🚀 News Spectrum 시각화 프로토타입 생성"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 환경 확인
if [ ! -f ".env.local" ]; then
    echo "⚠️  Warning: .env.local not found"
    echo "   Make sure Supabase credentials are set"
fi

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python first."
    exit 1
fi

echo "📊 Step 1: Constellation Map (별자리 지도)"
echo "   - 다크모드 + 애니메이션"
echo "   - 시간에 따라 토픽이 별처럼 생성/소멸"
echo ""
python3 visualize_constellation_timeline.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📊 Step 2: Stream Chart (흐름 차트)"
echo "   - 토픽을 강물처럼 표현"
echo "   - 생성 → 성장 → 소멸 과정 시각화"
echo ""
python3 visualize_stream_chart.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ 완료!"
echo ""
echo "📁 생성된 파일:"
echo "   1. constellation_timeline.html (별자리 지도)"
echo "   2. stream_chart.html (흐름 차트)"
echo ""
echo "💡 브라우저에서 열어서 양쪽을 비교해보세요!"
echo ""
echo "🤔 피드백:"
echo "   - 어느 쪽이 더 직관적인가요?"
echo "   - 프로덕트 톤과 잘 맞나요?"
echo "   - 추가하고 싶은 기능이 있나요?"
