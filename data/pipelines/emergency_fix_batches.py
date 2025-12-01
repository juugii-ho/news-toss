import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

# Load env
load_dotenv('backend/.env')

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase = create_client(url, key)

def emergency_fix():
    print("🚑 Starting Emergency Batch Fix...")
    
    # 1. Define time window (last 2 hours)
    cutoff = (datetime.utcnow() - timedelta(hours=2)).isoformat()
    print(f"  Targeting items created after: {cutoff}")
    
    # 2. Generate Unified Batch ID
    unified_batch_id = str(uuid.uuid4())
    print(f"  Generated Unified Batch ID: {unified_batch_id}")
    
    # 3. Update Topics
    print("  Fixing Topics...")
    topics_res = supabase.table("mvp2_topics").update({
        "batch_id": unified_batch_id,
        "is_published": True
    }).gt("created_at", cutoff).execute()
    print(f"    ✅ Updated & Published {len(topics_res.data)} topics")
    
    # 4. Update Megatopics
    print("  Fixing Megatopics...")
    mega_res = supabase.table("mvp2_megatopics").update({
        "batch_id": unified_batch_id,
        "is_published": True
    }).gt("created_at", cutoff).execute()
    print(f"    ✅ Updated & Published {len(mega_res.data)} megatopics")
    
    # 5. Unpublish Older Items (Cleanup)
    print("  Cleaning up old items...")
    
    # Unpublish topics NOT in the new batch
    old_topics = supabase.table("mvp2_topics").update({
        "is_published": False
    }).neq("batch_id", unified_batch_id).eq("is_published", True).execute()
    print(f"    🧹 Unpublished {len(old_topics.data)} old topics")
    
    # Unpublish megatopics NOT in the new batch
    old_mega = supabase.table("mvp2_megatopics").update({
        "is_published": False
    }).neq("batch_id", unified_batch_id).eq("is_published", True).execute()
    print(f"    🧹 Unpublished {len(old_mega.data)} old megatopics")
    
    # 6. Link Articles
    print("  Linking articles...")
    total_linked = 0
    for topic in topics_res.data:
        topic_id = topic['id']
        article_ids = topic.get('article_ids', [])
        if article_ids:
            try:
                res = supabase.table("mvp2_articles")\
                    .update({"local_topic_id": topic_id})\
                    .in_("id", article_ids)\
                    .execute()
                if res.data:
                    total_linked += len(res.data)
            except Exception as e:
                print(f"    ⚠️ Error linking articles for topic {topic_id}: {e}")
    print(f"    ✅ Linked {total_linked} articles")

    print("✅ Emergency Fix Complete. Site should be live.")

if __name__ == "__main__":
    emergency_fix()
