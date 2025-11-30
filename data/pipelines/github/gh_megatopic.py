import os
# GRPC DNS Resolver Workaround
os.environ["GRPC_DNS_RESOLVER"] = "native"

import json
import glob
import time
import numpy as np
import google.generativeai as genai
from sklearn.cluster import HDBSCAN, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
env_path = os.path.join(project_root, 'backend', '.env')
load_dotenv(env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
    exit(1)

# Load Local Model (Multilingual)
print("⏳ Loading Local Embedding Model (paraphrase-multilingual-MiniLM-L12-v2)...")
embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_embeddings(texts, batch_size=100):
    """Generate embeddings locally using sentence-transformers"""
    print(f"Generating embeddings locally for {len(texts)} topics (Batch Size: {batch_size})...")
    embeddings = embed_model.encode(
        texts, 
        batch_size=batch_size, 
        show_progress_bar=True, 
        normalize_embeddings=True
    )
    return embeddings

def main():
    print("🚀 Starting Megatopic Analysis (GitHub Actions Mode)...")
    
    # 1. Load all enriched topic files
    search_pattern = os.path.join(script_dir, "enriched_topics_*.json")
    cluster_files = glob.glob(search_pattern)
    
    if not cluster_files:
        print("⚠️ No enriched topics found. Falling back to raw clusters...")
        search_pattern = os.path.join(script_dir, "clusters_*_hdbscan.json")
        cluster_files = glob.glob(search_pattern)
    
    all_topics = []
    
    print(f"Loading enriched topics from {len(cluster_files)} files...")
    for fpath in cluster_files:
        try:
            filename = os.path.basename(fpath)
            if "enriched_topics_" in filename:
                country_code = filename.replace("enriched_topics_", "").replace(".json", "")
            else:
                country_code = filename.split('_')[1]
            
            country = country_code
        except Exception:
            print(f"Skipping malformed filename: {fpath}")
            continue
            
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            for topic_name, details in data.items():
                display_name = details.get("topic_name_ko", topic_name)
                
                # Calculate size correctly
                # Calculate size correctly
                stances = details.get('stances', details)
                size = len(stances.get('factual', [])) + \
                       len(stances.get('critical', [])) + \
                       len(stances.get('supportive', []))
                       
                topic_id = details.get('topic_id')
                
                all_topics.append({
                    "name": display_name,
                    "country": country,
                    "size": size,
                    "id": topic_id, 
                    "keywords": details.get('keywords', []),
                    "category": details.get('category', 'Unclassified')
                })

    # 1.5 Lookup missing topic IDs from DB
    print("Looking up missing topic IDs from DB...")
    
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    supabase_lookup = create_client(url, key)
    
    names_to_lookup = [t['name'] for t in all_topics if not t['id']]
    
    if names_to_lookup:
        batch_size = 50
        name_to_id_map = {}
        
        for i in range(0, len(names_to_lookup), batch_size):
            batch = names_to_lookup[i:i+batch_size]
            try:
                response = supabase_lookup.table("mvp2_topics").select("id, topic_name").in_("topic_name", batch).execute()
                for row in response.data:
                    name_to_id_map[row['topic_name']] = row['id']
            except Exception as e:
                print(f"  ⚠️ Lookup failed for batch {i}: {e}")
                
        for t in all_topics:
            if not t['id'] and t['name'] in name_to_id_map:
                t['id'] = name_to_id_map[t['name']]
                
    count_with_id = sum(1 for t in all_topics if t.get('id'))
    print(f"DEBUG: {count_with_id} / {len(all_topics)} topics have IDs after lookup.")
    print(f"Total Local Topics Found: {len(all_topics)}")
    
    if not all_topics:
        print("No topics found. Run clustering first.")
        return

    # 2. Embed Topic Names
    topic_names = [t['name'] for t in all_topics]
    embeddings = get_embeddings(topic_names)
    
    # 3. Cluster Topics (Megatopics)
    print("Clustering into Megatopics (AgglomerativeClustering)...")
    
    clusterer = AgglomerativeClustering(
        n_clusters=None, 
        distance_threshold=0.20, 
        metric='cosine', 
        linkage='average'
    )
    labels = clusterer.fit_predict(embeddings)
    
    n_clusters = len(set(labels))
    print(f"Found {n_clusters} Megatopics.")
    
    megatopics = {}
    for i, label in enumerate(labels):
        if label == -1: continue
        if label not in megatopics: megatopics[label] = []
        megatopics[label].append(all_topics[i])
        
    # 4. Name and Format Megatopics
    final_output = []
    
    genai.configure(api_key=GOOGLE_API_KEY)
    generation_config = {
        "temperature": 0.3,
        "top_p": 0.8,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json",
    }
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        generation_config=generation_config
    )

    def generate_megatopic_label(topics, default_name):
        input_text = "\n".join([f"- [ID:{i}] [{t['country']}] {t['name']} (Articles: {t['size']})" for i, t in enumerate(topics)])
        
        prompt = f"""
Role: Global News Editor
Task: Analyze the following list of local news topics and identify the SINGLE dominant global news theme.
If the list contains multiple unrelated themes (e.g. "Cyber Attack" AND "Shooting Incident"), choose the one with the most articles/countries and mark the others as Outliers.

Input (Local Topics):
{input_text}

Requirements:
1. **Megatopic Name**: Create a broad, neutral, global headline in KOREAN for the DOMINANT theme.
2. **Keywords**: Extract 3-5 global keywords (KOREAN).
3. **Category**: Classify into one of: Politics, Economy, Society, World, Tech, Culture, Sports.
4. **Outliers**: List the IDs (0-indexed) of topics that do NOT belong to the DOMINANT theme.

Output JSON:
{{
  "megatopic_name": "Global Headline",
  "keywords": ["Key1", "Key2"],
  "category": "Category",
  "outliers": [1, 3]
}}
"""
        try:
            response = model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            print(f"    ⚠️ Global Labeling failed: {e}")
            return {
                "megatopic_name": default_name,
                "keywords": [],
                "category": "Unclassified",
                "outliers": []
            }

    print(f"Processing {len(megatopics)} Megatopics...")
    
    for i, (label_id, items) in enumerate(megatopics.items()):
        items.sort(key=lambda x: x['size'], reverse=True)
        default_name = items[0]['name']
        
        temp_countries = list(set([t['country'] for t in items]))
        temp_total_articles = sum([t['size'] for t in items])
        
        if len(temp_countries) < 2 and temp_total_articles < 10:
            continue
        
        llm_result = None
        retries = 3
        for attempt in range(retries):
            try:
                llm_result = generate_megatopic_label(items, default_name)
                break
            except Exception as e:
                time.sleep(5 * (attempt + 1))
        
        if not llm_result:
            llm_result = {
                "megatopic_name": default_name,
                "keywords": [],
                "category": "Unclassified"
            }
        
        megatopic_name = llm_result.get('megatopic_name', default_name)
        keywords = llm_result.get('keywords', [])
        category = llm_result.get('category', 'Unclassified')
        outliers = llm_result.get('outliers', [])
        
        if outliers:
            filtered_items = [item for i, item in enumerate(items) if i not in outliers]
        else:
            filtered_items = items
            
        if not filtered_items:
            filtered_items = items
        
        countries = list(set([t['country'] for t in filtered_items]))
        total_articles = sum([t['size'] for t in filtered_items])
        
        if len(countries) < 2 and total_articles < 10:
            continue
        
        print(f"  [{i+1}/{len(megatopics)}] {megatopic_name} ({len(countries)} countries, {total_articles} articles)")
        
        final_output.append({
            "megatopic_name": megatopic_name,
            "countries": countries,
            "total_articles": total_articles,
            "topic_ids": [t['id'] for t in filtered_items if t.get('id')],
            "keywords": keywords,
            "category": category,
            "created_at": datetime.utcnow().isoformat()
        })
        time.sleep(1)

    final_output.sort(key=lambda x: (len(x['countries']), x['total_articles']), reverse=True)
    
    output_file = os.path.join(script_dir, "megatopics.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Megatopic Analysis Complete. Saved to {output_file}")
    
    # 5. Save to DB
    print(f"Saving {len(final_output)} megatopics to Supabase...")
    
    try:
        supabase: Client = create_client(url, key)
        supabase.table("mvp2_megatopics").delete().neq("name", "______").execute()
        
        rows = []
        for i, item in enumerate(final_output):
            rows.append({
                "name": item['megatopic_name'],
                "title_ko": item['megatopic_name'],
                "summary": f"Global coverage across {len(item['countries'])} countries.", 
                "countries": item['countries'],
                "total_articles": item['total_articles'],
                "article_count": item['total_articles'],
                "country_count": len(item['countries']),
                "rank": i + 1,
                "is_pinned": False,
                "topic_ids": item['topic_ids'],
                "keywords": item['keywords'],
                "category": item['category'],
                "content": item['megatopic_name'] + "\n" + f"Global coverage across {len(item['countries'])} countries.", 
                "created_at": item['created_at']
            })
            
        batch_size = 50
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            supabase.table("mvp2_megatopics").insert(batch).execute()
            print(f"  Inserted batch {i//batch_size + 1}")
            
        print("✅ Saved to DB successfully.")
        
    except Exception as e:
        print(f"❌ Error saving to DB: {e}")

if __name__ == "__main__":
    main()
