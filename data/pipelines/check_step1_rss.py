"""
Step 1 Validation: Check RSS Collection Results
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("STEP 1 VALIDATION: RSS Collection")
print("=" * 60)

# 1. Check total articles
response = supabase.table("mvp2_articles").select("*", count="exact").execute()
total = response.count
print(f"\n📊 Total Articles in DB: {total}")

# 2. Check recent articles (last 24 hours)
time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()
response = supabase.table("mvp2_articles") \
    .select("*", count="exact") \
    .gte("collected_at", time_threshold) \
    .execute()

recent_count = response.count
print(f"📅 Articles collected in last 24h: {recent_count}")

# 3. Check by country
response = supabase.table("mvp2_articles") \
    .select("country_code", count="exact") \
    .gte("collected_at", time_threshold) \
    .execute()

articles = response.data
country_counts = {}
for article in articles:
    country = article.get('country_code', 'Unknown')
    country_counts[country] = country_counts.get(country, 0) + 1

print(f"\n🌍 Articles by Country (last 24h):")
for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {country}: {count}")

# 4. Check translation status
response = supabase.table("mvp2_articles") \
    .select("*") \
    .gte("collected_at", time_threshold) \
    .limit(100) \
    .execute()

articles = response.data
needs_translation = 0
for article in articles:
    if not article.get('title_ko') or not article.get('title_en'):
        needs_translation += 1

print(f"\n🔤 Translation Status:")
print(f"  Needs Translation: {needs_translation}/{len(articles)} (sampled)")

# 5. Sample articles
print(f"\n📰 Sample Articles (first 5):")
response = supabase.table("mvp2_articles") \
    .select("*") \
    .gte("collected_at", time_threshold) \
    .order("collected_at", desc=True) \
    .limit(5) \
    .execute()

for i, article in enumerate(response.data, 1):
    print(f"\n  {i}. [{article['country_code']}] {article.get('title_original', 'No title')[:60]}...")
    print(f"     Source: {article.get('source_name', 'Unknown')}")
    print(f"     Published: {article.get('published_at', 'Unknown')}")
    print(f"     Has KO: {bool(article.get('title_ko'))}, Has EN: {bool(article.get('title_en'))}")

print("\n" + "=" * 60)
print("✅ Step 1 Validation Complete")
print("=" * 60)
