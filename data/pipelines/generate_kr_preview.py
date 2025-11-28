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

def main():
    print("🚀 Generating Full Korean Cluster Preview...")
    
    file_path = "data/pipelines/clusters_KR_hdbscan.json"
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

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

    # Generate Markdown Content
    md_content = "# 🇰🇷 Korean Cluster Preview (Full)\n\n"
    md_content += f"**Total Topics:** {len(clusters)}\n"
    md_content += f"**Total Articles:** {len(all_ids)}\n\n"
    md_content += "---\n\n"

    # Sort clusters by size
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1].get('factual', []) + x[1].get('critical', []) + x[1].get('supportive', [])), reverse=True)

    for i, (topic, data) in enumerate(sorted_clusters):
        ids = data.get("factual", []) + data.get("critical", []) + data.get("supportive", [])
        md_content += f"## {i+1}. {topic} ({len(ids)} articles)\n"
        
        for article_id in ids:
            article = id_map.get(article_id)
            if article:
                title = article.get('title_ko') or article.get('title_en') or "(No Title)"
                md_content += f"- {title}\n"
            else:
                md_content += f"- (ID: {article_id} not found)\n"
        md_content += "\n"

    # Save to file
    output_path = "korean_clusters_preview.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"✅ Preview saved to {output_path}")

if __name__ == "__main__":
    main()
