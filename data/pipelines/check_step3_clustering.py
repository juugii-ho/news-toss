"""
Step 3 Validation: Check Clustering Results
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
print("STEP 3 VALIDATION: Clustering (Topic Persistence)")
print("=" * 60)

# 1. Check total topics
response = supabase.table("mvp2_topics").select("*", count="exact").execute()
total_topics = response.count
print(f"\n📊 Total Topics in DB: {total_topics}")

# 2. Check topics by country
response = supabase.table("mvp2_topics").select("country_code", count="exact").execute()
topics = response.data

country_counts = {}
for topic in topics:
    country = topic.get('country_code', 'Unknown')
    country_counts[country] = country_counts.get(country, 0) + 1

print(f"\n🌍 Topics by Country:")
for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {country}: {count}")

# 3. Check topic persistence (first_seen_at vs last_updated_at)
response = supabase.table("mvp2_topics") \
    .select("*") \
    .not_.is_("first_seen_at", "null") \
    .limit(100) \
    .execute()

persistent_topics = response.data
updated_topics = sum(1 for t in persistent_topics if t.get('first_seen_at') != t.get('last_updated_at'))

print(f"\n🔄 Topic Persistence (sample of {len(persistent_topics)}):")
print(f"  Updated (not new): {updated_topics}")
print(f"  New: {len(persistent_topics) - updated_topics}")

# 4. Sample topics
print(f"\n📰 Sample Topics (first 5):")
response = supabase.table("mvp2_topics") \
    .select("*") \
    .order("article_count", desc=True) \
    .limit(5) \
    .execute()

for i, topic in enumerate(response.data, 1):
    print(f"\n  {i}. [{topic['country_code']}] {topic.get('topic_name', 'No name')[:60]}...")
    print(f"     Articles: {topic.get('article_count', 0)}")
    print(f"     Category: {topic.get('category', 'Unknown')}")
    print(f"     Keywords: {', '.join(topic.get('keywords', [])[:3])}")
    
    # Check if it's updated or new
    first_seen = topic.get('first_seen_at')
    last_updated = topic.get('last_updated_at')
    if first_seen and last_updated:
        if first_seen == last_updated:
            print(f"     Status: 🆕 New topic")
        else:
            print(f"     Status: 🔄 Updated topic")

# 5. Check stances
print(f"\n📊 Stance Distribution (sample):")
response = supabase.table("mvp2_topics") \
    .select("stances") \
    .limit(100) \
    .execute()

total_factual = 0
total_critical = 0
total_supportive = 0

for topic in response.data:
    stances = topic.get('stances', {})
    total_factual += len(stances.get('factual', []))
    total_critical += len(stances.get('critical', []))
    total_supportive += len(stances.get('supportive', []))

total_articles = total_factual + total_critical + total_supportive
if total_articles > 0:
    print(f"  Factual: {total_factual} ({total_factual/total_articles*100:.1f}%)")
    print(f"  Critical: {total_critical} ({total_critical/total_articles*100:.1f}%)")
    print(f"  Supportive: {total_supportive} ({total_supportive/total_articles*100:.1f}%)")

print("\n" + "=" * 60)
print("✅ Step 3 Validation Complete")
print("=" * 60)
