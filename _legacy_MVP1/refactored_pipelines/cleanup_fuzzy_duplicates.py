import os
import json
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path
from difflib import SequenceMatcher

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

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def cleanup_fuzzy_duplicates():
    print("Fetching recent topics (limit 2000)...")
    response = supabase.table("mvp_topics") \
        .select("id, title, created_at") \
        .order("id", desc=True) \
        .limit(2000) \
        .execute()
        
    topics = response.data
    print(f"Fetched {len(topics)} topics.")
    
    # Fetch article counts in batch
    print("Fetching article counts (batch)...")
    topic_ids = [t['id'] for t in topics]
    
    # Initialize with 0
    for t in topics: t['article_count'] = 0
    
    # Fetch stats in chunks
    CHUNK_SIZE = 1000
    for i in range(0, len(topic_ids), CHUNK_SIZE):
        chunk = topic_ids[i:i+CHUNK_SIZE]
        res = supabase.table("mvp_topic_country_stats").select("topic_id, supportive_count, factual_count, critical_count").in_("topic_id", chunk).execute()
        
        stats = res.data
        for s in stats:
            tid = s['topic_id']
            count = (s.get('supportive_count') or 0) + (s.get('factual_count') or 0) + (s.get('critical_count') or 0)
            
            # Find topic and add count
            for t in topics:
                if t['id'] == tid:
                    t['article_count'] += count
                    break
            
    # Sort by ID desc (newest first)
    topics.sort(key=lambda x: x['id'], reverse=True)
    
    duplicates = []
    visited = set()
    
    THRESHOLD = 0.65 # Fuzzy match threshold
    
    for i in range(len(topics)):
        if i in visited: continue
        
        group = [topics[i]]
        visited.add(i)
        
        for j in range(i + 1, len(topics)):
            if j in visited: continue
            
            # Compare titles
            sim = similar(topics[i]['title'].lower(), topics[j]['title'].lower())
            
            if sim >= THRESHOLD:
                group.append(topics[j])
                visited.add(j)
                
        if len(group) > 1:
            duplicates.append(group)
            
    print(f"\nFound {len(duplicates)} groups of fuzzy duplicates.")
    
    total_deleted = 0
    
    for group in duplicates:
        # Sort by article_count desc, then id desc
        # Prefer topic with most articles. If equal, prefer newest.
        group.sort(key=lambda x: (x['article_count'], x['id']), reverse=True)
        
        winner = group[0]
        losers = group[1:]
        
        print(f"\nGroup: {[t['title'][:30] for t in group]}")
        print(f"Winner: [{winner['id']}] '{winner['title'][:50]}...' (Articles: {winner['article_count']})")
        
        loser_ids = [l['id'] for l in losers]
        print(f"Deleting Losers: {loser_ids} (Articles: {[l['article_count'] for l in losers]})")
        
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
    cleanup_fuzzy_duplicates()
