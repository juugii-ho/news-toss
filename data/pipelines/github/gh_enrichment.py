import os
import json
import time
import sys
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
env_path = os.path.join(project_root, 'backend', '.env')
load_dotenv(env_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Environment variables missing.")
    exit(1)

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

COUNTRIES = ['AU', 'BE', 'CA', 'CN', 'DE', 'FR', 'UK', 'IT', 'JP', 'KR', 'NL', 'RU', 'US']

def fetch_article_details(article_ids):
    """Fetch details for a list of article IDs"""
    chunk_size = 100
    all_articles = []
    
    for i in range(0, len(article_ids), chunk_size):
        chunk = article_ids[i:i+chunk_size]
        try:
            response = supabase.table("mvp2_articles") \
                .select("id, title_ko, title_en, source_name, published_at") \
                .in_("id", chunk) \
                .execute()
            all_articles.extend(response.data)
        except Exception as e:
            print(f"  ⚠️ Error fetching articles: {e}")
            
    return {a['id']: a for a in all_articles}

def deduplicate_sources(cluster_articles):
    """
    Filter out articles if a single source dominates (>50%).
    Keep only the top 2 latest articles from that source.
    """
    if not cluster_articles: return []
    
    sources = [a.get('source_name', 'Unknown') for a in cluster_articles]
    counts = Counter(sources)
    
    if not counts: return cluster_articles
    
    top_source, top_count = counts.most_common(1)[0]
    total = len(cluster_articles)
    dominance = top_count / total
    
    if dominance > 0.5 and total > 2:
        dominant_articles = [a for a in cluster_articles if a.get('source_name') == top_source]
        other_articles = [a for a in cluster_articles if a.get('source_name') != top_source]
        
        dominant_articles.sort(key=lambda x: x.get('published_at') or '', reverse=True)
        kept_dominant = dominant_articles[:2]
        
        return other_articles + kept_dominant
        
    return cluster_articles

def process_country(country):
    print(f"\n🚀 Starting Source Deduplication for {country}...")
    
    input_file = os.path.join(script_dir, f"clusters_{country}_hdbscan.json")
    output_file = os.path.join(script_dir, f"enriched_topics_{country}.json")
    
    if not os.path.exists(input_file):
        print(f"⚠️ Input file not found: {input_file}. Skipping.")
        return
        
    with open(input_file, "r", encoding="utf-8") as f:
        clusters = json.load(f)
        
    enriched_data = {}
    
    # Collect all IDs to fetch details
    all_ids = []
    for data in clusters.values():
        # Handle both old format (list of IDs) and new format (dict with stances)
        # But gh_clustering.py outputs new format
        stances = data.get("stances", {})
        all_ids.extend(stances.get("factual", []) + stances.get("critical", []) + stances.get("supportive", []))
        
    if not all_ids:
        print("  No articles found in clusters.")
        return

    print(f"  Fetching details for {len(all_ids)} articles...")
    article_map = fetch_article_details(all_ids)
    
    total_clusters = len(clusters)
    print(f"  Processing {total_clusters} clusters...")
    
    for i, (topic_key, data) in enumerate(clusters.items()):
        stances_data = data.get("stances", {})
        stances_result = {"factual": [], "critical": [], "supportive": []}
        has_articles = False
        
        for stance_type in ["factual", "critical", "supportive"]:
            ids = stances_data.get(stance_type, [])
            articles = [article_map.get(aid) for aid in ids if article_map.get(aid)]
            
            # Deduplicate per stance group
            filtered = deduplicate_sources(articles)
            stances_result[stance_type] = [a['id'] for a in filtered]
            
            if filtered:
                has_articles = True
        
        if not has_articles:
            continue
            
        # Preserve metadata from clustering step
        enriched_data[topic_key] = {
            "topic_name_ko": topic_key,
            "summary_ko": "", 
            "keywords": data.get("keywords", []),
            "category": data.get("category", "Unclassified"),
            "stances": stances_result
        }
        
    # Final Save
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Deduplication Complete. Saved {len(enriched_data)} topics to {output_file}")

    # Save to DB
    print(f"Saving enriched topics to Supabase DB (mvp2_topics) for {country}...")
    try:
        # 1. Clear existing topics for this country
        # Note: gh_clustering.py might have inserted them, but we are overwriting with cleaner data
        supabase.table("mvp2_articles").update({"local_topic_id": None}).eq("country_code", country).execute()
        supabase.table("mvp2_topics").delete().eq("country_code", country).execute()
        
        db_rows = []
        article_source_map = {a['id']: a.get('source_name', 'Unknown') for a in article_map.values()}
        
        for topic_name, details in enriched_data.items():
            stances = details['stances']
            article_ids = stances['factual'] + stances['critical'] + stances['supportive']
            
            unique_sources = set()
            for aid in article_ids:
                if aid in article_source_map:
                    unique_sources.add(article_source_map[aid])
            
            db_rows.append({
                "country_code": country,
                "topic_name": topic_name,
                "article_ids": article_ids,
                "article_count": len(article_ids),
                "source_count": len(unique_sources),
                "stances": stances,
                "keywords": details.get('keywords', []),
                "category": details.get('category', 'Unclassified'),
                "created_at": datetime.utcnow().isoformat()
            })
        
        if db_rows:
            batch_size = 50
            for i in range(0, len(db_rows), batch_size):
                batch = db_rows[i:i+batch_size]
                response = supabase.table("mvp2_topics").insert(batch).execute()
                print(f"  Inserted batch {i//batch_size + 1}")
                
                # Link articles
                if response.data:
                    for topic in response.data:
                        topic_id = topic['id']
                        article_ids = topic['article_ids']
                        if article_ids:
                            supabase.table("mvp2_articles") \
                                .update({"local_topic_id": topic_id}) \
                                .in_("id", article_ids) \
                                .execute()
                    print(f"    🔗 Linked articles for batch {i//batch_size + 1}")
                
        print("✅ Saved to DB successfully.")
        
    except Exception as e:
        print(f"❌ Error saving to DB: {e}")

def main():
    print("Starting Enrichment & Deduplication (GitHub Actions Mode)...")
    for country in COUNTRIES:
        process_country(country)
    print("\n🎉 All countries processed.")

if __name__ == "__main__":
    main()
