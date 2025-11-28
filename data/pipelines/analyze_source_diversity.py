import os
import json
from collections import Counter
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv('backend/.env')
supabase: Client = create_client(os.getenv("NEXT_PUBLIC_SUPABASE_URL"), os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY"))

def main():
    print("📊 Analyzing Source Diversity for KR Clusters...")
    
    with open("data/pipelines/clusters_KR_hdbscan.json", "r", encoding="utf-8") as f:
        clusters = json.load(f)
        
    all_ids = []
    for data in clusters.values():
        all_ids.extend(data.get("factual", []) + data.get("critical", []) + data.get("supportive", []))
        
    # Fetch source_name
    id_map = {}
    chunk_size = 100
    for i in range(0, len(all_ids), chunk_size):
        chunk = all_ids[i:i+chunk_size]
        res = supabase.table("mvp2_articles").select("id, source_name").in_("id", chunk).execute()
        for item in res.data:
            id_map[item['id']] = item.get('source_name', 'Unknown')
            
    # Analyze
    print("\n--- Source Dominance Report ---")
    for topic, data in clusters.items():
        ids = data.get("factual", []) + data.get("critical", []) + data.get("supportive", [])
        sources = [id_map.get(aid, 'Unknown') for aid in ids]
        if not sources: continue
        
        counts = Counter(sources)
        top_source, top_count = counts.most_common(1)[0]
        dominance = (top_count / len(sources)) * 100
        
        print(f"Topic: {topic[:30]}... ({len(ids)} articles)")
        print(f"  - Top Source: {top_source} ({top_count}/{len(ids)}, {dominance:.1f}%)")
        if dominance > 50:
            print(f"  ⚠️ DOMINATED by {top_source}")
        else:
            print(f"  ✅ Diverse")
        print("")

if __name__ == "__main__":
    main()
