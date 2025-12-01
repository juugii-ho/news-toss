import os
from dotenv import load_dotenv
from supabase import create_client

# Load env
load_dotenv('backend/.env')

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase = create_client(url, key)

def check_state():
    print("🔍 Checking DB State...")
    
    # 1. Check Published Counts
    pub_topics = supabase.table("mvp2_topics").select("count", count="exact").eq("is_published", True).execute()
    pub_mega = supabase.table("mvp2_megatopics").select("count", count="exact").eq("is_published", True).execute()
    
    print(f"  ✅ Published Topics: {pub_topics.count}")
    print(f"  ✅ Published Megatopics: {pub_mega.count}")
    
    # 2. Check Unpublished Counts
    unpub_topics = supabase.table("mvp2_topics").select("count", count="exact").eq("is_published", False).execute()
    unpub_mega = supabase.table("mvp2_megatopics").select("count", count="exact").eq("is_published", False).execute()
    
    print(f"  Draft/Archived Topics: {unpub_topics.count}")
    print(f"  Draft/Archived Megatopics: {unpub_mega.count}")
    
    # 3. Check NULL batch_id (Pending Drafts)
    pending_topics = supabase.table("mvp2_topics").select("count", count="exact").is_("batch_id", "null").execute()
    pending_mega = supabase.table("mvp2_megatopics").select("count", count="exact").is_("batch_id", "null").execute()
    
    print(f"  Pending Topics (No Batch ID): {pending_topics.count}")
    print(f"  Pending Megatopics (No Batch ID): {pending_mega.count}")
    
    # 4. Check Recent Batches
    print("\n  Recent Batches (Topics):")
    recent_batches = supabase.table("mvp2_topics").select("batch_id, created_at, is_published")\
        .order("created_at", desc=True).limit(10).execute()
    
    seen_batches = set()
    for item in recent_batches.data:
        bid = item.get('batch_id')
        if bid and bid not in seen_batches:
            seen_batches.add(bid)
            # Count items in this batch
            c = supabase.table("mvp2_topics").select("count", count="exact").eq("batch_id", bid).execute()
            status = "PUBLISHED" if item['is_published'] else "Unpublished"
            print(f"    - Batch {bid}: {c.count} items ({status}) - {item['created_at']}")

    # 5. Check Published Megatopic Batch & Details
    print("\n  Published Megatopics Details:")
    pub_mega = supabase.table("mvp2_megatopics").select("id, name, created_at, batch_id").eq("is_published", True).execute()
    if pub_mega.data:
        for m in pub_mega.data:
            print(f"    - [{m['created_at']}] {m['name']} (Batch: {m['batch_id']})")
    else:
        print("    - None")

    # 6. Check Thumbnails
    print("\n  Thumbnail Status (Published Topics):")
    pub_topics = supabase.table("mvp2_topics").select("id, thumbnail_url").eq("is_published", True).execute()
    
    total = len(pub_topics.data)
    with_thumb = sum(1 for t in pub_topics.data if t.get('thumbnail_url'))
    print(f"    - Total Published: {total}")
    print(f"    - With Thumbnail: {with_thumb}")
    print(f"    - Missing Thumbnail: {total - with_thumb}")

if __name__ == "__main__":
    check_state()
