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

if not url or not key:
    print("❌ Environment variables missing in backend/.env")
    exit(1)

supabase = create_client(url, key)

print(f"Checking Supabase: {url}")

# Check Megatopics
print("\n🌍 Checking Recent Megatopics (Last 24h)...")
time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()
try:
    response = supabase.table("mvp2_megatopics").select("id, name, created_at, total_articles").gte("created_at", time_threshold).order("created_at", desc=True).limit(5).execute()
    if response.data:
        print(f"✅ Found {len(response.data)} recent megatopics.")
        for item in response.data:
            print(f"  - [{item['created_at']}] {item['name']} ({item['total_articles']} articles)")
    else:
        print("❌ No recent megatopics found.")
        # Check total count
        count = supabase.table("mvp2_megatopics").select("id", count="exact").execute()
        print(f"  Total megatopics in DB: {count.count}")

except Exception as e:
    print(f"❌ Error checking megatopics: {e}")

# Check Local Topics (KR)
print("\n🇰🇷 Checking Recent Local Topics (KR, Last 24h)...")
try:
    response = supabase.table("mvp2_topics").select("id, topic_name, created_at, article_count").eq("country_code", "KR").gte("created_at", time_threshold).order("created_at", desc=True).limit(5).execute()
    if response.data:
        print(f"✅ Found {len(response.data)} recent local topics.")
        for item in response.data:
            print(f"  - [{item['created_at']}] {item['topic_name']} ({item['article_count']} articles)")
    else:
        print("❌ No recent local topics found.")
        count = supabase.table("mvp2_topics").select("id", count="exact").eq("country_code", "KR").execute()
        print(f"  Total KR topics in DB: {count.count}")

except Exception as e:
    print(f"❌ Error checking local topics: {e}")
