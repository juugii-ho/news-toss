import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from project root .env.local
root_dir = Path(__file__).resolve().parents[2] # data/pipelines/ -> data/ -> root
load_dotenv(root_dir / ".env.local")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print(f"Checking Supabase URL: {SUPABASE_URL}")

try:
    # Try to fetch 1 row from mvp_topics
    url = f"{SUPABASE_URL}/rest/v1/mvp_topics?select=*&limit=1"
    res = requests.get(url, headers=headers)
    
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    
except Exception as e:
    print(f"Error: {e}")
