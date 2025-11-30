#!/usr/bin/env python3
"""
Test the global insights API to see if category is returned
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

print("🔍 Testing API response for global topics...\n")

# Get the latest global topic
result = supabase.table("mvp2_global_topics").select("*").order("created_at", desc=True).limit(1).execute()

if result.data and len(result.data) > 0:
    topic = result.data[0]
    print(f"📊 Topic: {topic.get('title_ko', 'N/A')}")
    print(f"   ID: {topic.get('id')}")
    print(f"   Category: {topic.get('category', 'NOT FOUND')}")
    print(f"   Keywords: {topic.get('keywords', 'NOT FOUND')}")
    print(f"   Stances: {topic.get('stances', 'NOT FOUND')}")
    
    # Check if mvp2_global_topics table has these columns
    print("\n📋 Available fields in response:")
    for key in sorted(topic.keys()):
        print(f"   - {key}")
else:
    print("No data found")
