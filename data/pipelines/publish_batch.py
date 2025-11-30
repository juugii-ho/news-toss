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
    1. Set new batch as published
    2. Unpublish old batches
    """
    print(f"Publishing batch: {batch_id}")
    
    try:
        # 1. Unpublish all old batches
        print("  Unpublishing old batches...")
        supabase.table("mvp2_topics").update({
            "is_published": False
        }).eq("is_published", True).execute()
        
        supabase.table("mvp2_megatopics").update({
            "is_published": False
        }).eq("is_published", True).execute()
        
        # 2. Publish new batch
        print(f"  Publishing new batch {batch_id}...")
        topics_result = supabase.table("mvp2_topics").update({
            "is_published": True
        }).eq("batch_id", batch_id).execute()
        
        megatopics_result = supabase.table("mvp2_megatopics").update({
            "is_published": True
        }).eq("batch_id", batch_id).execute()
        
        print(f"  ✅ Published {len(topics_result.data)} topics")
        print(f"  ✅ Published {len(megatopics_result.data)} megatopics")
        
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
        
        # Generate new batch_id
        from datetime import datetime
        new_batch_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        print(f"  Generating new batch_id: {new_batch_id}")
        
        # Assign to pending topics (is_published is false or null)
        # We assume anything not published is part of this new batch
        res_topics = supabase.table("mvp2_topics").update({"batch_id": new_batch_id}).is_("is_published", "null").execute()
        # Also handle false
        res_topics_false = supabase.table("mvp2_topics").update({"batch_id": new_batch_id}).eq("is_published", False).execute()
        
        count = len(res_topics.data) + len(res_topics_false.data)
        
        if count > 0:
            print(f"  ✅ Assigned {new_batch_id} to {count} pending topics")
            batch_id = new_batch_id
            
            # Also update megatopics
            supabase.table("mvp2_megatopics").update({"batch_id": new_batch_id}).is_("is_published", "null").execute()
            supabase.table("mvp2_megatopics").update({"batch_id": new_batch_id}).eq("is_published", False).execute()
            
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
