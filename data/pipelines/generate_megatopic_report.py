import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", "..", "backend", ".env")
load_dotenv(env_path)

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def main():
    print("🚀 Generating Megatopic Report...")
    
    # 1. Fetch Megatopics
    response = supabase.table("mvp2_megatopics").select("*").order("rank").execute()
    megatopics = response.data
    
    output_lines = ["# 🌍 Global Megatopic Report\n"]
    
    for m in megatopics:
        title = m['name']
        countries = m['countries']
        count = m['total_articles']
        topic_ids = m['topic_ids']
        
        output_lines.append(f"## {m['rank']}. {title}")
        output_lines.append(f"- **Countries**: {', '.join(countries)}")
        output_lines.append(f"- **Total Articles**: {count}")
        output_lines.append(f"- **Category**: {m['category']}")
        output_lines.append("\n### 🔗 Included Local Topics & Articles\n")
        
        # 2. Fetch Local Topics
        if not topic_ids:
            output_lines.append("  (No topics linked)\n")
            continue
            
        topics_response = supabase.table("mvp2_topics").select("id, topic_name, country_code, article_ids").in_("id", topic_ids).execute()
        topics = topics_response.data
        
        for t in topics:
            t_name = t['topic_name']
            t_country = t['country_code']
            article_ids = t['article_ids']
            
            output_lines.append(f"#### [{t_country}] {t_name}")
            
            # 3. Fetch Articles (Limit 5 per topic to keep it readable)
            if article_ids:
                articles_response = supabase.table("mvp2_articles").select("title_ko, title_en").in_("id", article_ids[:5]).execute()
                articles = articles_response.data
                for a in articles:
                    a_title = a.get('title_ko') or a.get('title_en')
                    output_lines.append(f"- {a_title}")
                if len(article_ids) > 5:
                    output_lines.append(f"- ... (and {len(article_ids)-5} more)")
            output_lines.append("")
            
        output_lines.append("---\n")
        
    # Save to file
    output_path = os.path.join(script_dir, "..", "..", "outputs", "megatopic_report.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
    print(f"✅ Report saved to {output_path}")

if __name__ == "__main__":
    main()
