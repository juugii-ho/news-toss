import os
import json
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Service Role for deletion

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def cosine_similarity_manual(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0: return 0
    return dot_product / (norm_v1 * norm_v2)

def cleanup_duplicates():
    # Fetch recent topics with embeddings
    # Increased limit to 2000 to catch older duplicates
    response = supabase.table("mvp_topics") \
        .select("id, title, centroid_embedding, created_at") \
        .order("id", desc=True) \
        .limit(2000) \
        .execute()
        
    topics = response.data
    
    # Parse embeddings and fetch article counts
    valid_topics = []
    print(f"Fetched {len(topics)} topics. Fetching article counts...")
    
    for t in topics:
        if not t.get('centroid_embedding'): continue
        
        try:
            # Parse embedding
            if isinstance(t['centroid_embedding'], str):
                t['centroid_embedding'] = json.loads(t['centroid_embedding'])
            
            # Fetch article count
            res = supabase.table("mvp_articles").select("id", count="exact").eq("topic_id", t['id']).execute()
            t['article_count'] = res.count
            
            valid_topics.append(t)
        except Exception as e:
            print(f"Error processing topic {t['id']}: {e}")
            continue

                
    print(f"Topics with embeddings: {len(valid_topics)}")
    
    embeddings = np.array([t['centroid_embedding'] for t in valid_topics])
    
    THRESHOLD = 0.85 # Lowered to catch looser matches
    
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
            
    print(f"\nFound {len(duplicates)} groups of duplicates.")
    
    total_deleted = 0
    
    for group in duplicates:
        # Check article counts for each
        group_ids = [t['id'] for t in group]
        
        # We can't easily check article counts in one query for all, so loop
        # Or just assume the latest one is the winner if we know the others are ghosts?
        # Let's verify counts to be safe.
        
        candidates = []
        for t in group:
            res_count = supabase.table("mvp_articles").select("id", count="exact").eq("topic_id", t['id']).execute()
            count = res_count.count
            candidates.append({**t, "article_count": count})
            
        # Sort by article_count desc, then id desc
        candidates.sort(key=lambda x: (x['article_count'], x['id']), reverse=True)
        
        winner = candidates[0]
        losers = candidates[1:]
        
        print(f"\nGroup: {[c['title'][:30] for c in candidates]}")
        print(f"Winner: [{winner['id']}] (Articles: {winner['article_count']})")
        
        loser_ids = [l['id'] for l in losers]
        if not loser_ids: continue
        
        print(f"Deleting Losers: {loser_ids} (Articles: {[l['article_count'] for l in losers]})")
        
        # Double check: if a loser has articles, we should move them?
        # But based on our finding, they have 0.
        # If they have articles, we should move them to winner.
        
        for l in losers:
            if l['article_count'] > 0:
                print(f"  -> Moving {l['article_count']} articles from {l['id']} to {winner['id']}...")
                supabase.table("mvp_articles").update({"topic_id": winner['id']}).eq("topic_id", l['id']).execute()
        
        # Delete stats
        supabase.table("mvp_topic_country_stats").delete().in_("topic_id", loser_ids).execute()
        
        # Delete history
        supabase.table("mvp_topic_history").delete().in_("topic_id", loser_ids).execute()
        
        # Delete topics
        supabase.table("mvp_topics").delete().in_("id", loser_ids).execute()
        
        total_deleted += len(loser_ids)
        
    print(f"\nTotal deleted topics: {total_deleted}")

if __name__ == "__main__":
    cleanup_duplicates()
