import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Environment variables missing.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

import sys

def main():
    # Default to GB if no argument
    COUNTRY = sys.argv[1] if len(sys.argv) > 1 else 'GB'
    file_path = f"data/pipelines/clusters_{COUNTRY}_hdbscan.json"
    
    print(f"Loading clusters from {file_path}...")
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    # Load clusters
    with open(file_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    # Collect all IDs
    all_ids = []
    for topic, data in clusters.items():
        all_ids.extend(data.get("factual", []))
        all_ids.extend(data.get("critical", []))
        all_ids.extend(data.get("supportive", []))

    # Fetch titles from Supabase in chunks
    print(f"Fetching titles for {len(all_ids)} articles...")
    
    chunk_size = 100
    id_map = {}
    
    for i in range(0, len(all_ids), chunk_size):
        chunk = all_ids[i:i + chunk_size]
        try:
            response = supabase.table("mvp2_articles").select("id, title_ko, title_en").in_("id", chunk).execute()
            for item in response.data:
                id_map[item['id']] = item
        except Exception as e:
            print(f"⚠️ Error fetching chunk {i}: {e}")

    # Print Preview (All non-empty clusters)
    count = 0
    for topic, data in clusters.items():
        # if count >= 5: break # Show all as requested
        
        ids = data.get("factual", []) + data.get("critical", []) + data.get("supportive", [])
        if not ids: continue
        
        print(f"\n==================================================")
        print(f"📂 TOPIC: {topic}")
        print(f"==================================================")
        
        for article_id in ids:
            article = id_map.get(article_id)
            if article:
                title = article.get('title_ko') or article.get('title_en') or "(No Title)"
                print(f" - {title}")
            else:
                print(f" - (ID: {article_id} not found)")
        
        count += 1

if __name__ == "__main__":
    main()
