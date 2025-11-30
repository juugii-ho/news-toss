import os
import json
import time
import sys
import numpy as np
import gc
from datetime import datetime, timedelta
from sklearn.cluster import KMeans, HDBSCAN
from sklearn.metrics.pairwise import cosine_distances
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client, Client

# Fix gRPC DNS resolution issue
os.environ['GRPC_DNS_RESOLVER'] = 'native'

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
env_path = os.path.join(project_root, 'backend', '.env')
load_dotenv(env_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not GOOGLE_API_KEY:
    print("Error: Environment variables missing.")
    exit(1)

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GOOGLE_API_KEY)

# Model configuration
generation_config = {
    "temperature": 0.3,
    "top_p": 0.8,
    "max_output_tokens": 4096,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    generation_config=generation_config,
    safety_settings={
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
    }
)

# Load Local Model (Multilingual) - Load ONCE
print("⏳ Loading Local Embedding Model (paraphrase-multilingual-MiniLM-L12-v2)...")
embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

COUNTRIES = ['AU', 'BE', 'CA', 'CN', 'DE', 'FR', 'UK', 'IT', 'JP', 'KR', 'NL', 'RU', 'US']

def fetch_articles(country_code):
    print(f"Fetching articles for {country_code} (Last 24 hours)...")
    time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    response = supabase.table("mvp2_articles") \
        .select("id, title_en, title_ko, published_at, source_name") \
        .eq("country_code", country_code) \
        .not_.is_("title_en", "null") \
        .gte("published_at", time_threshold) \
        .execute()
    return response.data

def get_embeddings(texts, batch_size=32):
    return embed_model.encode(texts, batch_size=batch_size, show_progress_bar=True, normalize_embeddings=True)

def generate_topic_label(cluster_articles, centroid_title):
    article_map = {i+1: a for i, a in enumerate(cluster_articles)}
    input_text = "\n".join([f"{i+1}. {a['title_en']}" for i, a in enumerate(cluster_articles)])
    
    prompt = f"""
Role: Professional News Editor & Data Analyst
Task: Analyze the following news articles (clustered by similarity) and provide a structured summary.

Articles:
{input_text}

Requirements:
1. **Topic Name**: Create a concise, neutral, descriptive topic name in KOREAN.
   - **PROHIBITION**: Do NOT use generic category names like "경제 동향", "사건 사고", "정치 이슈".
   - **REQUIREMENT**: Use specific event-based names like "비트코인 10만 달러 돌파", "강남역 묻지마 폭행 사건".
1. **Topic Name**: Create a concise, neutral headline in KOREAN for the DOMINANT topic.
2. **Keywords**: Extract 3-5 keywords (KOREAN).
3. **Category**: Classify into one of: Politics, Economy, Society, World, Tech, Culture, Sports.
4. **Stances**: Classify indices (0-indexed) into Factual, Critical, Supportive based on the DOMINANT topic.
5. **Outliers**: List indices of articles that do NOT belong to the DOMINANT topic.

Output JSON:
{{
  "topic_name": "Headline",
  "keywords": ["Key1", "Key2"],
  "category": "Category",
  "stances": {{
    "factual": [0, 1],
    "critical": [2],
    "supportive": []
  }},
  "outliers": [3, 4]
}}
"""
    retries = 3
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            result = json.loads(text)
            
            def map_indices_to_ids(indices, article_map):
                mapped_ids = []
                for idx in indices:
                    try:
                        idx_int = int(idx)
                        if idx_int in article_map:
                            mapped_ids.append(article_map[idx_int]['id'])
                    except:
                        continue
                return mapped_ids

            raw_stances = result.get("stances", {})
            mapped_stances = {
                "factual": map_indices_to_ids(raw_stances.get("factual", []), article_map),
                "critical": map_indices_to_ids(raw_stances.get("critical", []), article_map),
                "supportive": map_indices_to_ids(raw_stances.get("supportive", []), article_map)
            }
            mapped_outliers = map_indices_to_ids(result.get('outliers', []), article_map)
            
            all_classified_ids = set(mapped_stances["factual"] + mapped_stances["critical"] + mapped_stances["supportive"] + mapped_outliers)
            for a in cluster_articles:
                if a['id'] not in all_classified_ids:
                    mapped_stances["factual"].append(a['id'])
            
            return {
                "topic_name": result.get("topic_name", centroid_title),
                "keywords": result.get("keywords", []),
                "category": result.get("category", "Unclassified"),
                "stances": mapped_stances,
                "outliers": mapped_outliers
            }
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                print(f"    ⚠️ Labeling failed: {e}")
                
    return {
        "topic_name": f"{centroid_title} (자동 생성)",
        "keywords": [],
        "category": "Unclassified",
        "stances": {"factual": [a['id'] for a in cluster_articles], "critical": [], "supportive": []}
    }

def process_country(country):
    print(f"\n🚀 Processing {country}...")
    articles = fetch_articles(country)
    if not articles:
        print(f"No articles found for {country}.")
        return

    titles = [a['title_en'] for a in articles]
    
    # 1. Generate Embeddings
    embeddings = get_embeddings(titles)
    
    # 2. HDBSCAN Clustering
    n_articles = len(embeddings)
    if n_articles > 500:
        min_cluster_size = 5; min_samples = 5; epsilon = 0.0
    elif n_articles > 100:
        min_cluster_size = 3; min_samples = 3; epsilon = 0.0
    elif n_articles < 50:
        min_cluster_size = 2; min_samples = 2; epsilon = 0.0
    else:
        min_cluster_size = 3; min_samples = 3; epsilon = 0.0

    clusterer = HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples, cluster_selection_epsilon=epsilon, metric='euclidean')
    labels = clusterer.fit_predict(embeddings)
    
    clusters = {}
    for i, label in enumerate(labels):
        if label == -1: continue
        if label not in clusters: clusters[label] = []
        clusters[label].append(articles[i])
        
    # 3. Labeling
    final_output = {}
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
    
    for i, (label_id, cluster_items) in enumerate(sorted_clusters):
        cluster_indices = [idx for idx, l in enumerate(labels) if l == label_id]
        cluster_embeddings = embeddings[cluster_indices]
        center = np.mean(cluster_embeddings, axis=0)
        distances = cosine_distances([center], cluster_embeddings)[0]
        closest_idx = np.argmin(distances)
        centroid_title = cluster_items[closest_idx].get('title_ko') or cluster_items[closest_idx].get('title_en')
        
        print(f"  Cluster {label_id} ({len(cluster_items)} articles): {centroid_title}")
        
        llm_result = generate_topic_label(cluster_items, centroid_title)
        topic_name = llm_result.get('topic_name', centroid_title)
        stances = llm_result.get('stances')
        
        if topic_name in final_output:
            topic_name = f"{topic_name} ({label_id})"
            
        final_output[topic_name] = {
            "stances": stances,
            "keywords": llm_result.get('keywords', []),
            "category": llm_result.get('category', 'Unclassified')
        }
        time.sleep(1)

    # Save to JSON
    output_file = os.path.join(script_dir, f"clusters_{country}_hdbscan.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(final_output)} topics to {output_file}")
    
    # Save to DB (Initial Save - Enrichment will overwrite/update)
    # Actually, let's SKIP DB save here and let Enrichment do it to avoid double writes?
    # But if Enrichment fails, we have nothing.
    # Let's save here too, just in case.
    
    try:
        print(f"  Saving to DB for {country}...")
        supabase.table("mvp2_articles").update({"local_topic_id": None}).eq("country_code", country).execute()
        supabase.table("mvp2_topics").delete().eq("country_code", country).execute()
        
        db_rows = []
        article_source_map = {a['id']: a.get('source_name', 'Unknown') for a in articles}
        
        for topic_name, details in final_output.items():
            stances = details['stances']
            article_ids = stances['factual'] + stances['critical'] + stances['supportive']
            unique_sources = set(article_source_map.get(aid) for aid in article_ids if aid in article_source_map)
            
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
                supabase.table("mvp2_topics").insert(db_rows[i:i+batch_size]).execute()
        print("  ✅ DB Saved.")
    except Exception as e:
        print(f"  ❌ DB Save Failed: {e}")

def main():
    print("Starting Global Clustering (GitHub Actions Mode - Sequential)...")
    for country in COUNTRIES:
        try:
            process_country(country)
            gc.collect() # Cleanup memory
        except Exception as e:
            print(f"❌ Error processing {country}: {e}")
            
    print("\n🎉 All countries processed.")

if __name__ == "__main__":
    main()
