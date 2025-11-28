import os
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

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

def check_topic_embeddings():
    print("Checking mvp_topics for missing embeddings...")
    
    # Count total topics
    res_total = supabase.table("mvp_topics").select("id", count="exact").execute()
    total = res_total.count
    
    # Count topics with NULL embedding
    res_null = supabase.table("mvp_topics").select("id", count="exact").is_("centroid_embedding", "null").execute()
    null_count = res_null.count
    
    print(f"Total Topics: {total}")
    print(f"Topics with NULL embedding: {null_count}")
    
    # Debug: List latest 5 topics to check date format
    print("\nLatest 5 topics in DB:")
    res_latest = supabase.table("mvp_topics").select("id, title, date, centroid_embedding").order("id", desc=True).limit(5).execute()
    for t in res_latest.data:
        has_emb = "YES" if t['centroid_embedding'] else "NO"
        print(f"- [{t['id']}] {t['date']} | Emb: {has_emb} | {t['title'][:50]}...")

if __name__ == "__main__":
    check_topic_embeddings()
