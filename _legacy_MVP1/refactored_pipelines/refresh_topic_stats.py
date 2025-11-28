import os
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

# Load environment
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def refresh_stats():
    print("Fetching all articles with scores...")
    # Fetch all articles with topic_id and stance_score
    # We need to paginate if there are many articles
    all_articles = []
    offset = 0
    BATCH_SIZE = 2000
    
    while True:
        res = supabase.table("mvp_articles") \
            .select("topic_id, stance_score") \
            .not_.is_("topic_id", "null") \
            .not_.is_("stance_score", "null") \
            .range(offset, offset + BATCH_SIZE - 1) \
            .execute()
            
        if not res.data:
            break
            
        all_articles.extend(res.data)
        offset += BATCH_SIZE
        print(f"Fetched {len(all_articles)} articles...")

    print(f"Processing {len(all_articles)} articles...")
    
    # Group by topic_id
    topic_scores = {}
    for a in all_articles:
        tid = a['topic_id']
        score = a['stance_score']
        if tid not in topic_scores:
            topic_scores[tid] = []
        topic_scores[tid].append(score)
        
    # Calculate averages
    updates = []
    for tid, scores in topic_scores.items():
        avg = sum(scores) / len(scores)
        updates.append({
            "id": tid,
            "avg_stance_score": avg
        })
        
    print(f"Prepared updates for {len(updates)} topics.")
    
    # Bulk Upsert
    # Supabase upsert requires all columns or ignore duplicates. 
    # But we only want to update avg_stance_score.
    # 'upsert' usually replaces the row if it exists. 
    # If we only provide id and avg_stance_score, other columns might be set to null/default if not careful?
    # Wait, Supabase (PostgREST) upsert with 'ignore_duplicates=False' (default) will update.
    # BUT, if we don't provide other columns, will they be erased?
    # Yes, usually upsert replaces the row.
    
    # Alternative: Use .update() but we can't bulk update different values for different IDs easily in one request.
    # We have to loop for updates?
    # Or use a stored procedure?
    
    # Actually, for 1500 topics, looping update IS the standard way if we don't have a custom RPC.
    # But we can do it faster by parallelizing or just accepting it takes 2-3 mins.
    # The previous script was stuck because of something else? Or just slow?
    # Let's try to optimize the READ part first (which I did above).
    # The WRITE part: 1500 updates.
    # Let's try to run updates in parallel threads?
    
    # Or, we can use `upsert` if we fetch the existing rows first?
    # That's too much data.
    
    # Let's stick to sequential update but with the pre-calculated data.
    # At least we save 1500 READ requests.
    
    print("Applying updates...")
    count = 0
    for up in updates:
        try:
            supabase.table("mvp_topics").update({"avg_stance_score": up['avg_stance_score']}).eq("id", up['id']).execute()
            count += 1
            if count % 50 == 0:
                print(f"Updated {count} topics...")
        except Exception as e:
            print(f"Error updating topic {up['id']}: {e}")
            
    print(f"Done. Refreshed {count} topics.")

if __name__ == "__main__":
    refresh_stats()
