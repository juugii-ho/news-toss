"""
Step 2 Validation: Check Translation Results (Last 24h only)
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
print("STEP 2 VALIDATION: Translation (Last 24h)")
print("=" * 60)

# 1. Check translation completion for last 24h
time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()
response = supabase.table("mvp2_articles") \
    .select("*") \
    .gte("published_at", time_threshold) \
    .execute()

articles = response.data
total = len(articles)

has_ko = sum(1 for a in articles if a.get('title_ko'))
has_en = sum(1 for a in articles if a.get('title_en'))
fully_translated = sum(1 for a in articles if a.get('title_ko') and a.get('title_en'))

print(f"\n📊 Translation Status (Last 24h):")
print(f"  Total Articles: {total}")
print(f"  Has Korean: {has_ko} ({has_ko/total*100:.1f}%)")
print(f"  Has English: {has_en} ({has_en/total*100:.1f}%)")
print(f"  Fully Translated: {fully_translated} ({fully_translated/total*100:.1f}%)")

# 2. Check by country
country_stats = {}
for article in articles:
    country = article.get('country_code', 'Unknown')
    if country not in country_stats:
        country_stats[country] = {'total': 0, 'translated': 0}
    country_stats[country]['total'] += 1
    if article.get('title_ko') and article.get('title_en'):
        country_stats[country]['translated'] += 1

print(f"\n🌍 Translation by Country (Last 24h):")
for country, stats in sorted(country_stats.items(), key=lambda x: x[1]['total'], reverse=True):
    pct = stats['translated'] / stats['total'] * 100 if stats['total'] > 0 else 0
    print(f"  {country}: {stats['translated']}/{stats['total']} ({pct:.1f}%)")

# 3. Sample translations
print(f"\n📝 Sample Translations (first 5 fully translated):")
response = supabase.table("mvp2_articles") \
    .select("*") \
    .gte("published_at", time_threshold) \
    .not_.is_("title_ko", "null") \
    .not_.is_("title_en", "null") \
    .limit(5) \
    .execute()

for i, article in enumerate(response.data, 1):
    print(f"\n  {i}. [{article['country_code']}]")
    print(f"     Original: {article.get('title_original', 'N/A')[:60]}...")
    print(f"     Korean:   {article.get('title_ko', 'N/A')[:60]}...")
    print(f"     English:  {article.get('title_en', 'N/A')[:60]}...")

# 4. Check for failures
needs_translation = [a for a in articles if not a.get('title_ko') or not a.get('title_en')]
if needs_translation:
    print(f"\n⚠️  Still Need Translation: {len(needs_translation)}")
    print(f"   Sample failures:")
    for article in needs_translation[:3]:
        print(f"   - [{article['country_code']}] {article.get('title_original', 'N/A')[:50]}...")

print("\n" + "=" * 60)
print("✅ Step 2 Validation Complete")
print("=" * 60)
