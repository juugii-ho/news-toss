
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

def debug_topics():
    print("Fetching latest topics...")
    # Get latest date
    latest = supabase.table('mvp_topics').select('date').order('date', desc=True).limit(1).execute()
    if not latest.data:
        print("No topics found")
        return
    
    target_date = latest.data[0]['date']
    print(f"Target Date: {target_date}")
    
    # Fetch all topics for this date
    topics = supabase.table('mvp_topics').select('id, title, title_kr, headline, country_count').eq('date', target_date).execute()
    print(f"Total topics today: {len(topics.data)}")
    
    # Check a few topics to see if they have articles and country codes
    # We specifically look for topics that look like they should be Korean (based on title_kr or headline)
    kr_candidates = []
    for t in topics.data:
        text = t.get('title_kr') or t.get('headline') or t.get('title') or ''
        if any(char >= '\uAC00' and char <= '\uD7A3' for char in text):
            kr_candidates.append(t)
            
    print(f"Potential KR topics (by char): {len(kr_candidates)}")
    
    # Find topics with KR articles
    print("Searching for KR topics...")
    
    # Find topics linked to KR articles
    # First get KR article IDs
    kr_articles = supabase.table("mvp_articles").select("topic_id").eq("country_code", "KR").not_.is_("topic_id", "null").execute()
    kr_topic_ids = list(set([a['topic_id'] for a in kr_articles.data]))
    
    if not kr_topic_ids:
        print("No topics linked to KR articles found.")
        return

    # Get topic details
    response = supabase.table("mvp_topics").select("*").in_("id", kr_topic_ids).execute()
    topics = response.data
    
    print(f"Found {len(topics)} KR-linked topics.")
    
    for topic in topics[:20]:
        print(f"\n[Topic {topic['id']}]")
        print(f"  EN_TITLE: {topic.get('title')}")
        print(f"  KR_TITLE: {topic.get('title_kr')}")
        print(f"  HEADLINE: {topic.get('headline')}")
        print(f"  COUNTRIES: {topic.get('country_count')}")

if __name__ == "__main__":
    debug_topics()
