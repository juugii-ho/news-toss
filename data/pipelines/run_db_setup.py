import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load env
load_dotenv('backend/.env')
if not os.getenv("NEXT_PUBLIC_SUPABASE_URL"):
    load_dotenv() # Try local .env

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase: Client = create_client(url, key)

def run_migration():
    print("Running DB Migration...")
    with open("data/pipelines/setup_topics_db.sql", "r") as f:
        sql = f.read()
        
    # Supabase-py doesn't support raw SQL execution directly via client easily for DDL 
    # without service role or specific setup usually.
    # But we can try rpc if we had one, or just print instructions if it fails.
    # Actually, for MVP, the easiest way is often to ask the user to run it in SQL Editor 
    # OR use the postgres connection string if available.
    # However, since we are an agent, we can try to use the `psycopg2` if available or just guide the user.
    
    # Wait, supabase-py client usually interacts with REST API (PostgREST). 
    # It cannot execute CREATE TABLE unless we use a stored procedure.
    
    print("\n⚠️ IMPORTANT: The supabase-py client cannot execute 'CREATE TABLE' directly.")
    print("Please copy the content of 'data/pipelines/setup_topics_db.sql' and run it in your Supabase SQL Editor.")
    print("\nSQL Content Preview:")
    print("-" * 20)
    print(sql[:200] + "...")
    print("-" * 20)

if __name__ == "__main__":
    run_migration()
