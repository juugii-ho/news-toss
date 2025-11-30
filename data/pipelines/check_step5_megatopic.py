"""
Step 5 Validation: Check Global Megatopic Analysis Results
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
print("STEP 5 VALIDATION: Global Megatopic Analysis")
print("=" * 60)

# 1. Check total megatopics
response = supabase.table("mvp2_megatopics").select("*", count="exact").execute()
total = response.count
print(f"\n📊 Total Megatopics in DB: {total}")

# 2. Check published vs unpublished
response = supabase.table("mvp2_megatopics").select("*").execute()
megatopics = response.data

published = sum(1 for m in megatopics if m.get('is_published'))
unpublished = total - published

print(f"\n📢 Publication Status:")
print(f"  Published: {published}")
print(f"  Unpublished: {unpublished}")

# 3. Check megatopics by country count
country_distribution = {}
for mega in megatopics:
    country_count = len(mega.get('countries', []))
    country_distribution[country_count] = country_distribution.get(country_count, 0) + 1

print(f"\n🌍 Megatopics by Country Coverage:")
for count, num in sorted(country_distribution.items(), reverse=True):
    print(f"  {count} countries: {num} megatopics")

# 4. Sample megatopics
print(f"\n📰 Sample Megatopics (top 5 by country coverage):")
sorted_megatopics = sorted(megatopics, key=lambda x: len(x.get('countries', [])), reverse=True)

for i, mega in enumerate(sorted_megatopics[:5], 1):
    countries = mega.get('countries', [])
    print(f"\n  {i}. {mega.get('name', 'No name')[:60]}...")
    print(f"     Countries: {', '.join(countries[:5])}{'...' if len(countries) > 5 else ''} ({len(countries)} total)")
    print(f"     Articles: {mega.get('total_articles', 0)}")
    print(f"     Category: {mega.get('category', 'Unknown')}")
    print(f"     Keywords: {', '.join(mega.get('keywords', [])[:3])}")
    print(f"     Published: {'✅' if mega.get('is_published') else '❌'}")

# 5. Check topic_ids linkage
print(f"\n🔗 Topic Linkage Check:")
megatopics_with_topics = sum(1 for m in megatopics if m.get('topic_ids') and len(m.get('topic_ids', [])) > 0)
print(f"  Megatopics with linked topics: {megatopics_with_topics}/{total}")

if megatopics_with_topics > 0:
    sample = next((m for m in megatopics if m.get('topic_ids')), None)
    if sample:
        print(f"  Sample: {len(sample.get('topic_ids', []))} topics linked to '{sample.get('name', 'N/A')[:40]}...'")

print("\n" + "=" * 60)
print("✅ Step 5 Validation Complete")
print("=" * 60)
