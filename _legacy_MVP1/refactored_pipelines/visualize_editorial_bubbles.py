"""
Editorial Bubble Chart - O의 피드백 100% 반영
- 파스텔 6-8색 제한 팔레트
- 오프화이트 배경, 차분한 그리드
- Top N만 표시 (메가토픽 우선)
- Geist/Pretendard 스타일 폰트
- 미세한 시각적 계층
- 토픽 중심 (기사 점 완전 숨김)
"""

import os
import json
import numpy as np
import plotly.graph_objects as go
from sklearn.manifold import TSNE
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from collections import Counter

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

# Editorial Pastel Palette (제한된 6색)
EDITORIAL_COLORS = {
    'critical_strong': '#f59e9e',    # 강한 비판
    'critical_mild': '#fbbebe',      # 약한 비판
    'neutral': '#c7d2dd',            # 중립
    'supportive_mild': '#a8d5ba',    # 약한 지지
    'supportive_strong': '#7dc99c',  # 강한 지지
    'mixed': '#e8c9a1',              # 분산 높음
}

# Background & UI Colors (차분한 톤)
UI_COLORS = {
    'background': '#fafaf9',         # 오프화이트
    'grid': '#f5f5f4',               # 은은한 그리드
    'text_primary': '#27272a',       # 네이비-그레이 (zinc-800)
    'text_secondary': '#71717a',     # 회색 (zinc-500)
    'border': '#e4e4e7',             # 테두리 (zinc-200)
    'accent': '#10b981',             # 액센트 (emerald-500)
}

def get_editorial_color(avg_score, variance=0):
    """
    성향 점수와 분산에 따른 에디토리얼 색상 선택
    - 분산이 높으면(>400) mixed
    - 아니면 점수와 강도에 따라 색상 선택
    """
    if avg_score is None:
        return EDITORIAL_COLORS['neutral']

    # 분산이 높으면 mixed (갈등 높음)
    if variance > 400:
        return EDITORIAL_COLORS['mixed']

    # 중앙(50)에서 벗어난 정도
    deviation = abs(avg_score - 50)

    if avg_score < 34:
        # 비판적
        return EDITORIAL_COLORS['critical_strong'] if deviation > 25 else EDITORIAL_COLORS['critical_mild']
    elif avg_score < 67:
        # 중립
        return EDITORIAL_COLORS['neutral']
    else:
        # 지지
        return EDITORIAL_COLORS['supportive_strong'] if deviation > 25 else EDITORIAL_COLORS['supportive_mild']

def calculate_importance(article_count, country_count):
    """중요도 점수 (크기 결정용)"""
    return article_count * country_count

def visualize_editorial():
    """차분한 에디토리얼 버블 맵"""

    print("📰 뉴스 토픽 로딩...")

    # 토픽 가져오기
    topics_response = supabase.table("mvp_topics")\
        .select("*")\
        .not_.is_("centroid_embedding", "null")\
        .order("country_count", desc=True)\
        .limit(100)\
        .execute()

    topics = topics_response.data

    if not topics:
        print("❌ 토픽을 찾을 수 없습니다")
        return

    # 기사 수 계산
    articles_response = supabase.table("mvp_articles").select("topic_id, stance_score").execute()
    article_counts = Counter([a['topic_id'] for a in articles_response.data if a.get('topic_id')])

    # Stance variance 계산
    stance_by_topic = {}
    for article in articles_response.data:
        tid = article.get('topic_id')
        score = article.get('stance_score')
        if tid and score is not None:
            if tid not in stance_by_topic:
                stance_by_topic[tid] = []
            stance_by_topic[tid].append(score)

    stance_variance = {tid: np.var(scores) if len(scores) > 1 else 0
                      for tid, scores in stance_by_topic.items()}

    for t in topics:
        t['article_count'] = article_counts.get(t['id'], 0)
        t['stance_variance'] = stance_variance.get(t['id'], 0)

    # 임베딩 추출
    embeddings = []
    valid_topics = []

    for topic in topics:
        emb = topic.get('centroid_embedding')
        if emb and topic.get('article_count', 0) >= 3:  # 최소 3개 기사
            if isinstance(emb, str):
                emb = json.loads(emb)
            embeddings.append(emb)
            valid_topics.append(topic)

    if not embeddings:
        print("❌ 유효한 임베딩 없음")
        return

    print(f"🔄 t-SNE 차원 축소 중... ({len(embeddings)}개)")
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(embeddings)-1))
    coords_2d = tsne.fit_transform(np.array(embeddings))

    # 중요도 계산 및 Top N 선택
    for i, topic in enumerate(valid_topics):
        importance = calculate_importance(
            topic.get('article_count', 0),
            topic.get('country_count', 0)
        )
        topic['importance'] = importance
        topic['x'] = float(coords_2d[i][0])
        topic['y'] = float(coords_2d[i][1])

    # 중요도순 정렬
    valid_topics.sort(key=lambda t: t['importance'], reverse=True)

    # Top 15개만 (O의 제안: Top N만 표시)
    TOP_N = 15
    top_topics = valid_topics[:TOP_N]
    other_topics = valid_topics[TOP_N:]

    print(f"📊 핵심 토픽: {len(top_topics)}개 (나머지 {len(other_topics)}개는 숨김)")

    # Plotly Figure
    fig = go.Figure()

    # 1. "더 보기" 토픽들 (매우 연하게, 배경으로)
    if other_topics:
        fig.add_trace(go.Scatter(
            x=[t['x'] for t in other_topics],
            y=[t['y'] for t in other_topics],
            mode='markers',
            marker=dict(
                size=[max(t['importance']/4, 8) for t in other_topics],
                color='#e7e5e4',  # 매우 연한 회색
                opacity=0.25,
                line=dict(width=0),
                sizemode='diameter'
            ),
            name='기타 토픽',
            showlegend=False,
            hoverinfo='skip'
        ))

    # 2. Top N 핵심 토픽 (에디토리얼 스타일)
    top_colors = []
    top_sizes = []
    top_labels = []
    top_customdata = []

    for t in top_topics:
        color = get_editorial_color(
            t.get('avg_stance_score'),
            t.get('stance_variance', 0)
        )
        top_colors.append(color)

        # 크기: 중요도에 비례하되, 너무 크지 않게
        size = min(max(t['importance']/2, 20), 80)
        top_sizes.append(size)

        # 라벨: 메가토픽만 표시
        if t.get('country_count', 0) >= 3:
            title = t.get('title_kr') or t.get('title', '')
            label = title[:15] + '...' if len(title) > 15 else title
            top_labels.append(label)
        else:
            top_labels.append('')

        # Hover 데이터
        top_customdata.append([
            t.get('title_kr') or t.get('title', ''),
            t.get('country_count', 0),
            t.get('article_count', 0),
            t.get('avg_stance_score', 50),
            t.get('stance_variance', 0),
        ])

    fig.add_trace(go.Scatter(
        x=[t['x'] for t in top_topics],
        y=[t['y'] for t in top_topics],
        mode='markers+text',
        marker=dict(
            size=top_sizes,
            color=top_colors,
            opacity=0.75,
            line=dict(width=1.5, color='white'),
            sizemode='diameter'
        ),
        text=top_labels,
        textposition="top center",
        textfont=dict(
            size=11,
            color=UI_COLORS['text_primary'],
            family='Pretendard, -apple-system, sans-serif'
        ),
        name='핵심 토픽',
        hovertemplate=(
            "<b style='font-size:14px; color:#27272a'>%{customdata[0]}</b><br>" +
            "<span style='color:#71717a'>%{customdata[1]}개국 · %{customdata[2]}건</span><br>" +
            "<span style='color:#71717a'>성향: %{customdata[3]:.0f}점 (분산: %{customdata[4]:.0f})</span>" +
            "<extra></extra>"
        ),
        customdata=top_customdata
    ))

    # 레이아웃: 차분하고 에디토리얼
    fig.update_layout(
        # 제목
        title=dict(
            text=(
                '<b style="font-size:24px; color:#27272a; font-family: Pretendard, sans-serif">오늘의 글로벌 대화</b><br>'
                '<span style="font-size:12px; color:#71717a">크기 = 영향력 · 색상 = 성향 · 핵심 15개 토픽</span>'
            ),
            x=0.5,
            xanchor='center',
            y=0.97,
            yanchor='top',
            pad=dict(t=20, b=20)
        ),

        # 배경 (오프화이트)
        plot_bgcolor=UI_COLORS['background'],
        paper_bgcolor='white',

        # 축 (은은한 그리드)
        xaxis=dict(
            showgrid=True,
            gridcolor=UI_COLORS['grid'],
            gridwidth=1,
            showticklabels=False,
            zeroline=False,
            title=''
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=UI_COLORS['grid'],
            gridwidth=1,
            showticklabels=False,
            zeroline=False,
            title=''
        ),

        # 범례 (우측 카드 스타일)
        showlegend=True,
        legend=dict(
            title=dict(
                text="<b style='color:#27272a; font-size:13px'>범례</b>",
                font=dict(family='Pretendard, sans-serif')
            ),
            font=dict(size=11, family='Pretendard, sans-serif', color=UI_COLORS['text_secondary']),
            bgcolor="white",
            bordercolor=UI_COLORS['border'],
            borderwidth=1,
            x=1.02,
            y=0.95,
            xanchor='left',
            yanchor='top'
        ),

        hovermode='closest',
        height=800,
        width=1400,
        margin=dict(l=60, r=250, t=120, b=60)
    )

    # 색상 가이드 (우측 패널)
    fig.add_annotation(
        text=(
            '<b style="color:#27272a; font-size:13px">성향 색상</b><br><br>'
            '<span style="color:#f59e9e">●</span> <span style="color:#52525b">강한 비판</span><br>'
            '<span style="color:#fbbebe">●</span> <span style="color:#52525b">약한 비판</span><br>'
            '<span style="color:#c7d2dd">●</span> <span style="color:#52525b">중립</span><br>'
            '<span style="color:#a8d5ba">●</span> <span style="color:#52525b">약한 지지</span><br>'
            '<span style="color:#7dc99c">●</span> <span style="color:#52525b">강한 지지</span><br>'
            '<span style="color:#e8c9a1">●</span> <span style="color:#52525b">갈등 높음</span>'
        ),
        xref="paper", yref="paper",
        x=1.02, y=0.5,
        xanchor='left', yanchor='middle',
        showarrow=False,
        bgcolor="white",
        bordercolor=UI_COLORS['border'],
        borderwidth=1,
        borderpad=12,
        font=dict(size=11, family='Pretendard, sans-serif'),
        align='left'
    )

    # 데이터 소스 (상단)
    fig.add_annotation(
        text=(
            '<span style="font-size:10px; color:#a1a1aa">'
            'G10 + CN/RU 주요 언론 · 업데이트: 매일 23:30 KST'
            '</span>'
        ),
        xref="paper", yref="paper",
        x=0.5, y=1.0,
        xanchor='center', yanchor='bottom',
        showarrow=False,
        font=dict(family='Pretendard, sans-serif')
    )

    # 저장
    output_path = root_dir / "topic_map_editorial.html"
    fig.write_html(str(output_path))

    print(f"\n✅ 저장 완료: {output_path}")
    print(f"📌 핵심 토픽 {len(top_topics)}개 표시")
    print(f"📊 배경 토픽 {len(other_topics)}개 (연하게)")

if __name__ == "__main__":
    visualize_editorial()
