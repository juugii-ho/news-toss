#!/usr/bin/env python3
"""
Batch translate all topic titles to Korean.
This fixes the issue where title_kr was not translated properly.
"""

import os
import sys
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
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    sys.exit(1)

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found.")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def batch_translate_to_korean(texts, retries=3):
    """Translates a list of English texts to Korean using Gemini API."""
    if not texts:
        return []
        
    BATCH_SIZE = 50
    all_translations = []
    
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        
        prompt = """You are a professional news translator. Translate the following English headlines into natural Korean.
        Keep the tone professional and objective.
        Output ONLY the translated lines in the same order, one per line.
        Do NOT include numbers or dashes at the start of each line.
        
        Texts:
        """ + "\n".join([f"{t}" for t in batch_texts])
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        batch_results = []
        for attempt in range(retries):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=300)
                if response.ok:
                    result = response.json()
                    if result and 'candidates' in result and result['candidates']:
                        content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            # Remove leading numbers/dashes if present
                            if line and (line[0].isdigit() or line.startswith('-')):
                                cleaned = line.split('.', 1)[-1].strip() if '.' in line else line.strip('- ')
                                batch_results.append(cleaned)
                            else:
                                batch_results.append(line)
                        break
                else:
                    print(f"API error (attempt {attempt+1}): {response.status_code}")
            except Exception as e:
                print(f"Error translating batch (attempt {attempt+1}): {e}")
                time.sleep(2 ** attempt)
        
        if not batch_results:
            print(f"Translation failed for batch {i//BATCH_SIZE + 1}, using English fallback")
            batch_results = batch_texts
            
        # Ensure we have the right number of results
        if len(batch_results) < len(batch_texts):
            batch_results.extend(batch_texts[len(batch_results):])
        elif len(batch_results) > len(batch_texts):
            batch_results = batch_results[:len(batch_texts)]
            
        all_translations.extend(batch_results)
        print(f"Translated batch {i//BATCH_SIZE + 1}/{(len(texts)-1)//BATCH_SIZE + 1}")
        time.sleep(1)
        
    return all_translations


def main():
    # Fetch all topics where title_kr is same as title (not translated)
    print("Fetching topics needing translation...")
    
    # Get all topics
    response = supabase.table("mvp_topics") \
        .select("id, title, title_kr") \
        .order("id", desc=False) \
        .execute()
    
    topics = response.data
    print(f"Total topics: {len(topics)}")
    
    # Filter topics that need translation (where title_kr == title or title_kr is None)
    needs_translation = []
    for t in topics:
        if not t.get('title_kr') or t['title'] == t.get('title_kr'):
            needs_translation.append(t)
    
    print(f"Topics needing translation: {len(needs_translation)}")
    
    if not needs_translation:
        print("All topics already translated!")
        return
    
    # Extract titles
    titles_to_translate = [t['title'] for t in needs_translation]
    
    # Translate
    print(f"\nTranslating {len(titles_to_translate)} titles...")
    translated_titles = batch_translate_to_korean(titles_to_translate)
    
    # Update database
    print("\nUpdating database...")
    success_count = 0
    fail_count = 0
    
    for i, topic in enumerate(needs_translation):
        try:
            kr_title = translated_titles[i]
            # Only update if translation is different from English
            if kr_title != topic['title']:
                supabase.table("mvp_topics") \
                    .update({"title_kr": kr_title}) \
                    .eq("id", topic['id']) \
                    .execute()
                success_count += 1
                if success_count % 10 == 0:
                    print(f"Updated {success_count} topics...")
            else:
                fail_count += 1
                print(f"Skipped topic {topic['id']}: translation same as English")
        except Exception as e:
            fail_count += 1
            print(f"Error updating topic {topic['id']}: {e}")
    
    print(f"\n✅ Translation complete!")
    print(f"   Success: {success_count}")
    print(f"   Failed: {fail_count}")


if __name__ == "__main__":
    main()
