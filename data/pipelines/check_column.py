import os
from supabase import create_client

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

try:
    # There is no direct way to list tables via client usually, but we can try to guess or check known ones.
    # Or we can try to query information_schema if we had SQL access.
    # Since we don't, let's just check if 'mvp2_topics' has 'global_topic_id' by trying to select it explicitly.
    
    response = supabase.table("mvp2_topics").select("global_topic_id").limit(1).execute()
    print("Select global_topic_id result:", response)

except Exception as e:
    print(f"Error: {e}")
