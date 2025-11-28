import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") # Or SERVICE_ROLE_KEY if needed for writes

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

# Full list of countries from fetch_rss.py
COUNTRIES = [
    {"code": "US", "name": "United States", "flag_emoji": "🇺🇸"},
    {"code": "GB", "name": "United Kingdom", "flag_emoji": "🇬🇧"},
    {"code": "DE", "name": "Germany", "flag_emoji": "🇩🇪"},
    {"code": "FR", "name": "France", "flag_emoji": "🇫🇷"},
    {"code": "IT", "name": "Italy", "flag_emoji": "🇮🇹"},
    {"code": "JP", "name": "Japan", "flag_emoji": "🇯🇵"},
    {"code": "KR", "name": "South Korea", "flag_emoji": "🇰🇷"},
    {"code": "CA", "name": "Canada", "flag_emoji": "🇨🇦"},
    {"code": "AU", "name": "Australia", "flag_emoji": "🇦🇺"},
    {"code": "NZ", "name": "New Zealand", "flag_emoji": "🇳🇿"},
    {"code": "BE", "name": "Belgium", "flag_emoji": "🇧🇪"},
    {"code": "NL", "name": "Netherlands", "flag_emoji": "🇳🇱"},
    {"code": "RU", "name": "Russia", "flag_emoji": "🇷🇺"},
    {"code": "CN", "name": "China", "flag_emoji": "🇨🇳"}
]

def seed_countries():
    print(f"Seeding {len(COUNTRIES)} countries to {SUPABASE_URL}...")
    
    url = f"{SUPABASE_URL}/rest/v1/mvp_countries"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates" # Upsert
    }
    
    # Insert one by one or batch (batch is better)
    try:
        response = requests.post(url, headers=headers, json=COUNTRIES, timeout=30)
        if response.status_code in [200, 201]:
            print("Success!")
        else:
            print(f"Error: {response.status_code} {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    seed_countries()
