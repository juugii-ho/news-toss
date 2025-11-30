import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("backend/.env")
load_dotenv(".env.local")
load_dotenv(".env")

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

def check_linkage():
    print("Checking linkage between mvp2_megatopics and mvp2_articles...")
    
    # Get a few megatopic IDs
    res_mega = supabase.table("mvp2_megatopics").select("id, title_ko").limit(5).execute()
    megatopics = res_mega.data
    
    if not megatopics:
        print("No megatopics found.")
        return

    for m in megatopics:
        mid = m['id']
        print(f"\nMegatopic: {m['title_ko']} ({mid})")
        
        # Check articles with this global_topic_id
        res_articles = supabase.table("mvp2_articles").select("id, local_topic_id").eq("global_topic_id", mid).limit(5).execute()
        articles = res_articles.data
        
        print(f"  Linked Articles: {len(articles)}")
        if articles:
            print(f"  Sample Article IDs: {[a['id'] for a in articles]}")
            print(f"  Sample Local Topic IDs: {[a['local_topic_id'] for a in articles]}")
        else:
            print("  ❌ No articles linked to this megatopic.")

if __name__ == "__main__":
    check_linkage()
