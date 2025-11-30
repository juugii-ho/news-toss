#!/usr/bin/env python3
"""
Apply migration to add category, keywords, stances to mvp2_global_topics
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Missing credentials")
    exit(1)

supabase = create_client(url, key)

print("🔧 Adding columns to mvp2_global_topics...")

# Read migration file
with open("/Users/sml/Downloads/code/MVP2/infra/supabase/migrations/20251130_add_category_fields.sql", "r") as f:
    sql = f.read()

# Execute via RPC (if available) or manually
# Since Supabase client doesn't support raw SQL easily, we'll use psycopg2 or execute via Supabase dashboard
# For now, let's try using the service role to execute

try:
    # This won't work directly, but let's try
    # We need to use psycopg2 or execute in Supabase SQL editor
    print("⚠️  Please execute the following SQL in Supabase SQL Editor:")
    print("\n" + "="*60)
    print(sql)
    print("="*60)
    print("\nOr use psycopg2 to execute directly.")
    
except Exception as e:
    print(f"Error: {e}")
