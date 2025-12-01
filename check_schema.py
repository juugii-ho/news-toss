import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('backend/.env')
load_dotenv('.env.local')
load_dotenv('.env')

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("Missing env vars")
    exit(1)

supabase = create_client(url, key)

# Fetch one row to check columns
try:
    response = supabase.table("mvp2_articles").select("*").limit(1).execute()
    if response.data:
        print("Columns:", response.data[0].keys())
        if 'embedding' in response.data[0]:
            print("Embedding found!")
            print("Embedding length:", len(response.data[0]['embedding']))
        else:
            print("No embedding column found in data.")
    else:
        print("Table is empty.")
except Exception as e:
    print(f"Error: {e}")
