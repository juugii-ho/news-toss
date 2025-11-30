#!/usr/bin/env python3
"""
Link articles to their corresponding megatopics based on local_topic_id
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    raise ValueError("Supabase credentials not found")

supabase = create_client(url, key)

def main():
    print("🔗 Linking articles to megatopics...")
    
    # Get all megatopics
    megatopics_response = supabase.from_("mvp2_megatopics").select("id, local_topic_ids").execute()
    megatopics = megatopics_response.data
    
    print(f"Found {len(megatopics)} megatopics")
    
    total_updated = 0
    
    for mega in megatopics:
        mega_id = mega['id']
        local_ids = mega.get('local_topic_ids', [])
        
        if not local_ids:
            print(f"  ⚠️ Megatopic {mega_id} has no local_topic_ids, skipping")
            continue
        
        print(f"  Processing megatopic {mega_id} with {len(local_ids)} local topics...")
        
        # Update all articles that belong to these local topics
        for local_id in local_ids:
            result = supabase.from_("mvp2_articles")\
                .update({"global_topic_id": mega_id})\
                .eq("local_topic_id", local_id)\
                .execute()
            
            if result.data:
                count = len(result.data)
                total_updated += count
                print(f"    ✓ Linked {count} articles from local topic {local_id}")
    
    print(f"\n✅ Done! Linked {total_updated} articles to megatopics")

if __name__ == "__main__":
    main()
