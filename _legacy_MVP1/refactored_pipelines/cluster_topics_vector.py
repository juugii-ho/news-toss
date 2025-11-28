import json
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
from utils import get_supabase_client, get_logger

# Initialize logger
logger = get_logger(__name__)

def fetch_all_articles_with_embeddings():
    """Fetches all articles that have an embedding from Supabase, handling pagination."""
    logger.info("Fetching all articles with embeddings from Supabase...")
    supabase = get_supabase_client()
    all_articles = []
    offset = 0
    BATCH_SIZE = 1000
    
    while True:
        try:
            response = supabase.table("mvp_articles").select("*").not_.is_("embedding", "null").range(offset, offset + BATCH_SIZE - 1).execute()
            batch = response.data
            if not batch:
                break
            
            # Ensure embedding is a list of floats
            for art in batch:
                if isinstance(art.get('embedding'), str):
                    art['embedding'] = json.loads(art['embedding'])
            
            all_articles.extend(batch)
            logger.info(f"Fetched {len(all_articles)} articles so far...")
            offset += BATCH_SIZE
        except Exception as e:
            logger.error(f"Failed to fetch batch starting at offset {offset}: {e}", exc_info=True)
            break
            
    logger.info(f"Total articles with embeddings fetched: {len(all_articles)}")
    return all_articles

def cluster_within_group(articles, threshold=0.60):
    """Clusters articles within a group using cosine similarity."""
    if not articles:
        return [], []
    
    embeddings = np.array([a['embedding'] for a in articles])
    clusters = []
    centroids = []
    assigned = [False] * len(articles)
    
    for i in range(len(articles)):
        if assigned[i]:
            continue
        
        current_cluster = [articles[i]]
        assigned[i] = True
        
        for j in range(i + 1, len(articles)):
            if assigned[j]:
                continue
            
            sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
            if sim >= threshold:
                current_cluster.append(articles[j])
                assigned[j] = True
        
        clusters.append(current_cluster)
        cluster_embeddings = np.array([a['embedding'] for a in current_cluster])
        centroids.append(np.mean(cluster_embeddings, axis=0))
        
    return clusters, centroids

def cluster_articles_vector(articles, national_threshold=0.60, global_threshold=0.85):
    """Performs a two-stage vector clustering on articles."""
    if not articles:
        logger.warning("No articles provided for clustering.")
        return []

    logger.info(f"Starting two-stage clustering on {len(articles)} articles...")
    
    # Stage 1: Cluster within each country
    logger.info(f"Stage 1: Clustering within countries (Threshold: {national_threshold})")
    country_groups = defaultdict(list)
    for art in articles:
        country_groups[art['country_code']].append(art)
        
    national_topics = []
    for country_code, group in country_groups.items():
        sub_clusters, sub_centroids = cluster_within_group(group, threshold=national_threshold)
        for i, sub_cluster in enumerate(sub_clusters):
            national_topics.append({
                "centroid": sub_centroids[i],
                "articles": sub_cluster,
                "country": country_code
            })
    logger.info(f"  -> Found {len(national_topics)} national topics.")
    
    # Stage 2: Cluster national topics globally
    if not national_topics:
        logger.warning("No national topics found, aborting Stage 2.")
        return []

    logger.info(f"Stage 2: Clustering national topics globally (Threshold: {global_threshold})")
    topic_embeddings = np.array([t['centroid'].tolist() for t in national_topics])
    final_clusters = []
    assigned_topics = [False] * len(national_topics)
    
    for i in range(len(national_topics)):
        if assigned_topics[i]:
            continue
        
        current_global_cluster_articles = list(national_topics[i]['articles'])
        assigned_topics[i] = True
        
        for j in range(i + 1, len(national_topics)):
            if assigned_topics[j]:
                continue
            
            sim = cosine_similarity([topic_embeddings[i]], [topic_embeddings[j]])[0][0]
            if sim >= global_threshold:
                current_global_cluster_articles.extend(national_topics[j]['articles'])
                assigned_topics[j] = True
                
        final_clusters.append(current_global_cluster_articles)
        
    logger.info(f"Clustering complete. Found {len(final_clusters)} final clusters.")
    return final_clusters

def save_clusters_to_json(clusters, filename="clustered_topics_vector.json"):
    """Saves the final clusters to a JSON file in the outputs directory."""
    if not clusters:
        logger.warning("No clusters to save.")
        return

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'outputs'))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    # Convert numpy arrays to lists for JSON serialization
    for cluster in clusters:
        for article in cluster:
            if 'centroid' in article and isinstance(article['centroid'], np.ndarray):
                article['centroid'] = article['centroid'].tolist()
            if 'embedding' in article and isinstance(article['embedding'], np.ndarray):
                article['embedding'] = article['embedding'].tolist()

    try:
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(clusters, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(clusters)} clusters to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save clusters to JSON: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("Starting vector clustering pipeline...")
    articles_with_embeddings = fetch_all_articles_with_embeddings()
    
    if articles_with_embeddings:
        final_topic_clusters = cluster_articles_vector(articles_with_embeddings)
        save_clusters_to_json(final_topic_clusters)
    else:
        logger.warning("No articles with embeddings found to process.")
        
    logger.info("Vector clustering pipeline finished.")