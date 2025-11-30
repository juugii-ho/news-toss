import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Need service role for updates

if not url or not key:
    print("Error: Service role key required for updates.")
    exit(1)

supabase = create_client(url, key)

def fix_links():
    print("Starting article link fix...")
    
    # 1. Fix Local Topic Links
    print("Fetching local topics...")
    # Pagination might be needed for large datasets, but for MVP/debugging fetch all is okay-ish or use range
    # Let's fetch in chunks
    
    page = 0
    size = 100
    total_updated = 0
    
    while True:
        res = supabase.table("mvp2_topics").select("id, article_ids").range(page*size, (page+1)*size - 1).execute()
        topics = res.data
        if not topics:
            break
            
        for topic in topics:
            tid = topic['id']
            aids = topic.get('article_ids')
            if not aids:
                continue
                
            # Update articles
            # We can't do "update where id in list" easily with one REST call unless we use a custom RPC or loop.
            # Looping is slow but safe for this fix script.
            # Actually, we can use "in" filter for update? No, update acts on filtered rows.
            
            try:
                # Update all articles in this topic
                # supabase.table("mvp2_articles").update({"local_topic_id": tid}).in_("id", aids).execute()
                # The above is the correct way.
                
                r = supabase.table("mvp2_articles").update({"local_topic_id": tid}).in_("id", aids).execute()
                # count is not always returned in update response depending on headers, but let's assume it works.
                # print(f"Updated local topic {tid} -> {len(aids)} articles")
                total_updated += len(aids)
            except Exception as e:
                print(f"Error updating topic {tid}: {e}")
                
        page += 1
        print(f"Processed local topics page {page}")

    print(f"Finished local links. Total articles targeted: {total_updated}")

    # 2. Fix Global Topic Links
    print("Fetching global topics...")
    # Assuming table name is mvp2_global_topics based on previous context, but checking schema said mvp2_megatopics.
    # Let's try mvp2_global_topics first as per recent code edits.
    
    table_name = "mvp2_megatopics"
    try:
        supabase.table(table_name).select("id").limit(1).execute()
    except:
        print(f"Error accessing {table_name}")
        return

    page = 0
    total_global = 0
    
    while True:
        res = supabase.table(table_name).select("id, topic_ids").range(page*size, (page+1)*size - 1).execute()
        gtopics = res.data
        if not gtopics:
            break
            
        for gtopic in gtopics:
            gid = gtopic['id']
            tids = gtopic.get('topic_ids') # Array of local topic IDs
            if not tids:
                continue
                
            try:
                # Update articles where local_topic_id is in tids
                # supabase.table("mvp2_articles").update({"global_topic_id": gid}).in_("local_topic_id", tids).execute()
                
                r = supabase.table("mvp2_articles").update({"global_topic_id": gid}).in_("local_topic_id", tids).execute()
                # print(f"Updated global topic {gid} -> articles in {len(tids)} local topics")
                total_global += 1
            except Exception as e:
                print(f"Error updating global topic {gid}: {e}")
                
        page += 1
        print(f"Processed global topics page {page}")
        
    print("Finished global links.")

if __name__ == "__main__":
    fix_links()
