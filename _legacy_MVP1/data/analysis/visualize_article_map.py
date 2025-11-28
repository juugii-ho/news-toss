import os
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from supabase import create_client
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_data():
    print("Fetching articles...")
    # Fetch articles with embedding and topic_id
    # We need to paginate because there might be many articles
    all_articles = []
    offset = 0
    BATCH_SIZE = 1000
    
    while True:
        res = supabase.table("mvp_articles") \
            .select("id, title, country_code, embedding, topic_id, stance") \
            .not_.is_("embedding", "null") \
            .range(offset, offset + BATCH_SIZE - 1) \
            .execute()
            
        if not res.data:
            break
            
        all_articles.extend(res.data)
        offset += BATCH_SIZE
        print(f"Fetched {len(all_articles)} articles...")
        
    print(f"Total articles fetched: {len(all_articles)}")
    
    print("Fetching topics...")
    # Fetch topics to get titles
    # Assuming not too many topics, fetch all
    topics_res = supabase.table("mvp_topics").select("id, title, title_kr").execute()
    topics_map = {t['id']: t for t in topics_res.data}
    
    # Calculate article counts locally
    for t_id in topics_map:
        topics_map[t_id]['article_count'] = 0
        
    for a in all_articles:
        t_id = a.get('topic_id')
        if t_id in topics_map:
            topics_map[t_id]['article_count'] += 1
            
    return all_articles, topics_map

def process_and_visualize(articles, topics_map):
    print("Processing data...")
    
    # Filter out articles without embeddings
    valid_articles = [a for a in articles if a.get('embedding')]
    
    if not valid_articles:
        print("No valid articles found.")
        return

    # Prepare data for PCA
    embeddings = []
    metadata = []
    
    for a in valid_articles:
        emb = a['embedding']
        if isinstance(emb, str):
            emb = json.loads(emb)
        embeddings.append(emb)
        
        topic_id = a.get('topic_id')
        topic = topics_map.get(topic_id)
        
        topic_title = "Unclustered"
        is_noise = True
        
        if topic:
            topic_title = topic.get('title_kr') or topic.get('title')
            # Noise Filtering: Hide topics with < 3 articles
            if topic.get('article_count', 0) >= 3:
                is_noise = False
        
        metadata.append({
            "title": a.get('title'),
            "country": a.get('country_code'),
            "stance": a.get('stance'),
            "topic_title": topic_title,
            "is_noise": is_noise
        })

    X = np.array(embeddings)
    
    # PCA to 2D
    print("Running PCA...")
    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X)
    
    # Create DataFrame
    df = pd.DataFrame(metadata)
    df['x'] = X_2d[:, 0]
    df['y'] = X_2d[:, 1]
    
    # Separate Noise and Signals
    df_signal = df[~df['is_noise']].copy()
    df_noise = df[df['is_noise']].copy()
    
    print(f"Signals: {len(df_signal)}, Noise: {len(df_noise)}")
    
    # --- Visualization (Premium Polish) ---
    fig = go.Figure()
    
    # 1. Plot Noise (Subtle Starfield)
    fig.add_trace(go.Scatter(
        x=df_noise['x'], y=df_noise['y'],
        mode='markers',
        marker=dict(color='white', size=2, opacity=0.15), # Faint stars
        name='Noise',
        hoverinfo='skip'
    ))
    
    # 2. Plot Signals (Neon Accents)
    # Calculate centroids for auto-labeling
    topic_centroids = df_signal.groupby('topic_title')[['x', 'y']].mean().reset_index()
    
    # Neon Palette
    neon_colors = [
        '#00FFFF', # Cyan
        '#FF00FF', # Magenta
        '#FFFF00', # Yellow
        '#00FF00', # Lime
        '#FF4500', # OrangeRed
        '#1E90FF', # DodgerBlue
        '#FF1493', # DeepPink
        '#7FFF00', # Chartreuse
    ]
    
    unique_topics = df_signal['topic_title'].unique()
    topic_color_map = {t: neon_colors[i % len(neon_colors)] for i, t in enumerate(unique_topics)}
    df_signal['color'] = df_signal['topic_title'].map(topic_color_map)
    
    # Custom Hover Template (HTML Mini Card)
    hovertemplate = (
        "<b>%{customdata[0]}</b><br>" +
        "<span style='font-size:10px; color: #aaa;'>%{customdata[1]} | %{customdata[2]}</span><br>" +
        "<i>%{customdata[3]}</i>" +
        "<extra></extra>"
    )
    
    fig.add_trace(go.Scatter(
        x=df_signal['x'], y=df_signal['y'],
        mode='markers',
        marker=dict(
            color=df_signal['color'],
            size=6,
            opacity=0.9,
            line=dict(width=0) # No border for glow effect
        ),
        customdata=df_signal[['topic_title', 'country', 'stance', 'title']],
        hovertemplate=hovertemplate,
        name='Articles'
    ))
    
    # 3. Add Labels (Top 20 Only, Clean Typography)
    topic_counts = df_signal['topic_title'].value_counts()
    top_topics = topic_counts.head(20).index.tolist()
    visible_centroids = topic_centroids[topic_centroids['topic_title'].isin(top_topics)]
    
    fig.add_trace(go.Scatter(
        x=visible_centroids['x'], y=visible_centroids['y'],
        mode='text',
        text=visible_centroids['topic_title'],
        textposition="top center",
        textfont=dict(size=11, color='white', family="Inter, sans-serif", weight="bold"),
        # Add a subtle background to text for readability? Plotly text doesn't support bg easily in scatter.
        # We rely on high contrast white text on dark bg.
        name='Labels'
    ))
    
    # 4. Premium Layout (Dark Mode, No Grid)
    fig.update_layout(
        title=dict(
            text="NEWS WEATHER MAP",
            font=dict(size=24, color='white', family="Inter, sans-serif", weight="bold"),
            x=0.05,
            y=0.95
        ),
        width=1400,
        height=900,
        template="plotly_dark", # Dark Theme
        paper_bgcolor='#111111', # Deep Black/Grey
        plot_bgcolor='#111111',
        showlegend=False, # Hide legend for cleaner look
        hovermode="closest",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
        margin=dict(l=0, r=0, t=0, b=0) # Full bleed
    )
    
    output_file = root_dir / "article_clusters_map_service.html"
    fig.write_html(output_file)
    print(f"Map saved to {output_file}")

if __name__ == "__main__":
    articles, topics_map = fetch_data()
    process_and_visualize(articles, topics_map)
