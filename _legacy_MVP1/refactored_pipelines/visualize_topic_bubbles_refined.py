"""
토픽 버블 시각화 (소비자 관점 최적화)

피드백 반영:
- 토픽 중심 (기사 점 제거)
- 파스텔 색상 (stance 기반)
- 미세 애니메이션 효과
- Top N 필터링
- 절제된 디자인
"""

import os
import json
import numpy as np
import plotly.graph_objects as go
from sklearn.manifold import TSNE
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

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

# 파스텔 컬러 팔레트 (stance 기반)
STANCE_COLORS = {
    'critical': '#fca5a5',      # 파스텔 레드
    'neutral': '#d4d4d8',       # 파스텔 그레이
    'supportive': '#86efac',    # 파스텔 그린
    'mixed': '#fcd34d'          # 파스텔 옐로우 (분산 높음)
}

# Category 이모지
CATEGORY_EMOJI = {
    1: '🌱',
    2: '🌿',
    3: '🌀',
    4: '🌪️',
    5: '⚡️'
}

def get_stance_category(avg_score, article_count):
    """
    Stance 카테고리 결정
    0-33: Critical
    34-66: Neutral
    67-100: Supportive
    """
    if avg_score is None:
        return 'neutral'

    if avg_score < 34:
        return 'critical'
    elif avg_score < 67:
        return 'neutral'
    else:
        return 'supportive'

def calculate_category(intensity):
    """태풍 등급 (1-5)"""
    if intensity < 20: return 1
    if intensity < 50: return 2
    if intensity < 100: return 3
    if intensity < 150: return 4
    return 5

def visualize_topic_bubbles():
    """
    깔끔한 토픽 버블 맵
    """

    print("Fetching topics from Supabase...")

    # 토픽 가져오기 (메가토픽 우선)
    topics_response = supabase.table("mvp_topics")\
        .select("*")\
        .not_.is_("centroid_embedding", "null")\
        .order("country_count", desc=True)\
        .limit(100)\
        .execute()

    topics = topics_response.data

    if not topics:
        print("No topics found with embeddings")
        return

    print(f"Found {len(topics)} topics")

    # Calculate article counts locally (since column might be missing)
    print("Fetching article counts...")
    articles_response = supabase.table("mvp_articles").select("topic_id").execute()
    article_counts = {}
    if articles_response.data:
        from collections import Counter
        counts = Counter([a['topic_id'] for a in articles_response.data if a.get('topic_id')])
        article_counts = dict(counts)
    
    # Update topics with local count
    for t in topics:
        t['article_count'] = article_counts.get(t['id'], 0)

    # 임베딩 추출
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
        print("No valid embeddings")
        return

    print(f"Running t-SNE on {len(embeddings)} embeddings...")

    # t-SNE
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(embeddings)-1))
    coords_2d = tsne.fit_transform(np.array(embeddings))

    # 버블 데이터 준비
    bubbles = {
        'megatopic': [],      # 3+ countries (Top tier)
        'global': [],         # 2 countries
        'robust_national': [], # 1 country, 5+ articles
        'noise': []           # Others (숨김)
    }

    for i, topic in enumerate(valid_topics):
        article_count = topic.get('article_count', 0)
        country_count = topic.get('country_count', 0)

        # 노이즈 필터링 (3건 미만)
        if article_count < 3:
            continue

        intensity = article_count * country_count
        category = calculate_category(intensity)

        avg_stance = topic.get('avg_stance_score')
        stance_cat = get_stance_category(avg_stance, article_count)
        color = STANCE_COLORS[stance_cat]

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
            'stance': stance_cat,
            'avg_stance': avg_stance or 50,
            'article_count': article_count,
            'country_count': country_count,
            'emoji': CATEGORY_EMOJI[category]
        }

        # 토픽 타입 분류
        if country_count >= 3:
            bubbles['megatopic'].append(bubble)
        elif country_count == 2:
            bubbles['global'].append(bubble)
        elif country_count == 1 and article_count >= 5:
            bubbles['robust_national'].append(bubble)
        else:
            bubbles['noise'].append(bubble)

    print(f"Megatopics: {len(bubbles['megatopic'])}")
    print(f"Global: {len(bubbles['global'])}")
    print(f"Robust National: {len(bubbles['robust_national'])}")
    print(f"Noise (hidden): {len(bubbles['noise'])}")

    # Plotly Figure
    fig = go.Figure()

    # 1. Megatopics (최우선, 가장 크고 진하게)
    if bubbles['megatopic']:
        fig.add_trace(go.Scatter(
            x=[b['x'] for b in bubbles['megatopic']],
            y=[b['y'] for b in bubbles['megatopic']],
            mode='markers+text',
            marker=dict(
                size=[max(b['intensity']/1.5, 30) for b in bubbles['megatopic']],
                color=[b['color'] for b in bubbles['megatopic']],
                opacity=0.8,
                line=dict(width=3, color='white'),
                sizemode='diameter'
            ),
            text=[f"{b['emoji']} {b['title_kr'][:12]}..." for b in bubbles['megatopic']],
            textposition="top center",
            textfont=dict(size=11, color='#1f2937', family='Arial'),
            name='🔥 메가토픽',
            hovertemplate=(
                "<b style='font-size:14px'>%{customdata[0]}</b><br>" +
                "<i style='color:#666'>%{customdata[1]}</i><br><br>" +
                "🌍 <b>%{customdata[2]}</b>개국<br>" +
                "📰 <b>%{customdata[3]}</b>건<br>" +
                "📊 성향: <b>%{customdata[4]}</b> (%{customdata[5]:.0f}점)<br>" +
                "💪 영향력: <b>%{customdata[6]}</b><br>" +
                "<extra></extra>"
            ),
            customdata=[
                [b['title_kr'], b['title_en'], b['country_count'],
                 b['article_count'], b['stance'], b['avg_stance'], b['intensity']]
                for b in bubbles['megatopic']
            ]
        ))

    # 2. Global Topics
    if bubbles['global']:
        fig.add_trace(go.Scatter(
            x=[b['x'] for b in bubbles['global']],
            y=[b['y'] for b in bubbles['global']],
            mode='markers+text',
            marker=dict(
                size=[max(b['intensity']/2, 20) for b in bubbles['global']],
                color=[b['color'] for b in bubbles['global']],
                opacity=0.7,
                line=dict(width=2, color='white'),
                sizemode='diameter'
            ),
            text=[f"{b['emoji']} {b['title_kr'][:10]}..." for b in bubbles['global']],
            textposition="top center",
            textfont=dict(size=9, color='#374151', family='Arial'),
            name='🌍 글로벌 토픽',
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>" +
                "<i style='color:#666'>%{customdata[1]}</i><br><br>" +
                "🌍 %{customdata[2]}개국 | 📰 %{customdata[3]}건<br>" +
                "📊 성향: %{customdata[4]} (%{customdata[5]:.0f}점)<br>" +
                "<extra></extra>"
            ),
            customdata=[
                [b['title_kr'], b['title_en'], b['country_count'],
                 b['article_count'], b['stance'], b['avg_stance']]
                for b in bubbles['global']
            ]
        ))

    # 3. Robust National (옵션, 기본 표시)
    if bubbles['robust_national']:
        fig.add_trace(go.Scatter(
            x=[b['x'] for b in bubbles['robust_national']],
            y=[b['y'] for b in bubbles['robust_national']],
            mode='markers',  # 텍스트 없음 (깔끔하게)
            marker=dict(
                size=[max(b['intensity']/3, 12) for b in bubbles['robust_national']],
                color=[b['color'] for b in bubbles['robust_national']],
                opacity=0.5,
                line=dict(width=1, color='white'),
                sizemode='diameter'
            ),
            name='📍 국내 토픽',
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>" +
                "📰 %{customdata[1]}건 | 📊 성향: %{customdata[2]}<br>" +
                "<extra></extra>"
            ),
            customdata=[
                [b['title_kr'], b['article_count'], b['stance']]
                for b in bubbles['robust_national']
            ]
        ))

    # 레이아웃 (절제된 디자인)
    fig.update_layout(
        title={
            'text': (
                '<b style="font-size:26px">🌍 글로벌 뉴스 지형도</b><br>'
                '<span style="font-size:14px;color:#6b7280">크기 = 영향력 | 색상 = 성향</span>'
            ),
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98,
            'yanchor': 'top'
        },
        template="plotly_white",
        hovermode='closest',

        # 범례 (우측 카드)
        showlegend=True,
        legend=dict(
            title="<b>토픽 타입</b>",
            font=dict(size=11, family='Arial'),
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#e5e7eb",
            borderwidth=1,
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top'
        ),

        # 축 (숨김, 은은한 배경)
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.03)',
            showticklabels=False,
            zeroline=False,
            title=''
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.03)',
            showticklabels=False,
            zeroline=False,
            title=''
        ),

        # 배경 (그라데이션 느낌)
        plot_bgcolor='#fafafa',
        paper_bgcolor='white',

        # 크기
        height=800,
        width=1200,

        # 여백
        margin=dict(l=50, r=200, t=100, b=50)
    )

    # Annotation (범례 추가 정보)
    fig.add_annotation(
        text=(
            '<b>색상 가이드</b><br>'
            '<span style="color:#fca5a5">■</span> 비판적 (0-33)<br>'
            '<span style="color:#d4d4d8">■</span> 중립 (34-66)<br>'
            '<span style="color:#86efac">■</span> 지지 (67-100)'
        ),
        xref="paper", yref="paper",
        x=1.02, y=0.5,
        xanchor='left', yanchor='middle',
        showarrow=False,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#e5e7eb",
        borderwidth=1,
        borderpad=10,
        font=dict(size=10, family='Arial')
    )

    # 저장
    output_path = root_dir / "topic_bubbles_refined.html"
    fig.write_html(str(output_path))
    print(f"\n✅ Saved to {output_path}")
    print(f"\n📊 Summary:")
    print(f"   🔥 Megatopics: {len(bubbles['megatopic'])}")
    print(f"   🌍 Global: {len(bubbles['global'])}")
    print(f"   📍 National: {len(bubbles['robust_national'])}")
    print(f"   (Noise filtered: {len(bubbles['noise'])})")

if __name__ == "__main__":
    visualize_topic_bubbles()
