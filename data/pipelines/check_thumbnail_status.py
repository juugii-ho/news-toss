import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("backend/.env")
load_dotenv(".env.local")
load_dotenv(".env")

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase: Client = create_client(url, key)

def check_status():
    # Count total topics
    res_total = supabase.from_("mvp2_topics").select("id", count="exact").execute()
    total_count = res_total.count

    # Count topics with thumbnails
    res_done = supabase.from_("mvp2_topics").select("id", count="exact").not_.is_("thumbnail_url", "null").execute()
    done_count = res_done.count

    # Count topics needing thumbnails
    res_pending = supabase.from_("mvp2_topics").select("id", count="exact").is_("thumbnail_url", "null").execute()
    pending_count = res_pending.count

    print(f"Total Topics: {total_count}")
    print(f"Thumbnails Created: {done_count}")
    print(f"Thumbnails Needed: {pending_count}")

if __name__ == "__main__":
    check_status()
