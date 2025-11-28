import os
import time
import requests
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def translate_single(text, retries=3):
    """Translates a single text to Korean."""
    if not text: return ""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    prompt = f"Translate the following news headline into natural Korean. Output ONLY the translation.\n\n{text}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.ok:
                result = response.json()
                if result and 'candidates' in result:
                    return result['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)
    return text # Fallback

def retranslate_day(target_date):
    print(f"Fetching topics for {target_date}...")
    
    # Fetch all topics for the day
    start_time = f"{target_date}T00:00:00"
    end_time = f"{target_date}T23:59:59"
    
    res = supabase.table("mvp_topics") \
        .select("id, title") \
        .gte("date", start_time) \
        .lte("date", end_time) \
        .execute()
        
    topics = res.data
    if not topics:
        print("No topics found.")
        return

    print(f"Found {len(topics)} topics. Retranslating in parallel...")
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def process_topic(t):
        try:
            new_kr = translate_single(t['title'])
            if new_kr and new_kr != t['title']:
                supabase.table("mvp_topics") \
                    .update({"title_kr": new_kr}) \
                    .eq("id", t['id']) \
                    .execute()
                return f"Updated [{t['id']}]: {new_kr}"
            return f"Skipped [{t['id']}]"
        except Exception as e:
            return f"Error [{t['id']}]: {e}"

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_topic, t) for t in topics]
        for future in as_completed(futures):
            print(future.result())

if __name__ == "__main__":
    # Target the problematic day
    retranslate_day("2025-11-26")
