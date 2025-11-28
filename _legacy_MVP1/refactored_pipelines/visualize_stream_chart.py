"""
Simplified Stream Chart (단일 날짜용)

현재 데이터: 1일치만 있음
→ 단일 스냅샷으로 "가상의 흐름" 시각화
"""

import os
import json
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment
root_dir = Path(__file__).resolve().parent
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

STREAM_COLORS = {
    'critical': 'rgba(251, 191, 36, 0.65)',
    'neutral': 'rgba(148, 163, 184, 0.5)',
    'supportive': 'rgba(110, 231, 183, 0.65)',
}

def get_stance_category(avg_score):
    if avg_score is None or (34 <= avg_score < 67):
        return 'neutral'
    return 'critical' if avg_score < 34 else 'supportive'

def create_simplified_stream():
    """
    데이터 부족 시 컨셉 시각화
    - 가상의 7일 데이터 생성 (현재 토픽 기반)
    """
    
    print("📅 Fetching current topics...")
    response = supabase.table("mvp_topic_history").select("*").execute()
    topics = response.data
    
    if not topics:
        print("❌ No topic data")
        return
    
    print(f"✅ Found {len(topics)} topics")
    
    # 가상의 7일 날짜
    from datetime import datetime, timedelta
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') 
             for i in range(6, -1, -1)]
    
    fig = go.Figure()
    
    
    # Filter and sort (NoneType handling)
    valid_topics = [t for t in topics if t.get('intensity') is not None]
    sorted_topics = sorted(valid_topics, key=lambda x: x.get('intensity', 0), reverse=True)[:10]

    
    for topic in sorted_topics:
        intensity = topic.get('intensity', 0)
        title_kr = topic.get('title_kr') or topic.get('title_en', 'Unknown')
        avg_stance = topic.get('avg_stance_score')
        stance_cat = get_stance_category(avg_stance)
        color = STREAM_COLORS[stance_cat]
        
        # 가상 라이프사이클 시뮬레이션
        # Day 1-2: 형성 (20% → 50%)
        # Day 3-4: 성장 (50% → 100%)
        # Day 5-6: 유지 (100% → 90%)
        # Day 7: 약화 (90% → 70%)
        lifecycle = np.array([0.2, 0.5, 0.8, 1.0, 0.95, 0.9, 0.7])
        intensities = intensity * lifecycle
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=intensities,
            mode='lines',
            name=title_kr[:18] + '...',
            line=dict(width=0.5, color=color),
            fillcolor=color,
            fill='tonexty',
            stackgroup='one',  # 누적
            hovertemplate=(
                f"<b>{title_kr}</b><br>"
                "날짜: %{x}<br>"
                "영향력: %{y:.0f}<br>"
                f"성향: {stance_cat}<br>"
                "<extra></extra>"
            )
        ))
    
    fig.update_layout(
        title=dict(
            text=(
                "<b style='color:#1f2937; font-size:24px'>🌊 뉴스 흐름 차트 (컨셉)</b><br>"
                "<span style='color:#6b7280; font-size:13px'>토픽이 강물처럼 생성 → 성장 → 소멸하는 과정</span><br>"
                "<span style='color:#ef4444; font-size:11px'>⚠️ 현재 1일 데이터만 있어 가상 라이프사이클로 시각화</span>"
            ),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='날짜 (가상)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
        ),
        yaxis=dict(
            title='영향력 (누적)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
        ),
        hovermode='x unified',
        plot_bgcolor='#fafafa',
        paper_bgcolor='white',
        height=650,
        width=1200,
        showlegend=True,
        legend=dict(
            title="<b>주요 토픽</b>",
            font=dict(size=9),
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#e5e7eb',
            borderwidth=1,
            x=1.01,
            y=1,
            xanchor='left'
        )
    )
    
    fig.add_annotation(
        text=(
            "<b>읽는 법</b><br><br>"
            "• 아래→위로 누적<br>"
            "• 넓어지면 성장<br>"
            "• 좁아지면 약화<br>"
            "• 사라지면 소멸<br><br>"
            "<b>색상</b><br>"
            "<span style='color:#fbbf24'>■</span> 비판적<br>"
            "<span style='color:#94a3b8'>■</span> 중립<br>"
            "<span style='color:#6ee7b7'>■</span> 지지"
        ),
        xref="paper", yref="paper",
        x=1.01, y=0.3,
        xanchor='left', yanchor='middle',
        showarrow=False,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#e5e7eb",
        borderwidth=1,
        borderpad=10,
        font=dict(size=9, color='#374151'),
        align='left'
    )
    
    output_path = root_dir / "stream_chart.html"
    fig.write_html(str(output_path))
    
    print(f"\n✅ Saved: {output_path}")
    print(f"📊 Top {len(sorted_topics)} topics with simulated lifecycle")
    print(f"💡 실제 데이터가 7일 이상 쌓이면 정확한 흐름을 볼 수 있습니다")

if __name__ == "__main__":
    create_simplified_stream()
