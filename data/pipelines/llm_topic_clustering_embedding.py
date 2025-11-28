import os
import json
import time
import sys
import numpy as np
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
if not load_dotenv():
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend', '.env'))

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not GOOGLE_API_KEY:
    print("Error: Environment variables missing.")
    exit(1)

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GOOGLE_API_KEY)

# Model configuration for Labeling
generation_config = {
    "temperature": 0.3,
    "top_p": 0.8,
    "max_output_tokens": 1024,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    safety_settings={
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
    }
)

def fetch_articles(country_code):
    print(f"Fetching articles for {country_code} (Last 24 hours)...")
    
    # Calculate 24 hours ago
    from datetime import datetime, timedelta
    time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()

    # Fetch both EN and KO titles. Use EN for embedding (better quality), KO for fallback naming if needed.
    response = supabase.table("mvp2_articles") \
        .select("id, title_en, title_ko, published_at") \
        .eq("country_code", country_code) \
        .not_.is_("title_en", "null") \
        .gte("published_at", time_threshold) \
        .execute()
    return response.data

def get_embeddings(texts, batch_size=100):
    """Generate embeddings for a list of texts using Gemini API"""
    embeddings = []
    total = len(texts)
    print(f"Generating embeddings for {total} articles...")
    
    for i in range(0, total, batch_size):
        batch = texts[i:i+batch_size]
        try:
            # text-embedding-004 is the recommended model
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=batch,
                task_type="clustering",
            )
            embeddings.extend(result['embedding'])
            print(f"  Embedded {min(i+batch_size, total)}/{total}")
            time.sleep(0.5) # Rate limit protection
        except Exception as e:
            print(f"  ❌ Embedding failed for batch {i}: {e}")
            # Fill with zeros to avoid crashing, or retry? 
            # For MVP, let's fill zeros but log error.
            embeddings.extend([[0.0]*768] * len(batch))
            
    return np.array(embeddings)

def generate_topic_label(cluster_articles, centroid_title):
    """
    Use LLM to generate topic name and stance for the cluster.
    Fallback to centroid_title if LLM fails.
    """
    input_text = "\n".join([f"[{a['id']}] {a['title_en']}" for a in cluster_articles])
    
    prompt = f"""
Role: Expert Media Analyst
Task: Analyze these {len(cluster_articles)} news headlines about the SAME event.

Input:
{input_text}

Requirements:
1. **Topic Name**: Create a specific, descriptive topic name in KOREAN.
2. **Stance**: Analyze the stance of each article (factual/critical/supportive).

Output JSON:
{{
  "topic_name": "Topic Name in Korean",
  "stances": {{
    "factual": [id, id],
    "critical": [id],
    "supportive": []
  }}
}}
"""
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"    ⚠️ Labeling failed (Safety/Error): {e}")
        # FALLBACK: Use the title of the article closest to the centroid (most representative)
        return {
            "topic_name": f"{centroid_title} (자동 생성)",
            "stances": {"factual": [a['id'] for a in cluster_articles], "critical": [], "supportive": []} # Default to factual
        }

def main():
    COUNTRY = sys.argv[1] if len(sys.argv) > 1 else 'RU'
    
    articles = fetch_articles(COUNTRY)
    if not articles:
        print("No articles found.")
        return
        
    titles = [a['title_en'] for a in articles]
    ids = [a['id'] for a in articles]
    
    # Output file path
    output_file = f"data/pipelines/clusters_{COUNTRY}_embedding.json"
    
    # 1. Generate Embeddings
    embeddings = get_embeddings(titles)
    
    # 2. HDBSCAN Clustering
    # HDBSCAN finds clusters of varying densities and identifies noise (-1)
    print(f"Clustering with HDBSCAN (min_cluster_size=3)...")
    
    from sklearn.cluster import HDBSCAN
    
    # min_cluster_size=3: Allow small micro-events
    # min_samples=2: Less conservative, allows more points to be core
    # metric='euclidean': Standard for embeddings (if normalized, equivalent to cosine ranking)
    clusterer = HDBSCAN(min_cluster_size=3, min_samples=2, metric='euclidean')
    labels = clusterer.fit_predict(embeddings)
    
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    print(f"  Found {n_clusters} clusters and {n_noise} noise points.")
    
    # Group articles by cluster
    clusters = {}
    noise_articles = []
    
    for i, label in enumerate(labels):
        if label == -1:
            noise_articles.append(articles[i])
            continue
            
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(articles[i])
        
    # 3. Labeling & Formatting
    final_output = {}
    print("Generating Topic Labels...")
    
    # Output file path (Updated for HDBSCAN)
    output_file = f"data/pipelines/clusters_{COUNTRY}_hdbscan.json"
    
    try:
        # Sort clusters by size (Importance)
        sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
        
        for i, (label_id, cluster_items) in enumerate(sorted_clusters):
            # Find centroid article (closest to cluster center)
            # HDBSCAN doesn't give centroids directly, so we calculate the mean of points
            cluster_indices = [idx for idx, l in enumerate(labels) if l == label_id]
            cluster_embeddings = embeddings[cluster_indices]
            center = np.mean(cluster_embeddings, axis=0)
            
            distances = cosine_distances([center], cluster_embeddings)[0]
            closest_idx = np.argmin(distances)
            # Use Korean title, fallback to English
            centroid_title = cluster_items[closest_idx].get('title_ko') or cluster_items[closest_idx].get('title_en') or f"Topic {label_id}"
            
            print(f"  Processing Cluster {i+1}/{n_clusters} (ID: {label_id}, {len(cluster_items)} articles)...")
            
            # PURE CLUSTERING MODE: No LLM Generation
            topic_name = centroid_title
            
            stances = {
                "factual": [a['id'] for a in cluster_items],
                "critical": [],
                "supportive": []
            }
            
            # Ensure unique keys
            if topic_name in final_output:
                topic_name = f"{topic_name} ({label_id})"
                
            final_output[topic_name] = stances
            
            # Incremental Save
            if (i + 1) % 5 == 0 or (i + 1) == n_clusters:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(final_output, f, ensure_ascii=False, indent=2)
                
            time.sleep(0.1)
            
        # Add Noise info at the end (Optional, or just log it)
        if noise_articles:
            print(f"  Note: {len(noise_articles)} articles were classified as Noise and excluded.")
            
    finally:
        if final_output:
            # Save to JSON (Backup)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(final_output, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Clustering Complete. Saved {len(final_output)} topics to {output_file}")
            
            # Save to DB
            print("Saving topics to Supabase DB (mvp2_topics)...")
            try:
                # 1. Clear existing topics for this country (Optional: or we can use upsert/versioning)
                # For MVP, let's clear old ones to keep it clean, OR we can just append.
                # Clearing is safer to avoid duplicates if we run often.
                # But wait, if we clear, we lose history. 
                # Let's just INSERT. We can filter by created_at in frontend.
                
                db_rows = []
                for topic_name, stances in final_output.items():
                    article_ids = stances['factual'] + stances['critical'] + stances['supportive']
                    db_rows.append({
                        "country_code": COUNTRY,
                        "topic_name": topic_name,
                        "article_ids": article_ids,
                        "article_count": len(article_ids),
                        "stances": stances,
                        "created_at": datetime.utcnow().isoformat()
                    })
                
                if db_rows:
                    # Batch insert
                    batch_size = 50
                    for i in range(0, len(db_rows), batch_size):
                        batch = db_rows[i:i+batch_size]
                        supabase.table("mvp2_topics").insert(batch).execute()
                        print(f"  Inserted batch {i//batch_size + 1}")
                        
                print("✅ Saved to DB successfully.")
                
            except Exception as e:
                print(f"❌ Error saving to DB: {e}")

    print(f"Total Topics: {len(final_output)}")
    
    # Preview
    print("\n--- Cluster Preview (First 5) ---")
    for k, v in list(final_output.items())[:5]:
        print(f"{k}: {len(v.get('factual', [])) + len(v.get('critical', [])) + len(v.get('supportive', []))} articles")

if __name__ == "__main__":
    main()
