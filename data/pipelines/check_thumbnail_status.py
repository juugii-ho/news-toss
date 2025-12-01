
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('backend/.env')

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(url, key)

print("--- 🔍 Checking Thumbnails for Published Topics ---")
res = supabase.table("mvp2_topics")\
    .select("id, topic_name, thumbnail_url, created_at")\
    .eq("is_published", True)\
    .execute()

total = len(res.data)
missing = [t for t in res.data if not t['thumbnail_url']]

print(f"Total Published Topics: {total}")
print(f"Missing Thumbnails: {len(missing)}")

if missing:
    print("\nSample topics missing thumbnails:")
    for t in missing[:5]:
        print(f"  - {t['topic_name']} (Created: {t['created_at']})")
else:
    print("\n✅ All published topics have thumbnails.")
