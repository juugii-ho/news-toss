import os
import json
import glob
from dotenv import load_dotenv
from supabase import create_client

# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", "..", "backend", ".env")
load_dotenv(env_path)

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase = create_client(url, key)

def main():
    print("🚀 Linking Articles to Topics...")
    
    # 1. Load all cluster files
    search_pattern = os.path.join(script_dir, "clusters_*_hdbscan.json")
    cluster_files = glob.glob(search_pattern)
    
    print(f"Found {len(cluster_files)} cluster files.")
    
    for fpath in cluster_files:
        print(f"Processing {os.path.basename(fpath)}...")
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Collect all topic names to lookup IDs
        topic_names = list(data.keys())
        
        # Lookup Topic IDs
        name_to_id = {}
        # Batch lookup
        batch_size = 50
        for i in range(0, len(topic_names), batch_size):
            batch = topic_names[i:i+batch_size]
            try:
                res = supabase.table("mvp2_topics").select("id, topic_name").in_("topic_name", batch).execute()
                for row in res.data:
                    name_to_id[row['topic_name']] = row['id']
            except Exception as e:
                print(f"  ⚠️ Lookup failed: {e}")
                
        # Update Articles
        updated_count = 0
        for topic_name, details in data.items():
            topic_id = name_to_id.get(topic_name)
            if not topic_id:
                # Try topic_name_ko if available (sometimes keys match display name)
                # But here keys are usually the name.
                continue
                
            article_ids = []
            article_ids.extend(details.get('factual', []))
            article_ids.extend(details.get('critical', []))
            article_ids.extend(details.get('supportive', []))
            
            if not article_ids:
                continue
                
            # Update articles
            try:
                # We can't do "update where id in list" easily in one go with supabase-py without RPC or loop?
                # Actually we can: .in_('id', article_ids).update({'local_topic_id': topic_id})
                # But article_ids list might be large.
                # Split into chunks of 50
                for i in range(0, len(article_ids), 50):
                    chunk = article_ids[i:i+50]
                    supabase.table("mvp2_articles").update({"local_topic_id": topic_id}).in_("id", chunk).execute()
                updated_count += len(article_ids)
            except Exception as e:
                print(f"  ❌ Update failed for topic {topic_name}: {e}")
                
        print(f"  Linked {updated_count} articles.")

    print("✅ Done.")

if __name__ == "__main__":
    main()
