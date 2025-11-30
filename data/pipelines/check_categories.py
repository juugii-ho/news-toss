#!/usr/bin/env python3
"""
Check if category data exists in topics and megatopics
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

print("🔍 Checking category data...\n")

# Check mvp2_megatopics
print("📊 mvp2_megatopics (Global Topics):")
try:
    result = supabase.table("mvp2_megatopics").select("id, title_ko, category").limit(10).execute()
    
    if result.data:
        total = len(result.data)
        with_category = sum(1 for item in result.data if item.get('category'))
        
        print(f"  Total topics: {total}")
        print(f"  With category: {with_category}")
        print(f"  Without category: {total - with_category}")
        
        if with_category > 0:
            print(f"\n  Sample topics with categories:")
            for item in result.data[:5]:
                if item.get('category'):
                    print(f"    - {item.get('title_ko', 'N/A')[:40]}: {item.get('category', 'N/A')}")
        else:
            print(f"\n  ⚠️  No categories found in megatopics!")
    else:
        print("  No data found")
        
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*60 + "\n")

# Check mvp2_topics
print("📊 mvp2_topics (Local Topics):")
try:
    result = supabase.table("mvp2_topics").select("id, headline, category").limit(10).execute()
    
    if result.data:
        total = len(result.data)
        with_category = sum(1 for item in result.data if item.get('category'))
        
        print(f"  Total topics: {total}")
        print(f"  With category: {with_category}")
        print(f"  Without category: {total - with_category}")
        
        if with_category > 0:
            print(f"\n  Sample topics with categories:")
            for item in result.data[:5]:
                if item.get('category'):
                    print(f"    - {item.get('headline', 'N/A')[:40]}: {item.get('category', 'N/A')}")
        else:
            print(f"\n  ⚠️  No categories found in topics!")
    else:
        print("  No data found")
        
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*60)
print("\n💡 If no categories found, you need to:")
print("   1. Run the topic clustering pipeline with LLM")
print("   2. Or manually update existing topics with categories")
