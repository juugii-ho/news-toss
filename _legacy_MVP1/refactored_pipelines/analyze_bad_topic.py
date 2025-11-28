import os
import json
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path
from collections import Counter

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

def analyze_topic():
    # Search for the topic by Korean title fragment
    search_term = "2025년 예산"
    print(f"Searching for topic containing: '{search_term}'...")
    
    res = supabase.table("mvp_topics") \
        .select("*") \
        .ilike("title_kr", f"%{search_term}%") \
        .execute()
        
    topics = res.data
    if not topics:
        print("Topic not found. Trying English search 'Budget 2025'...")
        res = supabase.table("mvp_topics") \
            .select("*") \
            .ilike("title", "%Budget 2025%") \
            .execute()
        topics = res.data
        
    if not topics:
        print("Topic not found.")
        return

    topic = topics[0]
    print(f"\nFOUND TOPIC: [{topic['id']}] {topic['title_kr']}")
    print(f"Original Title: {topic['title']}")
    print(f"Date: {topic['date']}")
    print(f"Country Count: {topic['country_count']}")
    
    # Fetch stats to see country distribution
    print("\n--- Country Distribution ---")
    stats_res = supabase.table("mvp_topic_country_stats") \
        .select("country_code, supportive_count, factual_count, critical_count") \
        .eq("topic_id", topic['id']) \
        .execute()
        
    total_articles = 0
    for s in stats_res.data:
        count = s['supportive_count'] + s['factual_count'] + s['critical_count']
        total_articles += count
        print(f"{s['country_code']}: {count} articles")
        
    print(f"\nTotal Articles (from stats): {total_articles}")
    
    # Fetch sample articles
    print("\n--- Sample Articles (Top 30) ---")
    articles_res = supabase.table("mvp_articles") \
        .select("id, title, country_code, source") \
        .eq("topic_id", topic['id']) \
        .limit(30) \
        .execute()
        
    for a in articles_res.data:
        print(f"[{a['country_code']}] {a['title']} ({a['source']})")
        
    print("\n--- Checking Adjacent Topics ---")
    adj_ids = [topic['id'] - 1, topic['id'] + 1]
    adj_res = supabase.table("mvp_topics").select("id, title, title_kr").in_("id", adj_ids).execute()
    for t in adj_res.data:
        print(f"[{t['id']}] EN: {t['title']}")
        print(f"       KR: {t['title_kr']}")

if __name__ == "__main__":
    analyze_topic()
