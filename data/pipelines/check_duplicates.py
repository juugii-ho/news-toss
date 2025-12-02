import os
from collections import Counter
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_duplicates():
    print("--- Checking for Duplicate Topics (Last 48h) ---")
    time_threshold = (datetime.utcnow() - timedelta(hours=48)).isoformat()
    
    response = supabase.table("mvp2_topics")\
        .select("id, topic_name, country_code, created_at, thumbnail_url, is_published")\
        .gte("created_at", time_threshold)\
        .order("created_at", desc=True)\
        .execute()
        
    topics = response.data
    print(f"Total topics in last 48h: {len(topics)}")
    
    name_counts = Counter([t['topic_name'] for t in topics])
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    
    print(f"Topics with duplicates: {len(duplicates)}")
    
    if duplicates:
        print("\nSample Duplicates:")
        for name in list(duplicates.keys())[:5]:
            print(f"Topic: {name}")
            matches = [t for t in topics if t['topic_name'] == name]
            for m in matches:
                print(f"  - ID: {m['id']}")
                print(f"    Created: {m['created_at']}")
                print(f"    Published: {m['is_published']}")
                print(f"    Thumbnail: {m['thumbnail_url']}")
            print("-" * 20)

if __name__ == "__main__":
    check_duplicates()
