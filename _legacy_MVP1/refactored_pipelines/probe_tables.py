import os
import requests
import json
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv('.env') # Fallback

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials in .env or .env.local")
    exit(1)

def probe_table(table_name):
    print(f"Probing table: {table_name}...")
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=*&limit=5&order=created_at.desc"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.ok:
            data = response.json()
            if data:
                print(f"✅ Table '{table_name}' exists and has data!")
                print(f"Fetched {len(data)} rows.")
                for i, row in enumerate(data):
                    print(f"\n--- Row {i+1} ---")
                    print(f"Title: {row.get('title')}")
                    print(f"Topic ID: {row.get('topic_id')}")
                    print(f"Stance: {row.get('stance')}")
                    print(f"URL: {row.get('url')}")
                return True
            else:
                print(f"✅ Table '{table_name}' exists but is empty.")
                return True
        else:
            print(f"❌ Table '{table_name}' not accessible (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"Error probing {table_name}: {e}")
        return False

if __name__ == "__main__":
    print("Probing mvp_topics for divergence_score and stats...")
    
    # Get top 5 topics
    url_topics = f"{SUPABASE_URL}/rest/v1/mvp_topics?select=id,title,divergence_score&limit=5&order=created_at.desc"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    
    try:
        res_topics = requests.get(url_topics, headers=headers)
        if res_topics.ok:
            topics = res_topics.json()
            for t in topics:
                print(f"\n--- Topic: {t['title']} (Score: {t['divergence_score']}) ---")
                
                # Get stats for this topic
                url_stats = f"{SUPABASE_URL}/rest/v1/mvp_topic_country_stats?select=country_code,avg_score&topic_id=eq.{t['id']}"
                res_stats = requests.get(url_stats, headers=headers)
                if res_stats.ok:
                    stats = res_stats.json()
                    for s in stats:
                        print(f"  - {s['country_code']}: {s['avg_score']}")
    except Exception as e:
        print(e)
