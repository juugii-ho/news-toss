"""
News Spectrum 브랜드 토픽 맵
- 사이트 디자인 시스템과 일치 (zinc 팔레트, emerald 액센트)
- 크기 = 영향력, 색상 = 성향 강도
- 깔끔한 타이포그래피, 다크모드 지원
"""

import os
import json
import numpy as np
import plotly.graph_objects as go
from sklearn.manifold import TSNE
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment
root_dir = Path(__file__).resolve().parent
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# News Spectrum Brand Colors (zinc palette + emerald accent)
BRAND_COLORS = {
    # 성향 색상 (더 선명하고 구분 가능하게)
    'critical': '#ef4444',      # red-500 (비판적)
    'neutral': '#71717a',       # zinc-500 (중립)
    'supportive': '#10b981',    # emerald-500 (지지)

    # 강도별 투명도
    'high_opacity': 0.85,
    'medium_opacity': 0.65,
    'low_opacity': 0.45,
}

# 영향력 등급 (태풍 카테고리)
INTENSITY_EMOJI = {
    1: '🌱',  # 약함
    2: '🌿',  # 보통
    3: '🌀',  # 강함
    4: '🌪️',  # 매우 강함
    5: '⚡️'   # 극강
}

def get_stance_info(avg_score):
    """성향 카테고리와 색상 반환"""
    if avg_score is None:
        return 'neutral', BRAND_COLORS['neutral'], '중립', BRAND_COLORS['medium_opacity']

    # 성향 강도 계산 (중앙 50에서 얼마나 떨어져 있는지)
    deviation = abs(avg_score - 50)

    if avg_score < 34:
        opacity = BRAND_COLORS['high_opacity'] if deviation > 30 else BRAND_COLORS['medium_opacity']
        return 'critical', BRAND_COLORS['critical'], '비판적', opacity
    elif avg_score < 67:
        return 'neutral', BRAND_COLORS['neutral'], '중립', BRAND_COLORS['low_opacity']
    else:
        opacity = BRAND_COLORS['high_opacity'] if deviation > 30 else BRAND_COLORS['medium_opacity']
        return 'supportive', BRAND_COLORS['supportive'], '지지', opacity

def calculate_category(intensity):
    """영향력 등급 (1-5)"""
    if intensity < 20: return 1
    if intensity < 50: return 2
    if intensity < 100: return 3
    if intensity < 150: return 4
    return 5

def visualize_branded_map():
    """News Spectrum 브랜드 토픽 맵"""

    print("📊 토픽 데이터 가져오는 중...")

    # 토픽 가져오기
    topics_response = supabase.table("mvp_topics")\
        .select("*")\
        .not_.is_("centroid_embedding", "null")\
        .order("country_count", desc=True)\
        .limit(100)\
        .execute()

    topics = topics_response.data

    if not topics:
        print("❌ 임베딩이 있는 토픽을 찾을 수 없습니다")
        return

    print(f"✅ {len(topics)}개 토픽 발견")

    # 기사 수 계산
    print("📰 기사 수 계산 중...")
    articles_response = supabase.table("mvp_articles").select("topic_id").execute()
    article_counts = {}
    if articles_response.data:
        from collections import Counter
        counts = Counter([a['topic_id'] for a in articles_response.data if a.get('topic_id')])
        article_counts = dict(counts)

    for t in topics:
        t['article_count'] = article_counts.get(t['id'], 0)

    # 임베딩 추출 및 차원 축소
    embeddings = []
    valid_topics = []

    for topic in topics:
        emb = topic.get('centroid_embedding')
        if emb:
            if isinstance(emb, str):
                emb = json.loads(emb)
            embeddings.append(emb)
            valid_topics.append(topic)

    if not embeddings:
        print("❌ 유효한 임베딩 없음")
        return

    print(f"🔄 t-SNE 실행 중 ({len(embeddings)}개 임베딩)...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(embeddings)-1))
    coords_2d = tsne.fit_transform(np.array(embeddings))

    # 토픽 분류
    megatopics = []
    global_topics = []
    national_topics = []

    for i, topic in enumerate(valid_topics):
        article_count = topic.get('article_count', 0)
        country_count = topic.get('country_count', 0)

        # 노이즈 필터링
        if article_count < 3:
            continue

        intensity = article_count * country_count
        category = calculate_category(intensity)

        avg_stance = topic.get('avg_stance_score')
        stance_cat, color, stance_kr, opacity = get_stance_info(avg_stance)

        title_kr = topic.get('title_kr') or topic.get('title', 'Unknown')
        title_en = topic.get('title', '')

        bubble = {
            'x': float(coords_2d[i][0]),
            'y': float(coords_2d[i][1]),
            'title_kr': title_kr,
            'title_en': title_en,
            'intensity': intensity,
            'category': category,
            'color': color,
            'opacity': opacity,
            'stance': stance_kr,
            'avg_stance': avg_stance or 50,
            'article_count': article_count,
            'country_count': country_count,
            'emoji': INTENSITY_EMOJI[category]
        }

        # 분류
        if country_count >= 3:
            megatopics.append(bubble)
        elif country_count == 2:
            global_topics.append(bubble)
        elif country_count == 1 and article_count >= 5:
            national_topics.append(bubble)

    print(f"📌 메가토픽: {len(megatopics)}, 글로벌: {len(global_topics)}, 국내: {len(national_topics)}")

    # Plotly Figure (Dark Mode)
    fig = go.Figure()

    # 1. 메가토픽 (가장 크고 선명하게)
    if megatopics:
        fig.add_trace(go.Scatter(
            x=[b['x'] for b in megatopics],
            y=[b['y'] for b in megatopics],
            mode='markers+text',
            marker=dict(
                size=[max(b['intensity']/1.2, 35) for b in megatopics],
                color=[b['color'] for b in megatopics],
                opacity=[b['opacity'] for b in megatopics],
                line=dict(width=2, color='rgba(255,255,255,0.3)'),
                sizemode='diameter'
            ),
            text=[f"{b['emoji']}" for b in megatopics],
            textposition="middle center",
            textfont=dict(size=16, color='white'),
            name='메가토픽',
            hovertemplate=(
                "<b style='font-size:15px; color:#fafafa'>%{customdata[0]}</b><br>" +
                "<span style='font-size:11px; color:#a1a1aa'>%{customdata[1]}</span><br><br>" +
                "<span style='color:#10b981'>🌍 %{customdata[2]}개국</span> · " +
                "<span style='color:#60a5fa'>📰 %{customdata[3]}건</span><br>" +
                "<span style='color:#fbbf24'>📊 %{customdata[4]} (%{customdata[5]:.0f}점)</span><br>" +
                "<span style='color:#a78bfa'>💪 영향력 %{customdata[6]}</span>" +
                "<extra></extra>"
            ),
            customdata=[
                [b['title_kr'], b['title_en'], b['country_count'],
                 b['article_count'], b['stance'], b['avg_stance'], b['intensity']]
                for b in megatopics
            ]
        ))

    # 2. 글로벌 토픽
    if global_topics:
        fig.add_trace(go.Scatter(
            x=[b['x'] for b in global_topics],
            y=[b['y'] for b in global_topics],
            mode='markers',
            marker=dict(
                size=[max(b['intensity']/2, 20) for b in global_topics],
                color=[b['color'] for b in global_topics],
                opacity=[b['opacity'] * 0.8 for b in global_topics],
                line=dict(width=1.5, color='rgba(255,255,255,0.2)'),
                sizemode='diameter'
            ),
            name='글로벌',
            hovertemplate=(
                "<b style='color:#fafafa'>%{customdata[0]}</b><br>" +
                "<span style='color:#10b981'>🌍 %{customdata[1]}개국</span> · " +
                "<span style='color:#60a5fa'>📰 %{customdata[2]}건</span><br>" +
                "<span style='color:#fbbf24'>📊 %{customdata[3]}</span>" +
                "<extra></extra>"
            ),
            customdata=[
                [b['title_kr'], b['country_count'], b['article_count'], b['stance']]
                for b in global_topics
            ]
        ))

    # 3. 국내 주요 토픽
    if national_topics:
        fig.add_trace(go.Scatter(
            x=[b['x'] for b in national_topics],
            y=[b['y'] for b in national_topics],
            mode='markers',
            marker=dict(
                size=[max(b['intensity']/3, 12) for b in national_topics],
                color=[b['color'] for b in national_topics],
                opacity=[b['opacity'] * 0.6 for b in national_topics],
                line=dict(width=1, color='rgba(255,255,255,0.15)'),
                sizemode='diameter'
            ),
            name='국내',
            hovertemplate=(
                "<b style='color:#fafafa'>%{customdata[0]}</b><br>" +
                "<span style='color:#60a5fa'>📰 %{customdata[1]}건</span> · " +
                "<span style='color:#fbbf24'>%{customdata[2]}</span>" +
                "<extra></extra>"
            ),
            customdata=[
                [b['title_kr'], b['article_count'], b['stance']]
                for b in national_topics
            ]
        ))

    # 다크모드 레이아웃 (사이트와 동일)
    fig.update_layout(
        title=dict(
            text=(
                '<b style="font-size:28px; color:#fafafa; font-family: Georgia, serif">글로벌 뉴스 지형도</b><br>'
                '<span style="font-size:13px; color:#a1a1aa">크기 = 영향력 (기사수 × 국가수) · 색상 = 성향</span>'
            ),
            x=0.5,
            xanchor='center',
            y=0.97,
            yanchor='top'
        ),

        # 다크 배경 (사이트와 동일)
        plot_bgcolor='#18181b',   # zinc-900
        paper_bgcolor='#09090b',  # zinc-950

        # 축 숨김
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            title=''
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            title=''
        ),

        # 범례 스타일
        showlegend=True,
        legend=dict(
            title=dict(text="<b style='color:#fafafa'>토픽 타입</b>"),
            font=dict(size=12, family='Arial', color='#d4d4d8'),
            bgcolor="rgba(24, 24, 27, 0.9)",  # zinc-900
            bordercolor="#3f3f46",  # zinc-700
            borderwidth=1,
            x=1.01,
            y=1,
            xanchor='left',
            yanchor='top'
        ),

        hovermode='closest',
        height=850,
        width=1400,
        margin=dict(l=40, r=200, t=120, b=40)
    )

    # 성향 가이드 (Emerald 강조)
    fig.add_annotation(
        text=(
            '<b style="color:#fafafa; font-size:13px">성향 범례</b><br><br>'
            '<span style="color:#ef4444">●</span> <span style="color:#e4e4e7">비판적 (0-33)</span><br>'
            '<span style="color:#71717a">●</span> <span style="color:#e4e4e7">중립 (34-66)</span><br>'
            '<span style="color:#10b981">●</span> <span style="color:#e4e4e7">지지 (67-100)</span><br><br>'
            '<span style="font-size:11px; color:#71717a">투명도 = 성향 강도</span>'
        ),
        xref="paper", yref="paper",
        x=1.01, y=0.5,
        xanchor='left', yanchor='middle',
        showarrow=False,
        bgcolor="rgba(24, 24, 27, 0.9)",
        bordercolor="#3f3f46",
        borderwidth=1,
        borderpad=12,
        font=dict(size=11, family='Arial'),
        align='left'
    )

    # 저장
    output_path = root_dir / "topic_map_branded.html"
    fig.write_html(str(output_path))

    print(f"\n✅ 저장 완료: {output_path}")
    print(f"\n📊 요약:")
    print(f"   🔥 메가토픽: {len(megatopics)}개")
    print(f"   🌍 글로벌: {len(global_topics)}개")
    print(f"   📍 국내: {len(national_topics)}개")
    print(f"\n💡 브라우저에서 열어보세요!")

if __name__ == "__main__":
    visualize_branded_map()
