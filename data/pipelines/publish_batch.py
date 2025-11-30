"""
Publish a batch of topics and megatopics atomically.
This script is called after Step 8 (thumbnails) completes.
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def publish_batch(batch_id):
    """
    Atomically publish a batch:
    1. Unpublish old batches
    2. Publish new batch (both local topics and global megatopics)
    3. Update article linkage for newly published topics
    4. Clean up old unpublished batches
    """
    print(f"Publishing batch: {batch_id}")
    
    try:
        # 1. Unpublish all old batches (both local and global)
        print("  Unpublishing old batches...")
        supabase.table("mvp2_topics").update({
            "is_published": False
        }).eq("is_published", True).execute()
        
        supabase.table("mvp2_megatopics").update({
            "is_published": False
        }).eq("is_published", True).execute()
        
        # 2. Publish new batch (both local and global)
        print(f"  Publishing new batch {batch_id}...")
        topics_result = supabase.table("mvp2_topics").update({
            "is_published": True
        }).eq("batch_id", batch_id).execute()
        
        megatopics_result = supabase.table("mvp2_megatopics").update({
            "is_published": True
        }).eq("batch_id", batch_id).execute()
        
        print(f"  ✅ Published {len(topics_result.data)} local topics")
        print(f"  ✅ Published {len(megatopics_result.data)} global megatopics")
        
        # 3. Update article linkage for newly published topics
        print("  🔗 Updating article linkage...")
        total_linked = 0
        for topic in topics_result.data:
            topic_id = topic['id']
            article_ids = topic.get('article_ids', [])
            if article_ids:
                try:
                    result = supabase.table("mvp2_articles")\
                        .update({"local_topic_id": topic_id})\
                        .in_("id", article_ids)\
                        .execute()
                    if result.data:
                        total_linked += len(result.data)
                except Exception as e:
                    print(f"    ⚠️ Error linking articles for topic {topic_id}: {e}")
        
        print(f"  ✅ Linked {total_linked} articles to local topics")
        
        # 4. Clean up old unpublished batches (older than 48 hours)
        # 4. Clean up old unpublished batches (older than 48 hours)
        # UPDATE: We now KEEP history for time-series analysis.
        # print("  🧹 Cleaning up old unpublished batches...")
        # from datetime import datetime, timedelta
        # cutoff = (datetime.utcnow() - timedelta(hours=48)).isoformat()
        
        # old_topics = supabase.table("mvp2_topics").delete()\
        #     .eq("is_published", False)\
        #     .lt("created_at", cutoff)\
        #     .execute()
            
        # old_megatopics = supabase.table("mvp2_megatopics").delete()\
        #     .eq("is_published", False)\
        #     .lt("created_at", cutoff)\
        #     .execute()
        
        # old_count = len(old_topics.data) + len(old_megatopics.data)
        # if old_count > 0:
        #     print(f"  ✅ Cleaned up {old_count} old unpublished records")
        print("  ℹ️  Skipping cleanup to preserve history (Time-series analysis)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error publishing batch: {e}")
        return False


if __name__ == "__main__":
    batch_id = None
    if len(sys.argv) >= 2:
        batch_id = sys.argv[1]
    
    if not batch_id:
        print("No batch_id provided, checking for pending topics...")
        
        # Check if there are any unpublished topics without batch_id
        # or just take all unpublished topics and assign a new batch_id
        
        # Generate new batch_id (UUID)
        import uuid
        new_batch_id = str(uuid.uuid4())
        
        print(f"  Generating new batch_id: {new_batch_id}")
        
        # Assign batch_id to ALL pending items (both topics and megatopics)
        res_topics = supabase.table("mvp2_topics").update({"batch_id": new_batch_id})\
            .is_("is_published", "null").execute()
        res_topics_false = supabase.table("mvp2_topics").update({"batch_id": new_batch_id})\
            .eq("is_published", False)\
            .is_("batch_id", "null")\
            .execute()
        
        count_topics = len(res_topics.data) + len(res_topics_false.data)
        
        res_mega = supabase.table("mvp2_megatopics").update({"batch_id": new_batch_id})\
            .is_("is_published", "null").execute()
        res_mega_false = supabase.table("mvp2_megatopics").update({"batch_id": new_batch_id})\
            .eq("is_published", False)\
            .is_("batch_id", "null")\
            .execute()
        
        count_mega = len(res_mega.data) + len(res_mega_false.data)
        
        if count_topics > 0 or count_mega > 0:
            print(f"  ✅ Assigned {new_batch_id} to {count_topics} topics and {count_mega} megatopics")
            batch_id = new_batch_id
            
        else:
            # Try to find latest existing if no pending
            res = supabase.table("mvp2_topics").select("batch_id").order("created_at", desc=True).limit(1).execute()
            if res.data and res.data[0].get('batch_id'):
                batch_id = res.data[0]['batch_id']
                print(f"  ⚠️ No pending topics found. Using latest existing batch_id: {batch_id}")
            else:
                print("❌ Could not find any batch_id in database and no pending topics to assign.")
                sys.exit(1)

            
    success = publish_batch(batch_id)
    sys.exit(0 if success else 1)
