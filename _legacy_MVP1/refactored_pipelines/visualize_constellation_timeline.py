import os
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

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

# --- Configuration ---
DAYS_TO_FETCH = 7
MIN_INTENSITY_FOR_LABEL = 50  # Only show labels for topics with intensity > N
THEME_BG = "#1c1917" # Stone 900 (Warm Dark)
THEME_PAPER = "#0c0a09" # Stone 950
COLOR_CRITICAL = "rgba(248, 113, 113, 0.9)" # Red 400
COLOR_NEUTRAL = "rgba(156, 163, 175, 0.5)"  # Gray 400
COLOR_SUPPORTIVE = "rgba(74, 222, 128, 0.9)" # Green 400

def get_stance_color(score):
    if score is None: return COLOR_NEUTRAL
    if score < 40: return COLOR_CRITICAL
    if score > 60: return COLOR_SUPPORTIVE
    return COLOR_NEUTRAL

def fetch_history(days=7):
    print(f"📅 Fetching {days}-day topic history...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    response = supabase.table("mvp_topic_history")\
        .select("*")\
        .gte("date", start_date.strftime('%Y-%m-%d'))\
        .lte("date", end_date.strftime('%Y-%m-%d'))\
        .order("date", desc=False)\
        .execute()
    
    data = response.data
    print(f"✅ Found {len(data)} records")
    return data

def process_coordinates(history_data):
    """
    Generate 2D coordinates using t-SNE on ALL history records.
    This ensures that the same topic (if embedding is similar) stays close,
    but drift is visible.
    """
    print("🧮 Calculating 2D projection (t-SNE)...")
    
    # Extract embeddings
    embeddings = []
    valid_indices = []
    
    for i, record in enumerate(history_data):
        emb = record.get('centroid_embedding')
        if emb:
            if isinstance(emb, str):
                emb = json.loads(emb)
            embeddings.append(emb)
            valid_indices.append(i)
            
    if not embeddings:
        print("❌ No embeddings found.")
        return history_data
        
    X = np.array(embeddings)
    
    # Reduce dim first if huge
    n_samples = X.shape[0]
    if X.shape[1] > 50:
        n_comps = min(50, n_samples)
        if n_comps < 2: n_comps = 2 # Minimum for PCA
        pca = PCA(n_components=n_comps, random_state=42)
        X = pca.fit_transform(X)
        
    # t-SNE
    # Perplexity must be < n_samples
    perp = min(30, len(X) - 1) if len(X) > 1 else 1
    tsne = TSNE(n_components=2, perplexity=perp, random_state=42, init='pca', learning_rate='auto')
    X_2d = tsne.fit_transform(X)
    
    # Normalize to -50 ~ 50 range for consistency
    x_min, x_max = X_2d[:, 0].min(), X_2d[:, 0].max()
    y_min, y_max = X_2d[:, 1].min(), X_2d[:, 1].max()
    
    # Avoid div by zero
    x_range = x_max - x_min if x_max != x_min else 1
    y_range = y_max - y_min if y_max != y_min else 1
    
    X_norm = (X_2d - [x_min, y_min]) / [x_range, y_range] # 0~1
    X_final = (X_norm - 0.5) * 100 # -50 ~ 50
    
    # Assign back
    for idx, real_idx in enumerate(valid_indices):
        history_data[real_idx]['viz_x'] = X_final[idx, 0]
        history_data[real_idx]['viz_y'] = X_final[idx, 1]
        
    return history_data

def create_viz(history_data):
    # Group by date
    from collections import defaultdict
    by_date = defaultdict(list)
    for r in history_data:
        if 'viz_x' in r: # Only plot if we have coords
            by_date[r['date']].append(r)
            
    dates = sorted(by_date.keys())
    if not dates:
        print("❌ No valid data for visualization.")
        return

    frames = []
    
    # Common marker settings
    def get_trace_data(topics):
        x, y, sz, c, txt, hov = [], [], [], [], [], []
        
        # Sort by size (intensity) so small ones are drawn first (behind)
        topics.sort(key=lambda t: t.get('intensity', 0) or 0)
        
        for t in topics:
            x.append(t['viz_x'])
            y.append(t['viz_y'])
            
            # Size: Log scale or sqrt scale for better perception
            intensity = t.get('intensity', 0) or 10
            size = np.sqrt(intensity) * 3  # Adjust multiplier
            size = max(8, min(size, 60))   # Clamp
            sz.append(size)
            
            # Color
            score = t.get('avg_stance_score')
            c.append(get_stance_color(score))
            
            # Text (Label) - Only for top items
            title = t.get('title_kr') or t.get('title_en', 'Unknown')
            # Show label if intensity is high enough
            if intensity > MIN_INTENSITY_FOR_LABEL:
                short_title = title[:8] + '..' if len(title) > 8 else title
                txt.append(short_title)
            else:
                txt.append("")
                
            # Hover
            score_str = f"{score:.0f}" if score is not None else "?"
            drift = t.get('drift_score')
            drift_str = f"{drift:.3f}" if drift else "0.000"
            
            hover_content = (
                f"<b>{title}</b><br>"
                f"<span style='color:#a8a29e'>영향력: {intensity} | 성향: {score_str}</span><br>"
                f"<span style='color:#78716c'>변화량: {drift_str}</span>"
            )
            hov.append(hover_content)
            
        return x, y, sz, c, txt, hov

    # Create Frames
    for date in dates:
        x, y, sz, c, txt, hov = get_trace_data(by_date[date])
        
        frames.append(go.Frame(
            data=[go.Scatter(
                x=x, y=y,
                mode='markers+text',
                marker=dict(
                    size=sz,
                    color=c,
                    opacity=0.9,
                    line=dict(width=1, color='rgba(255,255,255,0.3)'),
                    sizemode='diameter'
                ),
                text=txt,
                textposition="top center",
                textfont=dict(family="Pretendard, sans-serif", size=11, color="#e5e5e5"),
                hovertext=hov,
                hoverinfo='text'
            )],
            name=date,
            layout=go.Layout(
                annotations=[
                    dict(
                        text=f"{date}",
                        x=0.5, y=1.05,
                        xref="paper", yref="paper",
                        showarrow=False,
                        font=dict(size=14, color="#a8a29e")
                    )
                ]
            )
        ))
        
    # Initial Data (First Frame)
    x0, y0, sz0, c0, txt0, hov0 = get_trace_data(by_date[dates[0]])
    
    fig = go.Figure(
        data=[go.Scatter(
            x=x0, y=y0,
            mode='markers+text',
            marker=dict(
                size=sz0,
                color=c0,
                opacity=0.9,
                line=dict(width=1, color='rgba(255,255,255,0.3)'),
                sizemode='diameter'
            ),
            text=txt0,
            textposition="top center",
            textfont=dict(family="Pretendard, sans-serif", size=11, color="#e5e5e5"),
            hovertext=hov0,
            hoverinfo='text'
        )],
        frames=frames
    )
    
    # Layout
    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, t=40, b=80),
        plot_bgcolor=THEME_BG,
        paper_bgcolor=THEME_PAPER,
        title=dict(
            text="<b>News Weather Map</b>",
            y=0.96,
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(size=18, color="#fafafa")
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-55, 55], fixedrange=True),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-55, 55], fixedrange=True),
        hovermode='closest',
        
        # Controls
        updatemenus=[
            dict(
                type='buttons',
                showactive=False,
                y=0.05,
                x=0.5,
                xanchor='center',
                yanchor='bottom',
                pad=dict(t=0, r=10),
                bgcolor="rgba(255,255,255,0.1)",
                bordercolor="rgba(255,255,255,0.2)",
                font=dict(color="#fafafa"),
                buttons=[
                    dict(label='▶', method='animate',
                         args=[None, dict(frame=dict(duration=800, redraw=True), fromcurrent=True, mode='immediate')]),
                    dict(label='⏸', method='animate',
                         args=[[None], dict(frame=dict(duration=0, redraw=False), mode='immediate', transition=dict(duration=0))])
                ]
            )
        ],
        sliders=[
            dict(
                active=0,
                yanchor='bottom',
                y=0,
                xanchor='center',
                x=0.5,
                currentvalue=dict(visible=False),
                pad=dict(b=10, t=10),
                len=0.8,
                steps=[
                    dict(
                        args=[[f.name], dict(frame=dict(duration=300, redraw=True), mode='immediate')],
                        label=f.name[5:],
                        method='animate'
                    ) for f in frames
                ],
                bgcolor=THEME_BG,
                bordercolor="rgba(255,255,255,0.2)",
                font=dict(color="#a8a29e", size=10)
            )
        ]
    )
    
    # Legend (Custom Annotation)
    fig.add_annotation(
        text=(
            "<span style='color:#f87171'>●</span> Critical "
            "<span style='color:#9ca3af'>●</span> Neutral "
            "<span style='color:#4ade80'>●</span> Supportive"
        ),
        xref="paper", yref="paper",
        x=0.5, y=0.90,
        showarrow=False,
        font=dict(size=10, color="#a8a29e"),
        bgcolor="rgba(0,0,0,0)"
    )
    
    output_path = root_dir / "constellation_timeline.html"
    fig.write_html(str(output_path), config={'displayModeBar': False}) # Hide Plotly toolbar
    print(f"✅ Saved: {output_path}")

if __name__ == "__main__":
    history = fetch_history(DAYS_TO_FETCH)
    if history:
        history = process_coordinates(history)
        create_viz(history)
    else:
        print("No data.")
