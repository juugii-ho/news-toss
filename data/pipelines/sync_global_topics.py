import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

def sync_topics():
    print("Syncing mvp2_megatopics to mvp2_global_topics...")
    
    # Fetch all megatopics
    res = supabase.table("mvp2_megatopics").select("*").execute()
    megatopics = res.data
    
    if not megatopics:
        print("No megatopics found.")
        return
        
    print(f"Found {len(megatopics)} megatopics.")
    
    # Insert into global_topics
    # We need to map columns if they differ.
    # Let's inspect global_topics columns first to be safe, or just try insert with matching keys.
    # Based on previous inspection, global_topics was empty, so we can infer columns from error or just try.
    # But wait, inspect_global.py said "Columns: ..." wait, no it said "No data".
    # We don't know columns of global_topics.
    
    # Let's try to fetch one row from global_topics again to see columns? No data.
    # We can try to insert one row and see if it fails on column names.
    # Or better, assume they are similar since one is likely a rename of other.
    
    # Let's try to insert the first megatopic.
    for item in megatopics:
        # Fill defaults for required fields
        if not item.get('title_en'):
            item['title_en'] = item.get('title_ko', 'Untitled')
        if not item.get('intro_ko'):
            item['intro_ko'] = ''
        if not item.get('intro_en'):
            item['intro_en'] = ''
            
        # Remove columns that don't exist in global_topics
        for col in ['category', 'content', 'headline', 'summary', 'keywords', 'stances', 'countries', 'topic_ids', 'total_articles', 'article_count', 'country_count', 'rank', 'is_pinned', 'x', 'y', 'name_en', 'name']:
            if col in item:
                del item[col]
            
        try:
            # Try direct insert
            supabase.table("mvp2_global_topics").upsert(item).execute()
            print(f"Synced {item['id']}")
        except Exception as e:
            print(f"Error syncing {item['id']}: {e}")
            # If error is about missing column, we might need to filter keys.
            
if __name__ == "__main__":
    sync_topics()
