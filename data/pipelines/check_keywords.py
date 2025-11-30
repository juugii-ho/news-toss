import os
from dotenv import load_dotenv
from supabase import create_client

# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
load_dotenv(os.path.join(project_root, 'backend', '.env'))

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(url, key)

from datetime import datetime, timedelta

# Calculate 24 hours ago
time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()

print("Checking remaining untagged topics (KR, Last 24h)...")
response = supabase.table("mvp2_topics") \
    .select("id", count="exact") \
    .eq("country_code", "KR") \
    .gte("created_at", time_threshold) \
    .is_("keywords", "null") \
    .execute()

print(f"Remaining untagged topics: {response.count}")

if response.count > 0:
    print("Listing first 5:")
    data = supabase.table("mvp2_topics").select("topic_name").eq("country_code", "KR").gte("created_at", time_threshold).is_("keywords", "null").limit(5).execute()
    for row in data.data:
        print(f"  - {row['topic_name']}")
