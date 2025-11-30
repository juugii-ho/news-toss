#!/usr/bin/env python3
"""
Generate country-wise topic summary reports with article titles
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", "..", "backend", ".env")
load_dotenv(env_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get all cluster files
cluster_files = [f for f in os.listdir(script_dir) if f.startswith('clusters_') and f.endswith('_hdbscan.json')]

print(f"Found {len(cluster_files)} cluster files")

# Output directory
output_dir = os.path.join(script_dir, "..", "..", "outputs", "topic_summaries")
os.makedirs(output_dir, exist_ok=True)

for cluster_file in sorted(cluster_files):
    # Extract country code
    country_code = cluster_file.split('_')[1]
    
    # Load cluster data
    with open(os.path.join(script_dir, cluster_file), 'r', encoding='utf-8') as f:
        topics = json.load(f)
    
    # Generate summary
    summary_lines = []
    summary_lines.append(f"# {country_code} 토픽 요약")
    summary_lines.append(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append(f"총 토픽 수: {len(topics)}")
    summary_lines.append("")
    summary_lines.append("---")
    summary_lines.append("")
    
    # Sort topics by article count (descending)
    sorted_topics = sorted(topics.items(), key=lambda x: len(x[1].get('factual', [])) + len(x[1].get('critical', [])) + len(x[1].get('supportive', [])), reverse=True)
    
    for i, (topic_name, topic_data) in enumerate(sorted_topics, 1):
        # Calculate total articles
        total_articles = len(topic_data.get('factual', [])) + len(topic_data.get('critical', [])) + len(topic_data.get('supportive', []))
        
        summary_lines.append(f"## {i}. {topic_name}")
        summary_lines.append(f"**기사 수**: {total_articles}개")
        
        # Keywords
        keywords = topic_data.get('keywords', [])
        if keywords:
            summary_lines.append(f"**키워드**: {', '.join(keywords)}")
        
        # Category
        category = topic_data.get('category', 'Unclassified')
        summary_lines.append(f"**카테고리**: {category}")
        summary_lines.append("")
        
        # Get article titles from DB
        all_article_ids = topic_data.get('factual', []) + topic_data.get('critical', []) + topic_data.get('supportive', [])
        
        if all_article_ids:
            summary_lines.append("### 기사 목록:")
            
            # Fetch articles from DB
            try:
                articles_response = supabase.table("mvp2_articles").select("id, title_ko, title_en, title_original").in_("id", all_article_ids).execute()
                articles = articles_response.data
                
                # Create a map for quick lookup
                article_map = {a['id']: a for a in articles}
                
                # List articles in order
                for article_id in all_article_ids:
                    article = article_map.get(article_id)
                    if article:
                        # Prefer Korean title, fallback to English, then original
                        title = article.get('title_ko') or article.get('title_en') or article.get('title_original', 'Unknown')
                        summary_lines.append(f"- {title}")
                
            except Exception as e:
                summary_lines.append(f"- (기사 제목 로드 실패: {e})")
        
        summary_lines.append("")
        summary_lines.append("---")
        summary_lines.append("")
    
    # Save summary
    output_file = os.path.join(output_dir, f"{country_code}_topics.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))
    
    print(f"✅ {country_code}: {len(topics)} topics → {output_file}")

print(f"\n✅ All summaries saved to {output_dir}")
