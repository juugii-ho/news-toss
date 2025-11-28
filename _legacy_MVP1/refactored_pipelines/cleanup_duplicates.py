import os
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

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

def cleanup_topics():
    # Topics to delete
    # 1220: Ghost (0 articles)
    # 1287: Ghost (0 articles)
    # 1354: Fragment (30 articles) - we will delete the topic, articles will be orphaned (hidden)
    ids_to_delete = [1220, 1287, 1354]
    
    print(f"Deleting topics: {ids_to_delete}...")
    
    # 1. Unlink Articles (Set topic_id to NULL)
    print("Orphaning articles...")
    res_articles = supabase.table("mvp_articles").update({"topic_id": None}).in_("topic_id", ids_to_delete).execute()
    print(f"Orphaned articles count: {len(res_articles.data)}")

    # 2. Delete from mvp_topic_country_stats (Child table)
    print("Deleting stats...")
    res_stats = supabase.table("mvp_topic_country_stats").delete().in_("topic_id", ids_to_delete).execute()
    print(f"Deleted stats rows.")
    
    # 3. Delete from mvp_topics (Parent table)
    print("Deleting topics...")
    res_topics = supabase.table("mvp_topics").delete().in_("id", ids_to_delete).execute()
    print(f"Deleted topics: {len(res_topics.data)}")

if __name__ == "__main__":
    cleanup_topics()
