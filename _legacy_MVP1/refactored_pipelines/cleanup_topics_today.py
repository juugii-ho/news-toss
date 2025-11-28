import os
import sys
from datetime import datetime, timezone
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

# Load environment
root_dir = Path(__file__).resolve().parents[0]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TARGET_DATE = "2025-11-27"

def cleanup():
    print(f"Cleaning up topics for {TARGET_DATE}...")
    
    # 1. Get topic IDs
    response = supabase.table("mvp_topics").select("id").eq("date", TARGET_DATE).execute()
    topic_ids = [row['id'] for row in response.data]
    
    if not topic_ids:
        print("No topics found.")
        return

    print(f"Found {len(topic_ids)} topics.")
    
    # 2. Unlink articles (set topic_id to NULL)
    # Batch update to avoid timeouts
    batch_size = 100
    for i in range(0, len(topic_ids), batch_size):
        batch = topic_ids[i:i+batch_size]
        supabase.table("mvp_articles").update({"topic_id": None}).in_("topic_id", batch).execute()
        print(f"  Unlinked articles for batch {i//batch_size + 1}")

    # 3. Delete from mvp_topic_country_stats
    for i in range(0, len(topic_ids), batch_size):
        batch = topic_ids[i:i+batch_size]
        supabase.table("mvp_topic_country_stats").delete().in_("topic_id", batch).execute()
        print(f"  Deleted stats batch {i//batch_size + 1}")

    # 4. Delete topics
    for i in range(0, len(topic_ids), batch_size):
        batch = topic_ids[i:i+batch_size]
        supabase.table("mvp_topics").delete().in_("id", batch).execute()
        print(f"  Deleted topics batch {i//batch_size + 1}")
        
    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup()
