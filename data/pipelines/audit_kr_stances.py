import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv('backend/.env')
load_dotenv('.env.local')
load_dotenv('.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Environment variables missing.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    print("Fetching recent KR topics...")
    
    # Fetch recent KR topics (last 48 hours)
    time_threshold = (datetime.utcnow() - timedelta(hours=48)).isoformat()
    
    response = supabase.table("mvp2_topics") \
        .select("*") \
        .eq("country_code", "KR") \
        .gte("created_at", time_threshold) \
        .order("created_at", desc=True) \
        .execute()
        
    topics = response.data
    print(f"Found {len(topics)} topics.")
    
    if not topics:
        print("No topics found.")
        return

    # Collect all article IDs
    all_article_ids = []
    for t in topics:
        stances = t.get('stances', {})
        if isinstance(stances, dict):
            all_article_ids.extend(stances.get('factual', []))
            all_article_ids.extend(stances.get('critical', []))
            all_article_ids.extend(stances.get('supportive', []))
            
    # Fetch article details
    print(f"Fetching details for {len(all_article_ids)} articles...")
    article_map = {}
    
    # Chunking
    chunk_size = 100
    for i in range(0, len(all_article_ids), chunk_size):
        chunk = all_article_ids[i:i+chunk_size]
        if not chunk: continue
        
        res = supabase.table("mvp2_articles") \
            .select("id, title_ko, title_en, source_name") \
            .in_("id", chunk) \
            .execute()
            
        for a in res.data:
            article_map[a['id']] = a

    # Generate Markdown
    md_output = "# 🇰🇷 KR Stance Classification Audit\n\n"
    md_output += f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md_output += f"Total Topics: {len(topics)}\n\n"
    
    for t in topics:
        md_output += f"## {t['topic_name']}\n"
        md_output += f"- **ID**: `{t['id']}`\n"
        md_output += f"- **Created**: {t['created_at']}\n\n"
        
        stances = t.get('stances', {})
        if not isinstance(stances, dict):
            md_output += "> ⚠️ Invalid stance data format\n\n"
            continue
            
        for stance_type in ['supportive', 'critical', 'factual']:
            ids = stances.get(stance_type, [])
            icon = "🟢" if stance_type == 'supportive' else "🔴" if stance_type == 'critical' else "🔵"
            label = "Supportive (옹호/긍정)" if stance_type == 'supportive' else "Critical (비판/부정)" if stance_type == 'critical' else "Factual (중립/사실)"
            
            md_output += f"### {icon} {label}\n"
            if not ids:
                md_output += "_No articles_\n\n"
                continue
                
            for aid in ids:
                article = article_map.get(aid)
                if article:
                    title = article.get('title_ko') or article.get('title_en') or "No Title"
                    source = article.get('source_name') or "Unknown Source"
                    md_output += f"- **[{source}]** {title}\n"
                else:
                    md_output += f"- `Unknown Article ID: {aid}`\n"
            md_output += "\n"
            
        md_output += "---\n\n"
        
    # Save to file
    output_path = "audit_kr_stances.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_output)
        
    print(f"✅ Audit report saved to {output_path}")

if __name__ == "__main__":
    main()
