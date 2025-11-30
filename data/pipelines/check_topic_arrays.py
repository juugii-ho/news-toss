import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase = create_client(url, key)

def check_topic_arrays():
    try:
        print("Checking mvp2_topics article_ids...")
        res = supabase.table("mvp2_topics").select("id, article_ids").not_.is_("article_ids", "null").limit(5).execute()
        for item in res.data:
            print(f"Topic {item['id']}: {len(item.get('article_ids', []))} articles")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_topic_arrays()
