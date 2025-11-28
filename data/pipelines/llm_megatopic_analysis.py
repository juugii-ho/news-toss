import os
import json
import glob
import numpy as np
import google.generativeai as genai
from sklearn.cluster import HDBSCAN
from sklearn.metrics.pairwise import cosine_distances
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def get_embeddings(texts, batch_size=100):
    """Generate embeddings for a list of texts"""
    embeddings = []
    total = len(texts)
    print(f"Generating embeddings for {total} topics...")
    
    for i in range(0, total, batch_size):
        batch = texts[i:i+batch_size]
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=batch,
                task_type="clustering",
            )
            embeddings.extend(result['embedding'])
        except Exception as e:
            print(f"  ❌ Embedding failed for batch {i}: {e}")
            embeddings.extend([[0.0]*768] * len(batch))
            
    return np.array(embeddings)

def main():
    print("🚀 Starting Megatopic Analysis...")
    
    # 1. Load all enriched topic files
    cluster_files = glob.glob("data/pipelines/enriched_topics_*.json")
    all_topics = []
    
    print(f"Loading enriched topics from {len(cluster_files)} files...")
    for fpath in cluster_files:
        # data/pipelines/enriched_topics_RU.json -> ['data/pipelines/enriched', 'topics', 'RU.json']
        # easier: split by '_' then remove .json
        try:
            filename = os.path.basename(fpath) # enriched_topics_RU.json
            country = filename.replace("enriched_topics_", "").replace(".json", "")
        except Exception:
            print(f"Skipping malformed filename: {fpath}")
            continue
            
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            for topic_name, details in data.items():
                # In enriched format, topic_name is the key, but we also have "topic_name_ko" inside
                # We prefer "topic_name_ko" if available, as it's the polished title
                display_name = details.get("topic_name_ko", topic_name)
                
                # Calculate total articles
                size = len(details.get('stances', {}).get('factual', [])) + \
                       len(details.get('stances', {}).get('critical', [])) + \
                       len(details.get('stances', {}).get('supportive', []))
                       
                all_topics.append({
                    "name": display_name,
                    "country": country,
                    "size": size,
                    "original_data": details
                })
                
    print(f"Total Local Topics Found: {len(all_topics)}")
    
    if not all_topics:
        print("No topics found. Run clustering first.")
        return

    # 2. Embed Topic Names
    topic_names = [t['name'] for t in all_topics]
    embeddings = get_embeddings(topic_names)
    
    # 3. Cluster Topics (Megatopics)
    # Use HDBSCAN with small min_cluster_size to find shared themes
    print("Clustering into Megatopics (HDBSCAN)...")
    clusterer = HDBSCAN(min_cluster_size=2, min_samples=1, metric='euclidean')
    labels = clusterer.fit_predict(embeddings)
    
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"Found {n_clusters} Megatopics.")
    
    # Group by Megatopic
    megatopics = {}
    for i, label in enumerate(labels):
        if label == -1: continue # Ignore unique/noise topics
        
        if label not in megatopics:
            megatopics[label] = []
        megatopics[label].append(all_topics[i])
        
    # 4. Name and Format Megatopics
    final_output = []
    
    for label_id, items in megatopics.items():
        # Sort by size to find the "Major" version of this story
        items.sort(key=lambda x: x['size'], reverse=True)
        
        # Use the name of the largest/most common topic as the Megatopic Name
        # Or find centroid if needed, but largest is usually a good proxy for "Mainstream Title"
        megatopic_name = items[0]['name']
        
        countries = list(set([t['country'] for t in items]))
        total_articles = sum([t['size'] for t in items])
        
        final_output.append({
            "megatopic_name": megatopic_name,
            "countries": countries,
            "total_articles": total_articles,
            "local_topics": items
        })
        
    # Sort Megatopics by global reach (number of countries) then total articles
    final_output.sort(key=lambda x: (len(x['countries']), x['total_articles']), reverse=True)
    
    # Save
    with open("data/pipelines/megatopics.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Megatopic Analysis Complete. Saved to data/pipelines/megatopics.json")
    
    # Preview
    print("\n--- Top 10 Megatopics ---")
    for m in final_output[:10]:
        print(f"🌍 [{len(m['countries'])} Countries] {m['megatopic_name']} ({m['total_articles']} articles)")
        print(f"    Countries: {', '.join(m['countries'])}")

if __name__ == "__main__":
    main()
