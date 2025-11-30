
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv('app/frontend/.env.local')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase environment variables not found.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

sql = """
ALTER TABLE mvp2_topics ADD COLUMN IF NOT EXISTS thumbnail_url TEXT;
ALTER TABLE mvp2_global_topics ADD COLUMN IF NOT EXISTS thumbnail_url TEXT;
"""

try:
    # Supabase-py doesn't support raw SQL easily unless via RPC or specific function.
    # But we can try to use a dummy RPC if one exists, or just use the dashboard.
    # Actually, we can't run DDL via the JS/Python client directly unless we have a 'exec_sql' RPC function.
    # Let's check if we can assume it's already there or if we need to ask the user.
    # Wait, the user has `add_thumbnail_column.sql` in `data/pipelines`.
    # I can try to run it using `psql` if `psql` is installed and I have the connection string.
    # The .env.local has DATABASE_URL!
    
    print("Please run the following SQL in your Supabase SQL Editor:")
    print(sql)
    
except Exception as e:
    print(f"Error: {e}")
