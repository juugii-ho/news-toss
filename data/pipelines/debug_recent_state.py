import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

# Load environment
load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def inspect_topics():
    print("--- Inspecting Recent Topics (Last 24h) ---")
    time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    
    # Fetch all topics created in last 24h
    response = supabase.table("mvp2_topics")\
        .select("*")\
        .gte("created_at", time_threshold)\
        .execute()
        
    topics = response.data
    print(f"Total topics created in last 24h: {len(topics)}")
    
    if not topics:
        return

    published_count = sum(1 for t in topics if t.get('is_published'))
    missing_batch = sum(1 for t in topics if not t.get('batch_id'))
    missing_thumb = sum(1 for t in topics if not t.get('thumbnail_url'))
    missing_summary = sum(1 for t in topics if not t.get('summary'))
    
    print(f"Published: {published_count}")
    print(f"Missing Batch ID: {missing_batch}")
    print(f"Missing Thumbnail: {missing_thumb}")
    print(f"Missing Summary: {missing_summary}")
    
    print("\n--- Sample of Problematic Topics (Published but missing data) ---")
    problematic = [t for t in topics if t.get('is_published') and (not t.get('batch_id') or not t.get('thumbnail_url') or not t.get('summary'))]
    
    for t in problematic[:5]:
        print(f"ID: {t['id']}")
        print(f"  Name: {t.get('topic_name')}")
        print(f"  Created: {t.get('created_at')}")
        print(f"  Published: {t.get('is_published')}")
        print(f"  Batch ID: {t.get('batch_id')}")
        print(f"  Thumbnail: {t.get('thumbnail_url')}")
        print(f"  Summary: {t.get('summary')[:50] if t.get('summary') else 'None'}")
        print("-" * 20)

    print("\n--- Checking for Old Topics (Created < 24h ago) ---")
    # Just show total count of topics created before 24h ago
    response_old = supabase.table("mvp2_topics")\
        .select("id", count="exact")\
        .lt("created_at", time_threshold)\
        .execute()
        
    print(f"Total old topics: {response_old.count}")

if __name__ == "__main__":
    inspect_topics()
