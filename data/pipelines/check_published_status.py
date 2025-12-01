import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_published_status():
    print("Checking published topics...")
    
    # 1. Check count of published topics
    res = supabase.table("mvp2_topics").select("id", count="exact").eq("is_published", True).execute()
    print(f"Published Topics Count: {res.count}")
    
    # 2. Check latest batch_id
    res = supabase.table("mvp2_topics").select("batch_id, created_at").order("created_at", desc=True).limit(1).execute()
    if res.data:
        latest = res.data[0]
        print(f"Latest Topic Created At: {latest['created_at']}")
        print(f"Latest Topic Batch ID: {latest['batch_id']}")
        
        # Check if this batch is published
        res_batch = supabase.table("mvp2_topics").select("is_published", count="exact").eq("batch_id", latest['batch_id']).eq("is_published", True).execute()
        print(f"Is Latest Batch Published? Count: {res_batch.count}")
    else:
        print("No topics found.")

if __name__ == "__main__":
    check_published_status()
