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
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Use Service Role Key for writing
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def batch_translate(texts, retries=3):
    """Translates a list of English texts to Korean using Gemini API."""
    if not texts:
        return []
        
    BATCH_SIZE = 50
    all_translations = []
    
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        print(f"Translating batch {i//BATCH_SIZE + 1} ({len(batch_texts)} items)...")
        
        prompt = """You are a professional news translator. Translate the following English headlines into natural Korean.
        Keep the tone professional and objective.
        Output ONLY the translated lines in the same order, one per line.
        
        Headlines:
        """ + "\n".join([f"- {t}" for t in batch_texts])
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        batch_results = []
        success = False
        for attempt in range(retries):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=30)
                if response.ok:
                    result = response.json()
                    if result and 'candidates' in result and result['candidates']:
                        content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line:
                                # Remove bullet points if present
                                cleaned = line.split('.', 1)[-1].strip() if line[0].isdigit() and '.' in line else line.strip('- ')
                                batch_results.append(cleaned)
                        success = True
                        break
            except Exception as e:
                print(f"Error translating batch: {e}")
                time.sleep(2 ** attempt)
        
        if not success or not batch_results:
            print("Translation failed for batch, keeping original.")
            batch_results = batch_texts
            
        # Pad or truncate to match input length
        if len(batch_results) < len(batch_texts):
            batch_results.extend(batch_texts[len(batch_results):])
        elif len(batch_results) > len(batch_texts):
            batch_results = batch_results[:len(batch_texts)]
            
        all_translations.extend(batch_results)
        time.sleep(1) # Rate limit
        
    return all_translations

def fix_translations():
    today_start = "2025-11-27T00:00:00"
    today_end = "2025-11-27T23:59:59"
    
    print(f"Fetching topics for {today_start[:10]}...")
    
    # Fetch topics for today
    res = supabase.table("mvp_topics") \
        .select("id, title, title_kr") \
        .gte("date", today_start) \
        .lte("date", today_end) \
        .execute()
        
    topics = res.data
    if not topics:
        print("No topics found for today.")
        return

    print(f"Found {len(topics)} topics.")
    
    # Identify topics needing translation (where title_kr == title or title_kr is English-like)
    to_update = []
    for t in topics:
        # Simple heuristic: if title_kr equals title, it needs translation
        # Or if title_kr is None
        if not t['title_kr'] or t['title_kr'] == t['title']:
            to_update.append(t)
            
    if not to_update:
        print("All topics seem to have translations already.")
        return
        
    print(f"Translating {len(to_update)} topics...")
    
    titles = [t['title'] for t in to_update]
    translated_titles = batch_translate(titles)
    
    print("Updating database...")
    for i, t in enumerate(to_update):
        new_title_kr = translated_titles[i]
        # Skip if translation failed (returned same English) - though we might want to save it anyway?
        # Let's save it.
        
        try:
            supabase.table("mvp_topics") \
                .update({"title_kr": new_title_kr}) \
                .eq("id", t['id']) \
                .execute()
            print(f"Updated [{t['id']}]: {new_title_kr}")
        except Exception as e:
            print(f"Failed to update {t['id']}: {e}")
            
    print("Done.")

if __name__ == "__main__":
    fix_translations()
