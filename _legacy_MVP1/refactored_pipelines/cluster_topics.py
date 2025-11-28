import json
from collections import defaultdict
import re

def normalize_title(title):
    return re.sub(r'[^\w\s]', '', title.lower())

def cluster_articles(articles):
    """
    Simple clustering based on shared words in titles.
    For MVP, this is a placeholder for a more robust embedding-based clustering.
    """
    clusters = []
    # simplistic O(N^2) clustering for MVP demo
    # In production, use embeddings (e.g. OpenAI text-embedding-3-small) + DBSCAN/KMeans
    
    used_indices = set()
    
    for i, article in enumerate(articles):
        if i in used_indices:
            continue
            
        current_cluster = [article]
        used_indices.add(i)
        
        # Basic English stopwords (can be expanded)
        STOPWORDS = {'the', 'a', 'an', 'in', 'on', 'at', 'for', 'to', 'of', 'and', 'or', 'is', 'are', 'was', 'were', 'be', 'has', 'have', 'had', 'it', 'that', 'this', 'from', 'by', 'with', 'as', 'about', 'after', 'before', 'over', 'under', 'up', 'down', 'out', 'off', 'not', 'no', 'new', 'us', 'uk', 'says', 'said', 'will', 'would', 'could', 'should', 'can', 'may', 'might'}
        
        title_words = set(normalize_title(article['title']).split()) - STOPWORDS
        
        for j, other_article in enumerate(articles):
            if j in used_indices:
                continue
                
            other_words = set(normalize_title(other_article['title']).split()) - STOPWORDS
            common = title_words.intersection(other_words)
            
            # If enough common words (excluding stop words), group them
            if len(common) >= 2: # Lower threshold slightly since we removed stopwords
                current_cluster.append(other_article)
                used_indices.add(j)
        
        if len(current_cluster) > 1:
            clusters.append(current_cluster)
            
    return clusters

if __name__ == "__main__":
    try:
        with open("raw_articles.json", "r") as f:
            articles = json.load(f)
            
        clusters = cluster_articles(articles)
        print(f"Found {len(clusters)} clusters.")
        
        # Save clusters
        with open("clustered_topics.json", "w") as f:
            json.dump(clusters, f, indent=2)
            
    except FileNotFoundError:
        print("raw_articles.json not found. Run fetch_rss.py first.")
