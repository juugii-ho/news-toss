
import os
import json
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

root_dir = Path('.').resolve()
load_dotenv(root_dir / '.env.local')
load_dotenv(root_dir / '.env')

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def debug_assignment():
    print("Loading megatopics.json...")
    try:
        with open('data/pipelines/megatopics.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("megatopics.json not found")
        return

    print(f"Data type: {type(data)}")
    
    if isinstance(data, list):
        print("Data is a list. Assuming it contains megatopics directly.")
        megatopics = data
        country_topics = {} # Can't get country topics if it's just a list of megatopics
    else:
        megatopics = data.get('megatopics', [])
        country_topics = data.get('country_topics', {})

    print(f"Loaded {len(megatopics)} megatopics")
    
    if not megatopics:
        return

    # Check first megatopic
    mega = megatopics[0]
    print(f"\nChecking Megatopic: {mega.get('title_kr', 'No Title')}")
    
    articles = mega.get('articles', [])
    print(f"  -> Articles in JSON: {len(articles)}")
    
    if not articles:
        print("  ⚠️ No articles in JSON!")
        return

    article_ids = [a['id'] for a in articles]
    print(f"  -> Article IDs: {article_ids[:5]}...")
    
    # Check if these articles exist in DB
    print("Checking existence in DB...")
    existing = supabase.table('mvp_articles').select('id, topic_id').in_('id', article_ids[:10]).execute()
    print(f"  -> Found {len(existing.data)} articles in DB")
    
    for a in existing.data:
        print(f"    - ID {a['id']}: topic_id={a['topic_id']}")

    # Check national topics
    print("\nChecking National Topics...")
    country_topics = data.get('country_topics', {})
    if 'KR' in country_topics:
        kr_topics = country_topics['KR'].get('topics', [])
        print(f"  -> KR Topics: {len(kr_topics)}")
        if kr_topics:
            t = kr_topics[0]
            print(f"  -> First KR Topic: {t.get('name')}")
            t_articles = t.get('articles', [])
            print(f"  -> Articles: {len(t_articles)}")
            t_ids = [a['id'] for a in t_articles]
            print(f"  -> IDs: {t_ids[:5]}...")
            
            # Check DB
            existing_kr = supabase.table('mvp_articles').select('id, topic_id').in_('id', t_ids[:10]).execute()
            print(f"  -> Found {len(existing_kr.data)} articles in DB")
            for a in existing_kr.data:
                print(f"    - ID {a['id']}: topic_id={a['topic_id']}")

if __name__ == "__main__":
    debug_assignment()
