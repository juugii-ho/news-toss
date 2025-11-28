import os
import json
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path
from collections import defaultdict

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

def cleanup_all_duplicates():
    print("Fetching ALL recent topics (limit 2000)...")
    res = supabase.table("mvp_topics") \
        .select("id, title, centroid_embedding, created_at") \
        .order("id", desc=True) \
        .limit(2000) \
        .execute()
        
    topics = res.data
    print(f"Fetched {len(topics)} topics.")
    
    # 1. Exact Title Deduplication
    print("\n--- Phase 1: Exact Title Match ---")
    title_map = defaultdict(list)
    for t in topics:
        title_map[t['title']].append(t)
        
    duplicates_by_title = [group for group in title_map.values() if len(group) > 1]
    print(f"Found {len(duplicates_by_title)} groups with identical titles.")
    
    process_duplicates(duplicates_by_title)
    
    # Refresh topics after Phase 1
    # Actually, we can just filter out deleted ones from memory, but safer to re-fetch or just proceed with remaining?
    # Let's proceed with Phase 2 on the *remaining* IDs.
    # But for simplicity, let's just run Phase 1 first, then maybe Phase 2 in a separate run or re-fetch.
    # Let's do Phase 2 (Semantic) on the *winners* of Phase 1 + unique titles.
    
    # For now, let's just do Phase 1 and see. The user's examples were mostly identical titles.
    
def process_duplicates(groups):
    total_deleted = 0
    
    for group in groups:
        # Check article counts
        candidates = []
        for t in group:
            res_count = supabase.table("mvp_articles").select("id", count="exact").eq("topic_id", t['id']).execute()
            count = res_count.count
            candidates.append({**t, "article_count": count})
            
        # Sort by article_count desc, then id desc (prefer newer if counts equal? or older? usually newer is better)
        # Actually, if counts are equal, keep the one with more metadata?
        # Let's keep the one with the MOST articles.
        candidates.sort(key=lambda x: (x['article_count'], x['id']), reverse=True)
        
        winner = candidates[0]
        losers = candidates[1:]
        
        if not losers: continue
        
        print(f"\nGroup: '{winner['title'][:50]}...'")
        print(f"Winner: [{winner['id']}] (Articles: {winner['article_count']})")
        print(f"Losers: {[l['id'] for l in losers]} (Articles: {[l['article_count'] for l in losers]})")
        
        loser_ids = [l['id'] for l in losers]
        
        # Move articles
        for l in losers:
            if l['article_count'] > 0:
                print(f"  -> Moving {l['article_count']} articles from {l['id']} to {winner['id']}...")
                supabase.table("mvp_articles").update({"topic_id": winner['id']}).eq("topic_id", l['id']).execute()
        
        # Delete stats & history & topics
        supabase.table("mvp_topic_country_stats").delete().in_("topic_id", loser_ids).execute()
        supabase.table("mvp_topic_history").delete().in_("topic_id", loser_ids).execute()
        supabase.table("mvp_topics").delete().in_("id", loser_ids).execute()
        
        total_deleted += len(loser_ids)
        
    print(f"\nTotal deleted topics: {total_deleted}")

if __name__ == "__main__":
    cleanup_all_duplicates()
