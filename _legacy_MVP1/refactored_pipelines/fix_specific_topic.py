import os
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

def translate_single(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    prompt = f"Translate the following news headline into natural Korean. Output ONLY the translation.\n\n{text}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.ok:
            result = response.json()
            if result and 'candidates' in result:
                return result['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Error: {e}")
    return None

def fix_topic(topic_id):
    print(f"Fetching topic {topic_id}...")
    res = supabase.table("mvp_topics").select("id, title, title_kr").eq("id", topic_id).execute()
    if not res.data:
        print("Topic not found.")
        return
        
    topic = res.data[0]
    print(f"Current Title (EN): {topic['title']}")
    print(f"Current Title (KR): {topic['title_kr']}")
    
    new_kr = translate_single(topic['title'])
    if new_kr:
        print(f"New Translation: {new_kr}")
        supabase.table("mvp_topics").update({"title_kr": new_kr}).eq("id", topic_id).execute()
        print("Updated successfully.")
    else:
        print("Translation failed.")

if __name__ == "__main__":
    fix_topic(1220)
