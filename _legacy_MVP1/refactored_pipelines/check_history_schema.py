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

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Try to insert a dummy record to get schema error or just guess
# Actually, let's just try to select * and print keys if empty
# Since it's empty, we can't get keys from data.
# We can try to inspect via a known method or just assume standard fields.
# Let's try to select specific fields we expect and see if they error.

expected_fields = ["id", "topic_id", "date", "article_count", "centroid_embedding", "country_count"]

print("Checking fields...")
for field in expected_fields:
    try:
        supabase.table("mvp_topic_history").select(field).limit(1).execute()
        print(f"Field '{field}' exists.")
    except Exception as e:
        print(f"Field '{field}' ERROR: {e}")
