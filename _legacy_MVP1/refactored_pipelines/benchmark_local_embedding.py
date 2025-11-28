import json
import time
import numpy as np
import os
from collections import Counter
from datetime import datetime

# Try to import sentence_transformers
try:
    from sentence_transformers import SentenceTransformer
    import torch
except ImportError:
    print("Error: sentence-transformers not installed.")
    print("Please run: pip install sentence-transformers torch")
    exit(1)

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def cluster_articles_vector(articles, embeddings, threshold=0.75):
    """
    Cluster articles based on pre-computed embeddings.
    """
    print(f"Clustering {len(articles)} articles...")
    start_time = time.time()
    
    clusters = [] # List of lists of indices
    cluster_centroids = [] # List of centroid vectors
    
    for i, vec in enumerate(embeddings):
        best_sim = -1
        best_idx = -1
        
        # Find best matching cluster
        for j, centroid in enumerate(cluster_centroids):
            sim = cosine_similarity(vec, centroid)
            if sim > best_sim:
                best_sim = sim
                best_idx = j
        
        # Assign to cluster or create new one
        if best_sim >= threshold:
            clusters[best_idx].append(i)
            # Update centroid (simple average)
            # Optimization: Moving average or re-calculate? 
            # For speed in benchmark, let's just keep the old centroid or do a quick update.
            # Correct way: new_centroid = (old_centroid * N + new_vec) / (N + 1)
            n = len(clusters[best_idx])
            cluster_centroids[best_idx] = (cluster_centroids[best_idx] * (n-1) + vec) / n
        else:
            clusters.append([i])
            cluster_centroids.append(vec)
            
    print(f"Clustering took {time.time() - start_time:.2f} seconds.")
    return clusters

def run_benchmark():
    # 1. Load Data
    # Resolve path relative to this script (data/pipelines/benchmark_local_embedding.py -> root)
    from pathlib import Path
    root_dir = Path(__file__).resolve().parents[2]
    
    input_file = root_dir / "translated_articles.json"
    if not input_file.exists():
        # Fallback to current dir
        input_file = Path("translated_articles.json")
    
    if not input_file.exists():
        print(f"{input_file} not found. Run translate_articles.py first.")
        return

    with open(input_file, "r") as f:
        articles = json.load(f)
    
    print(f"Loaded {len(articles)} articles.")
    
    # 2. Setup Model (Local GPU/MPS)
    model_name = 'all-MiniLM-L6-v2' # Fast & Good
    print(f"Loading local model: {model_name}...")
    
    device = 'cpu'
    if torch.backends.mps.is_available():
        device = 'mps'
        print("Using MPS (Apple Silicon GPU) acceleration! 🚀")
    elif torch.cuda.is_available():
        device = 'cuda'
        print("Using CUDA GPU acceleration! 🚀")
    else:
        print("Using CPU (might be slower).")
        
    model = SentenceTransformer(model_name, device=device)
    
    # 3. Generate Embeddings
    print("Generating embeddings locally...")
    start_time = time.time()
    
    # Prepare texts (English Titles)
    texts = [a.get('title_en', a['title']) for a in articles]
    
    embeddings = model.encode(texts, batch_size=64, show_progress_bar=True)
    
    print(f"Embedding took {time.time() - start_time:.2f} seconds.")
    
    # 4. Cluster
    # Note: Local embeddings might have different scale/distribution than Gemini.
    # We might need to tune threshold. Let's try 0.75 first (same as Gemini).
    # Cosine similarity is scale-invariant, but distribution matters.
    clusters_indices = cluster_articles_vector(articles, embeddings, threshold=0.60) # Lower threshold for MiniLM usually
    
    print(f"Found {len(clusters_indices)} clusters.")
    
    # 5. Analyze Results
    clusters = [[articles[i] for i in indices] for indices in clusters_indices]
    clusters.sort(key=len, reverse=True)
    
    print("\n--- Top 5 Clusters (Local Model) ---")
    for i, cluster in enumerate(clusters[:5]):
        countries = set(a['country_code'] for a in cluster)
        print(f"\nCluster {i+1} (Size: {len(cluster)}, Countries: {len(countries)} - {countries})")
        # Display Korean title for readability (fallback to original)
        print(f"Title: {cluster[0].get('title_kr', cluster[0]['title'])}")
        for a in cluster[:3]:
            print(f"  - [{a['country_code']}] {a.get('title_kr', a['title'])}")

if __name__ == "__main__":
    run_benchmark()
