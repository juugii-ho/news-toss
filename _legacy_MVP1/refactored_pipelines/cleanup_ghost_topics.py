import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env.local')

# Use service role key to bypass RLS
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase environment variables missing.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def cleanup_ghost_topics():
    print("Fetching all topics for 2025-11-27...")
    
    # Fetch all topics for the date
    # We need to paginate because there are many
    all_topics = []
    page = 0
    page_size = 1000
    
    while True:
        response = supabase.table("mvp_topics") \
            .select("id, title") \
            .eq("date", "2025-11-27") \
            .range(page * page_size, (page + 1) * page_size - 1) \
            .execute()
            
        if not response.data:
            break
            
        all_topics.extend(response.data)
        page += 1
        
    print(f"Total topics found: {len(all_topics)}")
    
    ghost_ids = []
    
    # Check for articles
    # Doing this in batches to avoid timeout
    batch_size = 100
    for i in range(0, len(all_topics), batch_size):
        batch = all_topics[i:i+batch_size]
        topic_ids = [t['id'] for t in batch]
        
        # Get topics that HAVE articles
        articles = supabase.table("mvp_articles") \
            .select("topic_id") \
            .in_("topic_id", topic_ids) \
            .execute()
            
        active_topic_ids = set(a['topic_id'] for a in articles.data)
        
        # Find ghosts
        for t in batch:
            if t['id'] not in active_topic_ids:
                ghost_ids.append(t['id'])
                
        print(f"Processed {i + len(batch)}/{len(all_topics)} topics. Found {len(ghost_ids)} ghosts so far.")

    print(f"\nTotal ghost topics to delete: {len(ghost_ids)}")
    
    if ghost_ids:
        # Delete in batches
        print("Deleting ghost topics...")
        delete_batch_size = 100
        for i in range(0, len(ghost_ids), delete_batch_size):
            batch_ids = ghost_ids[i:i+delete_batch_size]
            
            # Delete from stats table first due to FK constraint
            supabase.table("mvp_topic_country_stats").delete().in_("topic_id", batch_ids).execute()
            
            # Then delete topic
            supabase.table("mvp_topics").delete().in_("id", batch_ids).execute()
            print(f"Deleted {i + len(batch_ids)}/{len(ghost_ids)}")
            
        print("Cleanup complete!")
    else:
        print("No ghost topics found.")

if __name__ == "__main__":
    cleanup_ghost_topics()
