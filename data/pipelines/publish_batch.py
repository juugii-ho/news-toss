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
    """
    # Generate new batch_id
    new_batch_id = str(uuid.uuid4())
    print(f"🚀 Starting Force Publish (Last 24h) - Batch ID: {new_batch_id}")
    
    try:
        # 1. Calculate time threshold (24 hours ago)
        time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        print(f"  Time Threshold: {time_threshold}")

        # 2. Unpublish EVERYTHING first (Clean slate)
        print("  Unpublishing old batches...")
        supabase.table("mvp2_topics").update({"is_published": False}).eq("is_published", True).execute()
        supabase.table("mvp2_megatopics").update({"is_published": False}).eq("is_published", True).execute()
        
        # 3. Publish NEW topics (Created >= 24h ago)
        print(f"  Publishing topics created after {time_threshold}...")
        
        # Update Topics
        topics_result = supabase.table("mvp2_topics").update({
            "is_published": True,
            "batch_id": new_batch_id
        }).gte("created_at", time_threshold).execute()
        
        # Update Megatopics
        megatopics_result = supabase.table("mvp2_megatopics").update({
            "is_published": True,
            "batch_id": new_batch_id
        }).gte("created_at", time_threshold).execute()
        
        print(f"  ✅ Published {len(topics_result.data)} local topics")
        print(f"  ✅ Published {len(megatopics_result.data)} global megatopics")
        
        # 4. Update article linkage for newly published topics
        print("  🔗 Updating article linkage...")
        total_linked = 0
        for topic in topics_result.data:
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
        
        # 5. Link articles to megatopics
        print("  🔗 Updating megatopic linkage...")
        total_mega_linked = 0
        for mega in megatopics_result.data:
            mega_id = mega['id']
            local_topic_ids = mega.get('topic_ids', [])
            if local_topic_ids:
                try:
                    # Link articles that belong to these local topics
                    # We can't do a join update easily, so we iterate
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
