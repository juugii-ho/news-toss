import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
load_dotenv(os.path.join(project_root, 'backend', '.env'))

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(url, key)

print("Simulating Frontend Query for KR...")

# Calculate 24 hours ago
time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()

# Exact query from supabase-service.ts
response = supabase.table("mvp2_topics") \
    .select("*") \
    .eq("country_code", "KR") \
    .gte("created_at", time_threshold) \
    .gt("source_count", 1) \
    .order("source_count", desc=True) \
    .order("article_count", desc=True) \
    .limit(20) \
    .execute()

print(f"Fetched {len(response.data)} topics.")

for i, row in enumerate(response.data):
    keywords = row.get('keywords')
    topic_name = row.get('topic_name')
    print(f"[{i+1}] {topic_name[:30]}...")
    print(f"    Keywords: {keywords} (Type: {type(keywords)})")
    
    if not keywords or len(keywords) == 0:
        print("    ⚠️  NO KEYWORDS -> Will fallback to topic_name")
    else:
        print(f"    ✅  Will use: {keywords[0]}")
