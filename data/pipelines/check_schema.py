import os
from supabase import create_client

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

try:
    # Fetch one row to inspect keys
    response = supabase.table("mvp2_global_topics").select("*").limit(1).execute()
    if response.data:
        print("Keys in mvp2_global_topics:", response.data[0].keys())
    else:
        print("mvp2_global_topics is empty.")

    response_local = supabase.table("mvp2_topics").select("*").limit(1).execute()
    if response_local.data:
        print("Keys in mvp2_topics:", response_local.data[0].keys())

except Exception as e:
    print(f"Error: {e}")
