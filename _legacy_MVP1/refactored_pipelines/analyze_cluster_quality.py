import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
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

# --- Clustering Logic (Same as visualize_article_map.py) ---
def cluster_within_group(articles, threshold=0.60):
    if not articles: return [], []
    embeddings = np.array([a['embedding'] for a in articles])
    
    # Vectorized similarity calculation
    sim_matrix = cosine_similarity(embeddings)
    
    clusters = []
    centroids = []
    assigned = [False] * len(articles)
    
    for i in range(len(articles)):
        if assigned[i]: continue
        current_cluster = [articles[i]]
        assigned[i] = True
        
        # Use the pre-computed row
        sim_scores = sim_matrix[i]
        
        for j in range(i + 1, len(articles)):
            if assigned[j]: continue
            if sim_scores[j] >= threshold:
                current_cluster.append(articles[j])
                assigned[j] = True
                
        clusters.append(current_cluster)
        cluster_embeddings = np.array([a['embedding'] for a in current_cluster])
        centroids.append(np.mean(cluster_embeddings, axis=0))
    return clusters, centroids

def run_clustering_logic(articles):
    # Stage 1: National
    country_groups = defaultdict(list)
    for art in articles:
        country_groups[art['country_code']].append(art)
    national_topics = []
    for cc, group in country_groups.items():
        sub_clusters, sub_centroids = cluster_within_group(group, threshold=0.60)
        for i, sub_c in enumerate(sub_clusters):
            national_topics.append({"centroid": sub_centroids[i], "articles": sub_c, "country": cc})
    # Stage 2: Global
    if not national_topics: return []
    topic_embeddings = np.array([t['centroid'] for t in national_topics])
    
    # Vectorized similarity
    sim_matrix = cosine_similarity(topic_embeddings)
    
    final_clusters = []
    assigned_topics = [False] * len(national_topics)
    for i in range(len(national_topics)):
        if assigned_topics[i]: continue
        current_global_cluster_articles = list(national_topics[i]['articles'])
        assigned_topics[i] = True
        
        sim_scores = sim_matrix[i]
        
        for j in range(i + 1, len(national_topics)):
            if assigned_topics[j]: continue
            if sim_scores[j] >= 0.85:
                current_global_cluster_articles.extend(national_topics[j]['articles'])
                assigned_topics[j] = True
        final_clusters.append(current_global_cluster_articles)
    return final_clusters

def main():
    print("Fetching articles...")
    all_articles = []
    offset = 0
    BATCH_SIZE = 1000
    while True:
        response = supabase.table("mvp_articles").select("id, title, title_kr, country_code, embedding").not_.is_("embedding", "null").range(offset, offset + BATCH_SIZE - 1).execute()
        batch = response.data
        if not batch: break
        for art in batch:
            if isinstance(art['embedding'], str): art['embedding'] = json.loads(art['embedding'])
        all_articles.extend(batch)
        offset += BATCH_SIZE
        print(f"Fetched {len(all_articles)} articles...")

    if not all_articles: return

    clusters = run_clustering_logic(all_articles)
    
    # Analysis
    total_articles = len(all_articles)
    clustered_articles = sum(len(c) for c in clusters)
    noise_articles = total_articles - clustered_articles
    
    megatopics = []
    global_topics = []
    national_topics = []
    
    for c in clusters:
        countries = {a['country_code'] for a in c}
        if len(countries) >= 3: megatopics.append(c)
        elif len(countries) > 1: global_topics.append(c)
        else: national_topics.append(c)
        
    print("\n" + "="*40)
    print(f"📊 Clustering Analysis Report (Thresholds: 0.60 / 0.85)")
    print("="*40)
    print(f"Total Articles: {total_articles}")
    print(f"Clustered: {clustered_articles} ({clustered_articles/total_articles*100:.1f}%)")
    print(f"Noise (Unclustered): {noise_articles} ({noise_articles/total_articles*100:.1f}%)")
    print("-" * 20)
    print(f"🔥 Megatopics (3+ Countries): {len(megatopics)}")
    print(f"🌍 Global Topics (2 Countries): {len(global_topics)}")
    print(f"🏳️ National Topics (1 Country): {len(national_topics)}")
    
    # Analyze National Topic Sizes
    nat_sizes = [len(c) for c in national_topics]
    singletons = sum(1 for s in nat_sizes if s == 1)
    small = sum(1 for s in nat_sizes if 2 <= s <= 4)
    robust = sum(1 for s in nat_sizes if s >= 5)
    
    print("-" * 20)
    print(f"🧐 National Topic Integrity Check:")
    print(f"   - Singletons (1 article): {singletons} ({singletons/len(national_topics)*100:.1f}%) -> Potential Noise")
    print(f"   - Small (2-4 articles): {small}")
    print(f"   - Robust (5+ articles): {robust}")
    print("-" * 20)
    
    # Analyze Cluster Spread (Radius)
    print("\n📏 Cluster Spread Analysis (Widest Boundaries):")
    cluster_spreads = []
    for i, c in enumerate(clusters):
        if len(c) < 3: continue # Skip small ones
        embeddings = np.array([a['embedding'] for a in c])
        centroid = np.mean(embeddings, axis=0)
        # Avg distance to centroid
        dists = np.linalg.norm(embeddings - centroid, axis=1)
        avg_dist = np.mean(dists)
        cluster_spreads.append((i, avg_dist, c))
        
    cluster_spreads.sort(key=lambda x: x[1], reverse=True)
    
    for i, dist, c in cluster_spreads[:5]:
        title = c[0].get('title_kr') or c[0].get('title')
        countries = list({a['country_code'] for a in c})
        print(f"   - [Spread: {dist:.4f}] {title} ({len(c)} arts, {', '.join(countries)})")

    print("\n🏆 Top 5 Megatopics:")
    megatopics.sort(key=len, reverse=True)
    for i, c in enumerate(megatopics[:5]):
        countries = list({a['country_code'] for a in c})
        title = c[0].get('title_kr') or c[0].get('title')
        print(f"{i+1}. [{len(c)} arts] {title} ({', '.join(countries)})")
        
    print("\n🗑 Sample Singleton National Topics (Potential Noise):")
    # Find singletons
    singleton_clusters = [c for c in national_topics if len(c) == 1]
    for c in singleton_clusters[:5]:
        a = c[0]
        print(f"- [{a['country_code']}] {a.get('title_kr') or a.get('title')}")

if __name__ == "__main__":
    main()
