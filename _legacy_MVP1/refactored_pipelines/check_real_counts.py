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

def check_real_counts():
    topic_ids = [1220, 1287, 1354, 1568]
    print(f"Checking real article counts for topics: {topic_ids}")
    
    for tid in topic_ids:
        res = supabase.table("mvp_articles").select("id", count="exact").eq("topic_id", tid).execute()
        print(f"Topic {tid}: {res.count} articles (in mvp_articles)")
        
        # Also check stats to see the discrepancy
        res_stats = supabase.table("mvp_topic_country_stats").select("*").eq("topic_id", tid).execute()
        stats_count = sum(s['supportive_count'] + s['factual_count'] + s['critical_count'] for s in res_stats.data)
        print(f"Topic {tid}: {stats_count} articles (in mvp_topic_country_stats)")
        print("-" * 20)

if __name__ == "__main__":
    check_real_counts()
