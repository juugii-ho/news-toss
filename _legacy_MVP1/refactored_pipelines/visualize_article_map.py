import os
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial import ConvexHull
from collections import defaultdict
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
root_dir = Path(__file__).resolve().parent
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Clustering Logic ---

def cluster_within_group(articles, threshold=0.60):
    if not articles:
        return [], []
    
    embeddings = np.array([a['embedding'] for a in articles])
    clusters = []
    centroids = []
    assigned = [False] * len(articles)
    
    for i in range(len(articles)):
        if assigned[i]: continue
        
        current_cluster = [articles[i]]
        assigned[i] = True
        
        for j in range(i + 1, len(articles)):
            if assigned[j]: continue
            sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
            if sim >= threshold:
                current_cluster.append(articles[j])
                assigned[j] = True
        
        clusters.append(current_cluster)
        cluster_embeddings = np.array([a['embedding'] for a in current_cluster])
        centroids.append(np.mean(cluster_embeddings, axis=0))
        
    return clusters, centroids

def run_clustering_logic(articles):
    print("Running 2-Stage Clustering (Optimized: Nat=0.60, Glob=0.85)...")
    
    # Stage 1: National
    country_groups = defaultdict(list)
    for art in articles:
        country_groups[art['country_code']].append(art)
        
    national_topics = []
    for cc, group in country_groups.items():
        # National Threshold 0.60 (Looser to form solid chunks)
        sub_clusters, sub_centroids = cluster_within_group(group, threshold=0.60)
        for i, sub_c in enumerate(sub_clusters):
            national_topics.append({
                "centroid": sub_centroids[i],
                "articles": sub_c,
                "country": cc
            })
            
    # Stage 2: Global
    if not national_topics:
        return []

    topic_embeddings = np.array([t['centroid'] for t in national_topics])
    final_clusters = []
    assigned_topics = [False] * len(national_topics)
    
    for i in range(len(national_topics)):
        if assigned_topics[i]: continue
        
        current_global_cluster_articles = list(national_topics[i]['articles'])
        assigned_topics[i] = True
        
        for j in range(i + 1, len(national_topics)):
            if assigned_topics[j]: continue
            sim = cosine_similarity([topic_embeddings[i]], [topic_embeddings[j]])[0][0]
            if sim >= 0.85: # Global Threshold 0.85 (Strict to avoid blobs)
                current_global_cluster_articles.extend(national_topics[j]['articles'])
                assigned_topics[j] = True
                
        final_clusters.append(current_global_cluster_articles)
        
    return final_clusters

# --- Main Visualization Logic ---

def main():
    print("Fetching articles...")
    all_articles = []
    offset = 0
    BATCH_SIZE = 1000
    while True:
        response = supabase.table("mvp_articles") \
            .select("id, title, title_kr, country_code, embedding, summary") \
            .not_.is_("embedding", "null") \
            .range(offset, offset + BATCH_SIZE - 1) \
            .execute()
        batch = response.data
        if not batch: break
        for art in batch:
            if isinstance(art['embedding'], str):
                art['embedding'] = json.loads(art['embedding'])
        all_articles.extend(batch)
        offset += BATCH_SIZE
        print(f"Fetched {len(all_articles)} articles...")

    if not all_articles:
        print("No articles found.")
        return

    # Run Clustering
    clusters = run_clustering_logic(all_articles)
    
    # Map article -> cluster
    article_cluster_map = {}
    cluster_labels = {} # id -> label
    
    for cid, cluster in enumerate(clusters):
        countries = {a['country_code'] for a in cluster}
        if len(countries) >= 3:
            label = f"🔥 Megatopic {cid+1}"
        elif len(countries) > 1:
            label = f"Global Topic {cid+1}"
        else:
            label = f"Topic {cid+1}"
            
        cluster_labels[cid] = label
        for art in cluster:
            article_cluster_map[art['id']] = cid # Store ID for grouping

    # t-SNE
    embeddings = np.array([a['embedding'] for a in all_articles])
    print("Running t-SNE...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(all_articles)-1))
    projections = tsne.fit_transform(embeddings)
    
    # DataFrame
    df_data = []
    for i, art in enumerate(all_articles):
        cid = article_cluster_map.get(art['id'])
        cluster_label = cluster_labels.get(cid, "Unclustered")
        
        # Determine Symbol
        # Megatopic (3+ countries) -> Diamond
        # Robust National (1 country, >=5 articles) -> Square
        # Others -> Circle
        symbol = "circle"
        if cid is not None:
            cluster_size = len(clusters[cid])
            countries = {a['country_code'] for a in clusters[cid]}
            if len(countries) >= 3:
                symbol = "diamond"
            elif len(countries) == 1 and cluster_size >= 5:
                symbol = "square"
        
        # Use Korean title if available, else English title
        display_title = art.get('title_kr') or art.get('title', 'No Title')
        
        df_data.append({
            "x": projections[i, 0],
            "y": projections[i, 1],
            "title": display_title,
            "country": art.get('country_code', 'Unknown'),
            "cluster": cluster_label,
            "cluster_id": cid if cid is not None else -1,
            "summary": (art.get('summary') or '')[:100] + "...",
            "symbol": symbol
        })
        
    df = pd.DataFrame(df_data)
    
    # 1. Base Scatter Plot: Color by Country
    print("Generating Plotly chart...")
    fig = px.scatter(
        df, x="x", y="y",
        color="country", # User Request: Color by Country
        symbol="symbol", # User Request: Shape by Topic Type
        hover_data=["title", "cluster", "summary"], # User Request: See Topic in tooltip
        title="Article Map: Color=Country, Shape=Type (Diamond=Mega, Square=Robust)",
        template="plotly_white"
    )
    
    # 2. Add Boundaries (Convex Hulls) for Topics
    print("Adding topic boundaries...")
    unique_clusters = df['cluster_id'].unique()
    
    for cid in unique_clusters:
        if cid == -1: continue # Skip unclustered
        
        cluster_points = df[df['cluster_id'] == cid][['x', 'y']].values
        
        # Need at least 3 points for a hull
        if len(cluster_points) >= 3:
            try:
                hull = ConvexHull(cluster_points)
                hull_points = cluster_points[hull.vertices]
                # Close the loop
                hull_points = np.vstack((hull_points, hull_points[0]))
                
                fig.add_trace(go.Scatter(
                    x=hull_points[:, 0],
                    y=hull_points[:, 1],
                    mode='lines',
                    line=dict(color='rgba(100, 100, 100, 0.5)', width=1, dash='dot'),
                    fill='toself',
                    fillcolor='rgba(200, 200, 200, 0.1)', # Very light fill to indicate grouping
                    name=cluster_labels[cid],
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # Optional: Add Label at Centroid
                centroid = np.mean(cluster_points, axis=0)
                fig.add_trace(go.Scatter(
                    x=[centroid[0]],
                    y=[centroid[1]],
                    mode='text',
                    text=[cluster_labels[cid]],
                    textposition="top center",
                    textfont=dict(size=9, color='gray'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
            except Exception as e:
                print(f"Could not draw hull for cluster {cid}: {e}")
        elif len(cluster_points) == 2:
            # Draw a line for 2 points
            fig.add_trace(go.Scatter(
                x=cluster_points[:, 0],
                y=cluster_points[:, 1],
                mode='lines',
                line=dict(color='rgba(100, 100, 100, 0.5)', width=1, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ))

    fig.update_traces(marker=dict(size=6, opacity=0.8))
    fig.update_layout(
        legend_title_text='Country',
        hovermode='closest'
    )
    
    out_path = root_dir / "article_clusters_map_boundary.html"
    fig.write_html(out_path)
    print(f"Saved visualization to {out_path}")

if __name__ == "__main__":
    main()
