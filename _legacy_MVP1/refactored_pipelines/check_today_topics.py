import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env.local')
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

def check_today_topics():
    print(f"Checking latest 50 topics...")
    
    url = f"{SUPABASE_URL}/rest/v1/mvp_topics?select=*&order=id.desc&limit=50"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.ok:
            data = response.json()
            print(f"Found {len(data)} topics.")
            
            # Check for duplicates
            titles = [t['title'] for t in data]
            from collections import Counter
            counts = Counter(titles)
            duplicates = {k: v for k, v in counts.items() if v > 1}
            
            if duplicates:
                print(f"Found {len(duplicates)} duplicate titles!")
                print("Example duplicate:", list(duplicates.keys())[0])
                
            # Check title_kr presence
            kr_count = sum(1 for t in data if t.get('title_kr'))
            print(f"Topics with Korean title: {kr_count}/{len(data)}")
            
            if len(data) > 0:
                print("First topic:", data[0]['title'])
                print("First topic KR:", data[0].get('title_kr'))
                print("First topic Created At:", data[0].get('created_at'))
                
                # Check stats for first topic
                topic_id = data[0]['id']
                url_stats = f"{SUPABASE_URL}/rest/v1/mvp_topic_country_stats?topic_id=eq.{topic_id}&select=*"
                res_stats = requests.get(url_stats, headers=headers)
                if res_stats.ok:
                    stats = res_stats.json()
                    print("Stats for first topic:")
                    for s in stats:
                        print(f"  - {s['country_code']}: Avg Score {s.get('avg_score', 'N/A')}")
        else:
            print(f"Error: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_today_topics()
