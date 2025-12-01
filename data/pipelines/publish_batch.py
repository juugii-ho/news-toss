"""
Publish a batch of topics and megatopics atomically.
This script is called after Step 8 (thumbnails) completes.
"""
import os
import sys
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def publish_latest_24h():
    """
    Atomically publish ALL topics created in the last 24 hours.
    This is a "catch-all" strategy to ensure nothing is missed.
    INCLUDES DEDUPLICATION: Only publishes the LATEST version of each topic name.
    """
    # Generate new batch_id
    new_batch_id = str(uuid.uuid4())
    print(f"🚀 Starting Force Publish (Last 24h) - Batch ID: {new_batch_id}")
    
    try:
        # 1. Calculate time threshold (24 hours ago)
        time_threshold = (datetime.utcnow() - timedelta(hours=12)).isoformat()
        print(f"  Time Threshold: {time_threshold}")

        # 2. Unpublish EVERYTHING first (Clean slate)
        print("  Unpublishing old batches...")
        supabase.table("mvp2_topics").update({"is_published": False}).eq("is_published", True).execute()
        supabase.table("mvp2_megatopics").update({"is_published": False}).eq("is_published", True).execute()
        
        # 3. Fetch Candidates & Deduplicate (Topics)
        print(f"  Fetching candidate topics created after {time_threshold}...")
        
        # Fetch all candidates
        # Note: We need to fetch enough fields to identify duplicates (topic_name, country_code)
        all_topics = supabase.table("mvp2_topics")\
            .select("id, topic_name, country_code, created_at")\
            .gte("created_at", time_threshold)\
            .execute()
            
        if not all_topics.data:
            print("  ⚠️ No topics found in the last 24h.")
        else:
            # Group by (country_code, topic_name) and find latest
            topic_groups = {}
            for t in all_topics.data:
                key = (t['country_code'], t['topic_name'])
                if key not in topic_groups:
                    topic_groups[key] = t
                else:
                    # Keep the one with later created_at
                    if t['created_at'] > topic_groups[key]['created_at']:
                        topic_groups[key] = t
            
            unique_topic_ids = [t['id'] for t in topic_groups.values()]
            print(f"  Found {len(all_topics.data)} candidates -> Deduplicated to {len(unique_topic_ids)} unique topics.")
            
            # Batch Update (Supabase limits 'in_' filter size, so chunk it if needed)
            # Assuming < 1000 topics, one go is usually fine, but let's be safe with 500
            chunk_size = 500
            for i in range(0, len(unique_topic_ids), chunk_size):
                chunk = unique_topic_ids[i:i+chunk_size]
                supabase.table("mvp2_topics").update({
                    "is_published": True,
                    "batch_id": new_batch_id
                }).in_("id", chunk).execute()
                
            print(f"  ✅ Published {len(unique_topic_ids)} unique local topics")
            
            # 4. Update article linkage for newly published topics
            print("  🔗 Updating article linkage...")
            total_linked = 0
            
            # We need to fetch article_ids for the published topics to link them
            # Re-fetch or use what we have? We only have IDs in unique_topic_ids.
            # Let's fetch article_ids for the published ones.
            published_topics_data = supabase.table("mvp2_topics")\
                .select("id, article_ids")\
                .in_("id", unique_topic_ids)\
                .execute()
                
            for topic in published_topics_data.data:
                topic_id = topic['id']
                article_ids = topic.get('article_ids', [])
                if article_ids:
                    try:
                        # Link articles to this topic
                        result = supabase.table("mvp2_articles")\
                            .update({"local_topic_id": topic_id})\
                            .in_("id", article_ids)\
                            .execute()
                        if result.data:
                            total_linked += len(result.data)
                    except Exception as e:
                        print(f"    ⚠️ Error linking articles for topic {topic_id}: {e}")
            print(f"  ✅ Linked {total_linked} articles to local topics")


        # 5. Fetch Candidates & Deduplicate (Megatopics)
        print(f"  Fetching candidate megatopics created after {time_threshold}...")
        all_megas = supabase.table("mvp2_megatopics")\
            .select("id, name, created_at")\
            .gte("created_at", time_threshold)\
            .execute()
            
        if not all_megas.data:
            print("  ⚠️ No megatopics found in the last 24h.")
        else:
            # Group by name and find latest
            mega_groups = {}
            for m in all_megas.data:
                key = m['name']
                if key not in mega_groups:
                    mega_groups[key] = m
                else:
                    if m['created_at'] > mega_groups[key]['created_at']:
                        mega_groups[key] = m
            
            unique_mega_ids = [m['id'] for m in mega_groups.values()]
            print(f"  Found {len(all_megas.data)} candidates -> Deduplicated to {len(unique_mega_ids)} unique megatopics.")
            
            # Batch Update
            for i in range(0, len(unique_mega_ids), chunk_size):
                chunk = unique_mega_ids[i:i+chunk_size]
                supabase.table("mvp2_megatopics").update({
                    "is_published": True,
                    "batch_id": new_batch_id
                }).in_("id", chunk).execute()
                
            print(f"  ✅ Published {len(unique_mega_ids)} unique megatopics")
            
            # 6. Link articles to megatopics
            print("  🔗 Updating megatopic linkage...")
            total_mega_linked = 0
            
            published_megas_data = supabase.table("mvp2_megatopics")\
                .select("id, topic_ids")\
                .in_("id", unique_mega_ids)\
                .execute()
                
            for mega in published_megas_data.data:
                mega_id = mega['id']
                local_topic_ids = mega.get('topic_ids', [])
                if local_topic_ids:
                    try:
                        for local_id in local_topic_ids:
                             result = supabase.from_("mvp2_articles")\
                                .update({"global_topic_id": mega_id})\
                                .eq("local_topic_id", local_id)\
                                .execute()
                             if result.data:
                                total_mega_linked += len(result.data)
                    except Exception as e:
                        print(f"    ⚠️ Error linking articles for megatopic {mega_id}: {e}")

            print(f"  ✅ Linked {total_mega_linked} articles to megatopics")

        return True
        
    except Exception as e:
        print(f"  ❌ Error publishing batch: {e}")
        return False


if __name__ == "__main__":
    # Ignore arguments, just force publish last 24h
    success = publish_latest_24h()
    sys.exit(0 if success else 1)
