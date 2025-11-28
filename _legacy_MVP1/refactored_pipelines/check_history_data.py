import os
import json
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

# Load environment
root_dir = Path(__file__).resolve().parent
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_history():
    print("Checking for duplicates in recent history...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    
    response = supabase.table("mvp_topic_history")\
        .select("topic_id, date, created_at, avg_stance_score")\
        .gte("date", start_date.strftime('%Y-%m-%d'))\
        .execute()
        
    records = response.data
    if not records:
        print("No history records found.")
        return
        
    print(f"Found {len(records)} records.")
    
    # Check duplicates
    seen = {}
    duplicates = []
    for r in records:
        key = (r['topic_id'], r['date'])
        if key in seen:
            duplicates.append((key, seen[key], r))
        else:
            seen[key] = r
            
    if duplicates:
        print(f"Found {len(duplicates)} duplicates!")
        for d in duplicates[:5]:
            print(f"Duplicate: {d[0]}")
            print(f"  Existing: {d[1]['created_at']} (Score: {d[1]['avg_stance_score']})")
            print(f"  New:      {d[2]['created_at']} (Score: {d[2]['avg_stance_score']})")
    else:
        print("No duplicates found.")
        
    # Check for nulls in unique records
    null_records = [r for r in seen.values() if r['avg_stance_score'] is None]
    print(f"Records with null avg_stance_score: {len(null_records)} / {len(seen)}")
    
    if null_records:
        print("Sample NULL topics:")
        for r in null_records[:5]:
            print(f"  Topic ID: {r['topic_id']}, Date: {r['date']}")
            
        # Check if these topics have score in mvp_topics
        null_ids = [r['topic_id'] for r in null_records]
        print(f"\nChecking mvp_topics for {len(null_ids)} IDs...")
        res = supabase.table("mvp_topics").select("id, title, avg_stance_score").in_("id", null_ids).execute()
        for t in res.data:
            print(f"  Topic {t['id']}: {t['title'][:20]}... => Score: {t['avg_stance_score']}")

if __name__ == "__main__":
    check_history()
