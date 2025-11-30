import os
from supabase import create_client

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

try:
    response = supabase.table("mvp2_global_topic_mappings").select("*").limit(1).execute()
    if response.data:
        print("Keys in mvp2_global_topic_mappings:", response.data[0].keys())
    else:
        print("mvp2_global_topic_mappings is empty or does not exist.")

except Exception as e:
    print(f"Error: {e}")
