import os
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path
# from sklearn.metrics.pairwise import cosine_similarity

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

def cosine_similarity_manual(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return dot_product / (norm_v1 * norm_v2)

import json

def analyze_duplicates():
    print("Fetching recent topics...")
    # Fetch topics from last 48 hours
    # We need embeddings to do semantic check
    res = supabase.table("mvp_topics") \
        .select("id, title, title_kr, date, centroid_embedding, country_count") \
        .order("id", desc=True) \
        .limit(200) \
        .execute()
        
    topics = res.data
    print(f"Fetched {len(topics)} topics.")
    
    # Parse embeddings
    valid_topics = []
    for t in topics:
        if t['centroid_embedding']:
            if isinstance(t['centroid_embedding'], str):
                try:
                    t['centroid_embedding'] = json.loads(t['centroid_embedding'])
                    valid_topics.append(t)
                except:
                    pass
            else:
                valid_topics.append(t)
                
    print(f"Topics with embeddings: {len(valid_topics)}")
    
    if not valid_topics:
        print("No embeddings found. Cannot check semantic similarity.")
        return

    embeddings = np.array([t['centroid_embedding'] for t in valid_topics])
    ids = [t['id'] for t in valid_topics]
    titles = [t['title'] for t in valid_topics]
    
    print("Calculating similarity matrix...")
    # sim_matrix = cosine_similarity(embeddings)
    
    # Threshold for "Duplicate"
    THRESHOLD = 0.90
    
    duplicates = []
    visited = set()
    
    for i in range(len(valid_topics)):
        if i in visited: continue
        
        group = [valid_topics[i]]
        visited.add(i)
        
        for j in range(i + 1, len(valid_topics)):
            if j in visited: continue
            
            sim = cosine_similarity_manual(embeddings[i], embeddings[j])
            
            if sim >= THRESHOLD:
                group.append(valid_topics[j])
                visited.add(j)
                
        if len(group) > 1:
            duplicates.append(group)
            
    print(f"\nFound {len(duplicates)} groups of potential duplicates (Threshold {THRESHOLD}):")
    
    for group in duplicates:
        print("\n--- Duplicate Group ---")
        # Sort by ID desc (newest first)
        group.sort(key=lambda x: x['id'], reverse=True)
        for t in group:
            print(f"[{t['id']}] {t['date']} | {t['title'][:50]}... | KR: {t['title_kr'][:30] if t['title_kr'] else ''}")

if __name__ == "__main__":
    analyze_duplicates()
