import os
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(url, key)

# Fetch one row
res = supabase.table("mvp_topics").select("*").limit(1).execute()
if res.data:
    print("Columns:", res.data[0].keys())
else:
    print("No data found.")
