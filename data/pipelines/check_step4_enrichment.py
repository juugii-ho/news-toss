"""
Step 4 Validation: Check Enrichment Results
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
print("STEP 4 VALIDATION: Enrichment")
print("=" * 60)

# 1. Check topics with stances
response = supabase.table("mvp2_topics").select("*").execute()
topics = response.data
total = len(topics)

has_stances = sum(1 for t in topics if t.get('stances'))
has_keywords = sum(1 for t in topics if t.get('keywords') and len(t.get('keywords', [])) > 0)
has_category = sum(1 for t in topics if t.get('category') and t.get('category') != 'Unclassified')

print(f"\n📊 Enrichment Status:")
print(f"  Total Topics: {total}")
print(f"  Has Stances: {has_stances} ({has_stances/total*100:.1f}%)")
print(f"  Has Keywords: {has_keywords} ({has_keywords/total*100:.1f}%)")
print(f"  Has Category: {has_category} ({has_category/total*100:.1f}%)")

# 2. Category distribution
category_counts = {}
for topic in topics:
    category = topic.get('category', 'Unclassified')
    category_counts[category] = category_counts.get(category, 0) + 1

print(f"\n📂 Category Distribution:")
for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {category}: {count} ({count/total*100:.1f}%)")

# 3. Stance distribution
total_factual = 0
total_critical = 0
total_supportive = 0

for topic in topics:
    stances = topic.get('stances', {})
    total_factual += len(stances.get('factual', []))
    total_critical += len(stances.get('critical', []))
    total_supportive += len(stances.get('supportive', []))

total_articles = total_factual + total_critical + total_supportive

print(f"\n📊 Stance Distribution:")
if total_articles > 0:
    print(f"  Factual: {total_factual} ({total_factual/total_articles*100:.1f}%)")
    print(f"  Critical: {total_critical} ({total_critical/total_articles*100:.1f}%)")
    print(f"  Supportive: {total_supportive} ({total_supportive/total_articles*100:.1f}%)")

# 4. Sample enriched topics
print(f"\n📰 Sample Enriched Topics (first 5):")
response = supabase.table("mvp2_topics") \
    .select("*") \
    .order("article_count", desc=True) \
    .limit(5) \
    .execute()

for i, topic in enumerate(response.data, 1):
    stances = topic.get('stances', {})
    print(f"\n  {i}. [{topic['country_code']}] {topic.get('topic_name', 'No name')[:60]}...")
    print(f"     Category: {topic.get('category', 'Unknown')}")
    print(f"     Keywords: {', '.join(topic.get('keywords', [])[:5])}")
    print(f"     Stances: F:{len(stances.get('factual', []))} C:{len(stances.get('critical', []))} S:{len(stances.get('supportive', []))}")

print("\n" + "=" * 60)
print("✅ Step 4 Validation Complete")
print("=" * 60)
