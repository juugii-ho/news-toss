import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env.local')
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

def debug_titles():
    print(f"Searching for 'Israeli Strikes'...")
    
    url = f"{SUPABASE_URL}/rest/v1/mvp_topics?title=ilike.%Israeli%Strikes%&select=*"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.ok:
            data = response.json()
            print(f"Found {len(data)} matching topics.")
            for t in data:
                print(f"Title: {t['title']}")
                print(f"Title KR: {t.get('title_kr')}")
                print(f"Created At: {t.get('created_at')}")
        else:
            print(f"Error: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_titles()
