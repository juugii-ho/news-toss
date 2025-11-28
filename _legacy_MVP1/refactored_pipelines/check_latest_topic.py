import os
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

# Load env
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("Supabase credentials missing.")
    exit(1)

supabase = create_client(url, key)

# Get latest topic
response = supabase.table("mvp_topics").select("*").order("created_at", desc=True).limit(1).execute()

if response.data:
    topic = response.data[0]
    print(f"Latest Topic ID: {topic['id']}")
    print(f"Title (EN): {topic['title']}")
    print(f"Title (KR): {topic.get('title_kr')}")
    print(f"Created At: {topic['created_at']}")
    print(f"Summary: {topic.get('summary')}")
else:
    print("No topics found in DB.")
