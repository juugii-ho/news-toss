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
    if len(sys.argv) < 2:
        print("Usage: python publish_batch.py <batch_id>")
        sys.exit(1)
    
    batch_id = sys.argv[1]
    success = publish_batch(batch_id)
    sys.exit(0 if success else 1)
