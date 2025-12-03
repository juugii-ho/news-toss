import os
# GRPC DNS Resolver Workaround
os.environ["GRPC_DNS_RESOLVER"] = "native"

import json
import glob
import time
import numpy as np
import google.generativeai as genai
from sklearn.cluster import HDBSCAN
from sklearn.metrics.pairwise import cosine_distances
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up two levels from data/pipelines to root, then into backend
env_path = os.path.join(script_dir, "..", "..", "backend", ".env")
load_dotenv(env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
    # Try loading from a local .env in the same directory as a fallback
    load_dotenv(os.path.join(script_dir, ".env"))
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

from sentence_transformers import SentenceTransformer

# Load Local Model (Multilingual)
# This will download the model on first run (approx 500MB)
print("⏳ Loading Local Embedding Model (paraphrase-multilingual-MiniLM-L12-v2)...")
embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_embeddings(texts, batch_size=100):
    """Generate embeddings locally using sentence-transformers"""
    print(f"Generating embeddings locally for {len(texts)} topics (Batch Size: {batch_size})...")
    
    # encode returns numpy array by default
    # normalize_embeddings=True ensures cosine similarity works well
    embeddings = embed_model.encode(
        texts, 
        batch_size=batch_size, 
        show_progress_bar=True, 
        normalize_embeddings=True
    )
    return embeddings

def main():
    print("🚀 Starting Megatopic Analysis...")
    
    # 1. Fetch Topics from DB (Stateless for GitHub Actions)
    print("Fetching recent topics from Supabase DB...")
    
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    supabase_client = create_client(url, key)
    
    # Use a 24h window to match publish_batch.py
    window_hours = int(os.getenv("PUBLISH_WINDOW_HOURS", "24"))
    time_threshold = (datetime.utcnow() - timedelta(hours=window_hours)).isoformat()
    
    print(f"  Time Threshold: {time_threshold} (last {window_hours}h)")
    
    try:
        # Fetch all topics created in the last 24h
        # We fetch ALL candidates, regardless of publish status, to ensure we cluster everything relevant.
        # (Deduplication happens naturally via clustering if names are similar, or we can filter duplicates later)
        response = supabase_client.table("mvp2_topics")\
            .select("id, topic_name, country_code, article_count, keywords, category, stances")\
            .gte("created_at", time_threshold)\
            .execute()
            
        db_topics = response.data
        print(f"  Found {len(db_topics)} topics in DB.")
        
        all_topics = []
        for t in db_topics:
            # Calculate size from stances if possible, else use article_count
            size = t.get('article_count', 0)
            stances = t.get('stances')
            if stances and isinstance(stances, dict):
                calc_size = len(stances.get('factual', [])) + \
                           len(stances.get('critical', [])) + \
                           len(stances.get('supportive', []))
                if calc_size > 0:
                    size = calc_size
            
            all_topics.append({
                "name": t['topic_name'],
                "country": t['country_code'],
                "size": size,
                "id": t['id'],
                "keywords": t.get('keywords', []),
                "category": t.get('category', 'Unclassified')
            })
            
    except Exception as e:
        print(f"❌ Error fetching topics from DB: {e}")
        return

    print(f"Total Local Topics Loaded: {len(all_topics)}")
    
    if not all_topics:
        print("No topics found in the last 24h. Skipping megatopic analysis.")
        return

    # 2. Embed Topic Names
    topic_names = [t['name'] for t in all_topics]
    embeddings = get_embeddings(topic_names)
    
    # 3. Cluster Topics (Megatopics)
    # Use AgglomerativeClustering with cosine metric
    print("Clustering into Megatopics (AgglomerativeClustering)...")
    from sklearn.cluster import AgglomerativeClustering
    
    # Threshold 0.20: Stricter to prevent "Sports + Misc" garbage clusters (User Request)
    # linkage='average': Produces more balanced clusters than 'complete'
    clusterer = AgglomerativeClustering(
        n_clusters=None, 
        distance_threshold=0.20, 
        metric='cosine', 
        linkage='average'
    )
    labels = clusterer.fit_predict(embeddings)
    
    n_clusters = len(set(labels))
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
    
    # Configure Gemini for Megatopic Labeling
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
        """
        Generate a global title, keywords, and category for a group of local topics.
        Also identifies any OUTLIER topics that don't belong.
        """
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
            print("    ⏳ Asking Gemini for Global Label & Outliers...", flush=True)
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
        # Sort by size to find the "Major" version of this story
        items.sort(key=lambda x: x['size'], reverse=True)
        
        # Default name (largest local topic)
        default_name = items[0]['name']
        
        # Pre-filter: Check if this cluster is worth asking LLM (Optimization)
        # Rule: Must have at least 2 countries OR > 5 articles if single country
        temp_countries = list(set([t['country'] for t in items]))
        temp_total_articles = sum([t['size'] for t in items])
        
        if len(temp_countries) < 2 and temp_total_articles < 5:
            print(f"    Skipping small local megatopic (Pre-filter): {default_name} ({len(temp_countries)} countries, {temp_total_articles} articles)")
            continue
        
        # Call LLM with Retry
        llm_result = None
        retries = 3
        for attempt in range(retries):
            try:
                llm_result = generate_megatopic_label(items, default_name)
                break
            except Exception as e:
                print(f"    ⚠️ Labeling failed (Attempt {attempt+1}/{retries}): {e}")
                if "429" in str(e) or "Resource exhausted" in str(e):
                    time.sleep(5 * (attempt + 1))
                else:
                    break
        
        if not llm_result:
             # Fallback to default name (Largest Local Topic)
            llm_result = {
                "megatopic_name": default_name,
                "keywords": [],
                "category": "Unclassified"
            }
        
        megatopic_name = llm_result.get('megatopic_name', default_name)
        keywords = llm_result.get('keywords', [])
        category = llm_result.get('category', 'Unclassified')
        outliers = llm_result.get('outliers', [])
        
        # Filter out outliers
        if outliers:
            print(f"    🗑️ Removing {len(outliers)} outlier topics.")
            filtered_items = [item for i, item in enumerate(items) if i not in outliers]
        else:
            filtered_items = items
            
        # If all items are outliers (LLM hallucination?), keep original items
        if not filtered_items:
            print(f"    ⚠️ Warning: LLM marked all items as outliers. Keeping original items.")
            filtered_items = items
        
        countries = list(set([t['country'] for t in filtered_items]))
        total_articles = sum([t['size'] for t in filtered_items])
        
        # Filter by Minimum Countries
        # Rule: Must have at least 2 countries to be considered a true "global" megatopic
        if len(countries) < 2:
            print(f"    Skipping small local megatopic (Pre-filter): {megatopic_name} ({len(countries)} countries, {total_articles} articles)")
            continue
        
        print(f"  [{i+1}/{len(megatopics)}] {megatopic_name} ({len(countries)} countries, {total_articles} articles)")
        
        final_output.append({
            "megatopic_name": megatopic_name,
            "countries": countries,
            "total_articles": total_articles,
            "topic_ids": [t['id'] for t in filtered_items if t.get('id')], # These are UUIDs from DB
            "keywords": keywords,
            "category": category,
            "created_at": datetime.utcnow().isoformat()
        })
        time.sleep(1) # Rate limit safety

    # Sort Megatopics by global reach (number of countries) then total articles
    final_output.sort(key=lambda x: (len(x['countries']), x['total_articles']), reverse=True)
    
    output_file = os.path.join(script_dir, "megatopics.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Megatopic Analysis Complete. Saved to {output_file}")
    
    # 5. Save to DB
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("⚠️ Supabase credentials not found. Skipping DB save.")
        return

    supabase: Client = create_client(url, key)
    
    print(f"Saving {len(final_output)} megatopics to Supabase...")
    
    try:
        # 1. Clear ONLY unpublished DRAFTS (Preserve published ones and archived history)
        print("  🧹 Clearing unpublished drafts (preserving history)...")
        # Only delete drafts (batch_id is NULL), keep history (batch_id set) intact
        supabase.table("mvp2_megatopics").delete()\
            .eq("is_published", False)\
            .is_("batch_id", "null")\
            .execute()
        
        # Prepare rows
        rows = []
        for i, item in enumerate(final_output):
            rows.append({
                "name": item['megatopic_name'],
                "title_ko": item['megatopic_name'], # Map name to title_ko for API
                "summary": f"Global coverage across {len(item['countries'])} countries.", 
                "countries": item['countries'],
                "total_articles": item['total_articles'],
                "article_count": item['total_articles'], # Map to article_count for API
                "country_count": len(item['countries']), # Map to country_count for API
                "rank": i + 1, # Rank based on sort order
                "is_pinned": False,
                "topic_ids": item['topic_ids'],
                "keywords": item['keywords'],
                "category": item['category'],
                "content": item['megatopic_name'] + "\n" + f"Global coverage across {len(item['countries'])} countries.", 
                "created_at": item['created_at']
            })
            
        # Batch insert
        batch_size = 50
        inserted_megatopics = []
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            result = supabase.table("mvp2_megatopics").insert(batch).execute()
            inserted_megatopics.extend(result.data)
            print(f"  Inserted batch {i//batch_size + 1}")
        
        # 2. Link articles to megatopics
        print("\n  🔗 Linking articles to megatopics...")
        total_linked = 0
        for mega in inserted_megatopics:
            mega_id = mega['id']
            local_topic_ids = mega.get('topic_ids', [])
            
            if not local_topic_ids:
                continue
            
            # Update all articles that belong to these local topics
            for local_id in local_topic_ids:
                try:
                    result = supabase.from_("mvp2_articles")\
                        .update({"global_topic_id": mega_id})\
                        .eq("local_topic_id", local_id)\
                        .execute()
                    
                    if result.data:
                        total_linked += len(result.data)
                except Exception as e:
                    print(f"    ⚠️ Error linking articles for local topic {local_id}: {e}")
        
        print(f"  ✓ Linked {total_linked} articles to megatopics")
            
        print("✅ Saved to DB successfully.")
        
    except Exception as e:
        print(f"❌ Error saving to DB: {e}")
    
    # Preview
    print("\n--- Top 10 Megatopics ---")
    for m in final_output[:10]:
        print(f"🌍 [{len(m['countries'])} Countries] {m['megatopic_name']} ({m['total_articles']} articles)")

if __name__ == "__main__":
    main()
