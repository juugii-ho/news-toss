import os
import time
import requests
from dotenv import load_dotenv
from pathlib import Path
from supabase import create_client

# Load environment variables
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") # Use SERVICE_ROLE_KEY if RLS blocks updates

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def batch_translate(texts, target_lang="ko", model="models/gemini-2.5-flash"):
    """
    Translates a list of texts using Gemini API.
    Returns a list of translated texts.
    """
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found.")
        return texts

    # Prompt Engineering for Batch Translation
    prompt = f"""You are a professional translator. Translate the following news headlines into {target_lang}.
    Maintain the original meaning and tone.
    Output ONLY the translated lines in the same order, one per line.
    
    Headlines:
    """ + "\n".join(texts)

    url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=300)
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' in result and result['candidates']:
            content = result['candidates'][0]['content']['parts'][0]['text']
            translated_lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
            
            # Safety check: if counts mismatch, return original (or handle error)
            if len(translated_lines) != len(texts):
                print(f"Warning: Translation count mismatch ({len(translated_lines)} vs {len(texts)}).")
                # Fallback: try to align or just return originals for safety
                return texts 
                
            return translated_lines
            
    except Exception as e:
        print(f"Error in batch translation: {e}")
        return texts # Fallback to original

    return texts

def translate_articles_db():
    print("Fetching articles needing translation from Supabase...")
    
    # 1. Fetch articles where title_en is NULL
    # Note: Supabase limit is 1000 by default. We might need pagination if > 1000.
    # For now, let's process 100 at a time in a loop until done.
    
    BATCH_SIZE = 50
    
    while True:
        # Fetch a batch of untranslated articles
        # We prioritize English translation first as it's needed for embedding
        response = supabase.table("mvp_articles") \
            .select("id, title, country_code") \
            .is_("title_en", "null") \
            .limit(BATCH_SIZE) \
            .execute()
            
        articles = response.data
        
        if not articles:
            print("No more articles needing English translation.")
            break
            
        print(f"Processing batch of {len(articles)} articles for EN translation...")
        
        # Filter for English source countries (skip translation)
        english_countries = ['US', 'GB', 'CA', 'AU']
        to_translate = []
        to_update_direct = []
        
        for art in articles:
            if art['country_code'] in english_countries:
                to_update_direct.append({'id': art['id'], 'title_en': art['title']})
            else:
                to_translate.append(art)
        
        # Update English source articles directly
        if to_update_direct:
            print(f"  - Auto-filling {len(to_update_direct)} English source articles...")
            for item in to_update_direct:
                for attempt in range(3):
                    try:
                        supabase.table("mvp_articles").update({'title_en': item['title_en']}).eq('id', item['id']).execute()
                        break
                    except Exception as e:
                        print(f"    Error updating DB (Attempt {attempt+1}): {e}")
                        time.sleep(1)

        # Translate non-English articles
        if to_translate:
            titles = [a['title'] for a in to_translate]
            print(f"  - Translating {len(titles)} titles to English...")
            translated_titles = batch_translate(titles, target_lang="English")
            
            for i, t_title in enumerate(translated_titles):
                if i < len(to_translate):
                    art_id = to_translate[i]['id']
                    for attempt in range(3):
                        try:
                            supabase.table("mvp_articles").update({'title_en': t_title}).eq('id', art_id).execute()
                            break
                        except Exception as e:
                            print(f"    Error updating DB (Attempt {attempt+1}): {e}")
                            time.sleep(1)
        
        time.sleep(1)

    print("\n--- English Translation Complete. Starting Korean Translation ---\n")

    while True:
        # Fetch articles where title_kr is NULL
        response = supabase.table("mvp_articles") \
            .select("id, title, country_code") \
            .is_("title_kr", "null") \
            .limit(BATCH_SIZE) \
            .execute()
            
        articles = response.data
        
        if not articles:
            print("No more articles needing Korean translation.")
            break
            
        print(f"Processing batch of {len(articles)} articles for KR translation...")
        
        korean_countries = ['KR']
        to_translate = []
        to_update_direct = []
        
        for art in articles:
            if art['country_code'] in korean_countries:
                to_update_direct.append({'id': art['id'], 'title_kr': art['title']})
            else:
                to_translate.append(art)
        
        if to_update_direct:
             print(f"  - Auto-filling {len(to_update_direct)} Korean source articles...")
             for item in to_update_direct:
                for attempt in range(3):
                    try:
                        supabase.table("mvp_articles").update({'title_kr': item['title_kr']}).eq('id', item['id']).execute()
                        break
                    except Exception as e:
                        print(f"    Error updating DB (Attempt {attempt+1}): {e}")
                        time.sleep(1)

        if to_translate:
            titles = [a['title'] for a in to_translate]
            print(f"  - Translating {len(titles)} titles to Korean...")
            translated_titles = batch_translate(titles, target_lang="Korean")
            
            for i, t_title in enumerate(translated_titles):
                 if i < len(to_translate):
                    art_id = to_translate[i]['id']
                    for attempt in range(3):
                        try:
                            supabase.table("mvp_articles").update({'title_kr': t_title}).eq('id', art_id).execute()
                            break
                        except Exception as e:
                            print(f"    Error updating DB (Attempt {attempt+1}): {e}")
                            time.sleep(1)
        
        time.sleep(1)

if __name__ == "__main__":
    translate_articles_db()
