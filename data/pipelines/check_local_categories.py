#!/usr/bin/env python3
"""
Check if local topics have category data
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Missing Supabase credentials")
    exit(1)

supabase = create_client(url, key)

print("🔍 Checking local topics for category data...\n")

# Get topics for KR
result = supabase.table("mvp2_topics").select("id, headline, category, country_code").eq("country_code", "KR").order("created_at", desc=True).limit(15).execute()

if result.data:
    print(f"📊 Found {len(result.data)} KR topics:\n")
    
    with_category = 0
    without_category = 0
    
    for topic in result.data:
        has_cat = topic.get('category') is not None
        if has_cat:
            with_category += 1
        else:
            without_category += 1
            
        status = "✅" if has_cat else "❌"
        cat = topic.get('category', 'None')
        headline = (topic.get('headline') or 'N/A')[:40]
        
        print(f"{status} {cat:15} | {headline}")
    
    print(f"\n📈 Summary:")
    print(f"   With category: {with_category}")
    print(f"   Without category: {without_category}")
else:
    print("No topics found")
