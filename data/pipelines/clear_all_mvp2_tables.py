#!/usr/bin/env python3
"""
Clear all mvp2_* tables to start fresh
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", "..", "backend", ".env")
load_dotenv(env_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🧹 Clearing all mvp2_* tables...")
print("=" * 60)

# All 12 tables
all_tables = [
    "mvp2_article_stance",
    "mvp2_articles",
    "mvp2_countries",
    "mvp2_embeddings",
    "mvp2_global_topics",
    "mvp2_local_topics",
    "mvp2_media_assets",
    "mvp2_megatopics",
    "mvp2_news_sources",
    "mvp2_perspectives",
    "mvp2_topic_relations",
    "mvp2_topics"
]

# Step 1: Clear FK references in mvp2_articles
print("\n[Step 1] Clearing foreign key references...")
try:
    print("  - Clearing mvp2_articles.local_topic_id...")
    supabase.table("mvp2_articles").update({"local_topic_id": None}).neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("  - Clearing mvp2_articles.global_topic_id...")
    supabase.table("mvp2_articles").update({"global_topic_id": None}).neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("  ✅ FK references cleared")
except Exception as e:
    print(f"  ⚠️ Error clearing FK references: {e}")

# Step 2: Delete all rows from each table
print("\n[Step 2] Deleting all rows from tables...")
for table in all_tables:
    try:
        print(f"  - Deleting {table}...", end=" ")
        result = supabase.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("✅")
    except Exception as e:
        print(f"⚠️ Error: {e}")

print("\n" + "=" * 60)
print("✅ All mvp2_* tables cleared successfully!")
print("\nReady for fresh pipeline run.")
