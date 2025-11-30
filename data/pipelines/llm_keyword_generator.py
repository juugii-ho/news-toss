import os
import json
import time
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
load_dotenv(os.path.join(project_root, 'backend', '.env'))

# Setup Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    print("❌ GOOGLE_API_KEY not found.")
    exit(1)

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

# Setup Supabase
url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("❌ Supabase credentials not found.")
    exit(1)

supabase: Client = create_client(url, key)

def generate_keywords(title, context=""):
    """
    Generate 1-2 short keywords for a given title.
    """
    prompt = f"""
Role: Data Tagger
Task: Extract 1-2 representative keywords from the news title.
Title: {title}
Context: {context}

Rules:
1. Output: JSON array of strings.
2. Length: Each keyword must be UNDER 5 characters (Korean).
3. Content: Nouns only. No verbs.
4. Examples:
   - "손흥민 2골 폭발" -> ["손흥민", "EPL"]
   - "비트코인 1억 돌파" -> ["비트코인", "가상화폐"]
   - "윤석열 대통령 지지율 하락" -> ["윤석열", "지지율"]

Output JSON:
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        print(f"    ⚠️ Keyword generation failed: {e}")
        return []

def process_topics():
    print("\n🇰🇷 Processing Topics for Keywords...")
    try:
        # Calculate 24 hours ago
        time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        
        # Fetch all recent topics (regardless of keywords status to catch empty arrays)
        response = supabase.table("mvp2_topics") \
            .select("*") \
            .eq("country_code", "KR") \
            .gte("created_at", time_threshold) \
            .execute()
            
        topics = response.data
        print(f"Checking {len(topics)} recent topics for missing keywords...")
        
        count = 0
        for t in topics:
            keywords = t.get('keywords')
            # Check if keywords is None or empty list
            if not keywords or len(keywords) == 0:
                print(f"  Generating keywords for: {t['topic_name'][:30]}...")
                keywords = generate_keywords(t['topic_name'], t.get('headline', ''))
                
                if keywords:
                    print(f"    -> {keywords}")
                    supabase.table("mvp2_topics").update({"keywords": keywords}).eq("id", t['id']).execute()
                    time.sleep(0.5)
                    count += 1
                else:
                    print("    -> Failed.")
                
        print(f"Generated keywords for {count} topics.")

    except Exception as e:
        print(f"❌ Error processing topics: {e}")

if __name__ == "__main__":
    process_topics()
