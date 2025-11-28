import os
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path
from collections import defaultdict

# Load environment variables
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_duplicates():
    print('--- Recent Topics ---')
    res = supabase.table('mvp_topics').select('id, title, title_kr, date, country_count').order('id', desc=True).limit(50).execute()
    
    for t in res.data:
        title_kr = t['title_kr'] if t['title_kr'] else "None"
        print(f"[{t['id']}] {t['date']} | {title_kr[:30]}... | {t['title'][:30]}...")

    print('\n--- Checking for 228 articles ---')
    # Fetch all stats to count articles per topic
    # Note: This might be heavy if there are many topics, but for MVP it's fine.
    # Better to filter by date if possible, but we want to find the specific 228 count.
    
    res_stats = supabase.table('mvp_topic_country_stats').select('topic_id, supportive_count, factual_count, critical_count').execute()
    
    topic_counts = defaultdict(int)
    for s in res_stats.data:
        topic_counts[s['topic_id']] += (s['supportive_count'] + s['factual_count'] + s['critical_count'])
        
    found_duplicates = []
    for tid, count in topic_counts.items():
        if count == 228 or count == 135:
            print(f"Topic {tid}: {count} articles")
            found_duplicates.append(tid)
            
    if found_duplicates:
        print("\n--- Details of Duplicate Candidates ---")
        res_dups = supabase.table('mvp_topics').select('*').in_('id', found_duplicates).execute()
        for t in res_dups.data:
             print(f"[{t['id']}] {t['date']} | {t['title_kr']}")

if __name__ == "__main__":
    check_duplicates()
