import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("Error: Credentials not found.")
    exit(1)

supabase = create_client(url, key)

def check_links():
    try:
        print("Checking article links...")
        
        # Check articles with local_topic_id
        res_local = supabase.table("mvp2_articles").select("id", count="exact").not_.is_("local_topic_id", "null").limit(1).execute()
        print(f"Articles with local_topic_id: {res_local.count}")
        
        # Check articles with global_topic_id
        res_global = supabase.table("mvp2_articles").select("id", count="exact").not_.is_("global_topic_id", "null").limit(1).execute()
        print(f"Articles with global_topic_id: {res_global.count}")
        
        # Sample check for a specific global topic if any
        if res_global.count > 0:
             res_sample = supabase.table("mvp2_articles").select("global_topic_id").not_.is_("global_topic_id", "null").limit(1).execute()
             gid = res_sample.data[0]['global_topic_id']
             print(f"Sample Global Topic ID in articles: {gid}")
             
             # Verify if this ID exists in mvp2_global_topics (or mvp2_megatopics)
             # Note: Table name might be mvp2_megatopics based on schema, but code used mvp2_global_topics in recent edit?
             # Let's check both table names existence or just try one.
             # Schema says mvp2_megatopics. Code in step 6310 changed to mvp2_global_topics.
             # Let's check which table actually exists.
             
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_links()
