import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_recent_batches():
    print("Checking recent batches...")
    
    cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    
    res = supabase.table("mvp2_topics") \
        .select("batch_id, country_code, created_at, is_published") \
        .gte("created_at", cutoff) \
        .execute()
        
    batches = {}
    for t in res.data:
        bid = t['batch_id']
        if bid not in batches:
            batches[bid] = {'countries': set(), 'count': 0, 'published': False}
        batches[bid]['countries'].add(t['country_code'])
        batches[bid]['count'] += 1
        if t['is_published']:
            batches[bid]['published'] = True
            
    print(f"\nFound {len(batches)} batches in last 24h:")
    for bid, data in batches.items():
        print(f"Batch {bid}:")
        print(f"  - Countries: {list(data['countries'])}")
        print(f"  - Topics: {data['count']}")
        print(f"  - Published: {data['published']}")

if __name__ == "__main__":
    check_recent_batches()
