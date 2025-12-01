import os
import json
import time
import sys
import numpy as np
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances

# Fix gRPC DNS resolution issue (caused by sentence-transformers conflict)
os.environ['GRPC_DNS_RESOLVER'] = 'native'

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

def fetch_articles(country_code):
    print(f"Fetching articles for {country_code} (Last 24 hours)...")
    
    # Calculate 24 hours ago
    from datetime import datetime, timedelta
    time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()

    # Fetch both EN and KO titles. Use EN for embedding (better quality), KO for fallback naming if needed.
    response = supabase.table("mvp2_articles") \
        .select("id, title_en, title_ko, published_at, source_name") \
        .eq("country_code", country_code) \
        .not_.is_("title_en", "null") \
        .gte("published_at", time_threshold) \
        .execute()
    return response.data

from sentence_transformers import SentenceTransformer

# Load Local Model (Multilingual)
print("⏳ Loading Local Embedding Model (paraphrase-multilingual-MiniLM-L12-v2)...")
embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_embeddings(texts, batch_size=32):
    """Generate embeddings locally using sentence-transformers"""
    print(f"Generating embeddings locally for {len(texts)} articles (Batch Size: {batch_size})...")
    
    # encode returns numpy array by default
    # normalize_embeddings=True ensures cosine similarity works well
    embeddings = embed_model.encode(
        texts, 
        batch_size=batch_size, 
        show_progress_bar=True, 
        normalize_embeddings=True
    )
    return embeddings

def generate_topic_label(cluster_articles, centroid_title):
    """
    Generates a topic label, keywords, category, and stance classification using Gemini.
    Uses index-based mapping to avoid UUID hallucinations.
    """
    # Create index mapping
    article_map = {i+1: a for i, a in enumerate(cluster_articles)}
    
    # Format input with indices
    input_text = "\n".join([f"{i+1}. {a['title_en']}" for i, a in enumerate(cluster_articles)])
    
    prompt = f"""
    Role: Professional News Editor & Data Analyst
    Task: Analyze the following news articles (clustered by similarity) and provide a structured summary.

    Articles:
    {input_text}

    # Requirements
    1. **Topic Name**: Create a concise, neutral, descriptive topic name in KOREAN. (e.g., "비트코인 10만 달러 돌파")
    2. **Keywords**: Extract 3-5 keywords (KOREAN).
    3. **Category**: Politics, Economy, Society, World, Tech, Culture, Sports, Entertainment.
    4. **Outliers**: Identify indices of articles irrelevant to the dominant topic.
    5. **Stances**: Classify indices into Factual, Critical, Supportive using the **Logic & Process** below.

    # 🧠 Chain of Thought (MANDATORY PROCESS)
    **You must follow these 4 steps internally before deciding the stance:**

    **Step 1: Entity & Event Separation (Fact Check)**
    - Identify WHO (Subject) experienced WHAT (Event).
    - Determine if the event itself is positive (e.g., profit up) or negative (e.g., accident, stock drop).
    - *Goal:* Separate the "Event" from the "Tone".

    **Step 2: Linguistic Cues & Sentence Endings**
    - **Modifiers**: Are there emotional adjectives/adverbs?
        - Positive: "탁월한(Excellent)", "놀라운(Amazing)"
        - Negative: "충격적(Shocking)", "최악의(Worst)"
    - **Sentence Ending (Crucial)**:
        - **Dry/Descriptive**: Ends with "~했다", "~나타났다", "~전망이다", "~기록했다". -> Likely **Factual**.
        - **Evaluative/Judgmental**: Ends with "~위기", "~논란", "~비상", "~불가피". -> Likely **Critical**.

    **Step 3: Context & Framing (The "Bad Fact" Trap)**
    - **Distinguish "Bad Fact" vs. "Critical Stance"**:
        - Case A: "Exchange rate hits 1400 won" (Negative Fact) + "Recorded/Announced" (Dry Tone) → **🔵 Factual**
        - Case B: "Exchange rate hits 1400 won" (Negative Fact) + "Economy in Emergency" (Alarmist Tone) → **🔴 Critical**
    - **"Despite" Structure ("A에도 불구하고 B")**:
        - Focus on **B**. If B is positive (e.g., "Despite recession, profit up"), it is **🟢 Supportive**.

    **Step 4: Final Classification Criteria**
    - **🔴 Critical**: Focuses on failure, conflict, or anxiety. Keywords: "논란", "비판", "우려", "위기", "급락", "망신".
    - **🟢 Supportive**: Focuses on success, defense, or hope. Keywords: "성공", "기대", "호평", "돌파", "순항".
    - **🔵 Factual**: Dry delivery of info/stats without emotional coloring. Keywords: "발표", "개최", "출시", "수치 나열".

    # Output Format (JSON Only)
    {{
    "topic_name": "Headline",
    "keywords": ["Key1", "Key2"],
    "category": "Category",
    "stances": {{
        "factual": [index, ...],
        "critical": [index, ...],
        "supportive": [index, ...]
    }},
    "outliers": [index, ...]
    }}
    """
    retries = 3
    for attempt in range(retries):
        try:
            print("    ⏳ Asking Gemini...", flush=True)
            response = model.generate_content(prompt)
            text = response.text
            # DEBUG: Print raw response
            print(f"    🔍 Raw LLM Response: {text}", flush=True)
            
            # Clean markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            result = json.loads(text)
            
            # Helper to safely map indices to article IDs
            def map_indices_to_ids(indices, article_map):
                mapped_ids = []
                for idx in indices:
                    try:
                        # Handle if LLM returns string "1" instead of int 1
                        idx_int = int(idx)
                        if idx_int in article_map:
                            mapped_ids.append(article_map[idx_int]['id'])
                    except:
                        continue
                # DEBUG
                print(f"    DEBUG: Mapped indices {indices} -> {mapped_ids}")
                return mapped_ids

            raw_stances = result.get("stances", {})
            mapped_stances = {
                "factual": map_indices_to_ids(raw_stances.get("factual", []), article_map),
                "critical": map_indices_to_ids(raw_stances.get("critical", []), article_map),
                "supportive": map_indices_to_ids(raw_stances.get("supportive", []), article_map)
            }
            
            # Map outliers
            raw_outliers = result.get('outliers', [])
            mapped_outliers = map_indices_to_ids(raw_outliers, article_map)
            
            # Ensure all articles are accounted for (fallback to factual if missing)
            # Exclude outliers from this check
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
            print(f"    ⚠️ Labeling failed (Attempt {attempt+1}/{retries}): {e}")
            error_str = str(e)
            
            # Retriable errors: Rate limit, DNS, Timeout
            if "429" in error_str or "Resource exhausted" in error_str or "DNS" in error_str or "Timeout" in error_str:
                if attempt < retries - 1:  # Don't sleep on last attempt
                    sleep_time = 5 * (attempt + 1)
                    print(f"    💤 Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
            else:
                # Non-retriable error (safety filter, JSON parse error, etc)
                print(f"    ⛔ Non-retriable error. Skipping to fallback.")
                break
    
    # FALLBACK: Use the title of the article closest to the centroid (most representative)
    print("    ❌ Final failure. Using fallback name.")
    return {
        "topic_name": f"{centroid_title} (자동 생성)",
        "keywords": [],
        "category": "Unclassified",
        "stances": {"factual": [a['id'] for a in cluster_articles], "critical": [], "supportive": []} # Default to factual
    }

def find_similar_topic(new_topic_name, country_code, supabase, threshold=0.8):
    """
    Find similar existing topic within last 7 days.
    
    Args:
        new_topic_name: New topic name to match
        country_code: Country code
        supabase: Supabase client
        threshold: Similarity threshold (0.0 to 1.0)
    
    Returns:
        Existing topic dict or None
    """
    seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    
    try:
        response = supabase.table("mvp2_topics") \
            .select("id, topic_name, article_ids, stances") \
            .eq("country_code", country_code) \
            .gte("created_at", seven_days_ago) \
            .execute()
        
        existing_topics = response.data
        
        best_match = None
        best_score = 0.0
        
        for topic in existing_topics:
            similarity = SequenceMatcher(None, new_topic_name, topic['topic_name']).ratio()
            
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = topic
        
        if best_match:
            print(f"    🔍 Found similar topic: '{best_match['topic_name']}' (similarity: {best_score:.2f})")
        
        return best_match
        
    except Exception as e:
        print(f"    ⚠️ Error finding similar topic: {e}")
        return None


def main():
    COUNTRY = sys.argv[1] if len(sys.argv) > 1 else 'RU'
    
    articles = fetch_articles(COUNTRY)
    if not articles:
        print("No articles found.")
        return
        
    titles = [a['title_en'] for a in articles]
    ids = [a['id'] for a in articles]
    
    # Output file path (Absolute)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, f"clusters_{COUNTRY}_hdbscan.json")
    
    # 1. Generate Embeddings
    embeddings = get_embeddings(titles)
    
    # 2. HDBSCAN Clustering
    # HDBSCAN finds clusters of varying densities and identifies noise (-1)
    print(f"Clustering with HDBSCAN (min_cluster_size=3)...")
    
    from sklearn.cluster import HDBSCAN
    
    # Dynamic parameters based on data volume
    n_articles = len(embeddings)
    if n_articles > 500:
        # High volume (KR, US): Strict separation, higher noise tolerance
        min_cluster_size = 5
        min_samples = 5
        epsilon = 0.0
    elif n_articles > 100:
        # Medium volume (GB): Balanced
        min_cluster_size = 3
        min_samples = 3
        epsilon = 0.0
    else:
        # Small dataset (< 100 articles)
        # JP, BE, NL etc.
        min_cluster_size = 3
        min_samples = 2
        epsilon = 0.1 # Stricter separation to prevent "garbage clusters"

    # OVERRIDE for now: The user complained about RU (85 articles) merging everything.
    # min_samples=2 was too loose. Let's try min_samples=3 for everyone.
    
    if n_articles < 50:
        # Very small datasets: Be careful not to drop everything
        min_cluster_size = 2
        min_samples = 2
        epsilon = 0.0
    else:
        # Standard
        min_cluster_size = 3
        min_samples = 3 # Increased from 2 to break chains
        epsilon = 0.0

    print(f"  Params: min_cluster_size={min_cluster_size}, min_samples={min_samples}, epsilon={epsilon}")
    clusterer = HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples, cluster_selection_epsilon=epsilon, metric='euclidean')
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
            
            # LLM Generation - RE-ENABLED (DNS issue fixed)
            try:
                llm_result = generate_topic_label(cluster_items, centroid_title)
                topic_name = llm_result.get('topic_name', centroid_title)
                stances = llm_result.get('stances', {
                    "factual": [a['id'] for a in cluster_items],
                    "critical": [],
                    "supportive": []
                })
                # Merge metadata into stances for convenience (or keep separate)
                stances['keywords'] = llm_result.get('keywords', [])
                stances['keywords'] = llm_result.get('keywords', [])
                stances['category'] = llm_result.get('category', 'Unclassified')
                
                # Log outliers
                outliers = llm_result.get('outliers', [])
                if outliers:
                    print(f"    🗑️ Removed {len(outliers)} outlier articles.")
                
            except Exception as e:
                print(f"    ⚠️ LLM Error in loop: {e}")
                topic_name = centroid_title
                stances = {
                    "factual": [a['id'] for a in cluster_items],
                    "critical": [],
                    "supportive": [],
                    "keywords": [],
                    "category": "Unclassified"
                }
            
            # Ensure unique keys
            if topic_name in final_output:
                topic_name = f"{topic_name} ({label_id})"
                
            # Print generated metadata for verification
            print(f"    🏷️ Topic: {topic_name}")
            print(f"    🔑 Keywords: {stances.get('keywords', [])}")
            print(f"    📂 Category: {stances.get('category', 'Unclassified')}")
            
            final_output[topic_name] = stances
            
            # Incremental Save
            if (i + 1) % 5 == 0 or (i + 1) == n_clusters:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(final_output, f, ensure_ascii=False, indent=2)
                
            time.sleep(2) # Rate limit protection (2s delay)
            
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
                # Create a lookup for article sources
                article_source_map = {a['id']: a.get('source_name', 'Unknown') for a in articles}
                
                updated_count = 0
                inserted_count = 0
                
                for topic_name, stances in final_output.items():
                    article_ids = stances['factual'] + stances['critical'] + stances['supportive']
                    
                    # Calculate unique source count
                    unique_sources = set()
                    for aid in article_ids:
                        if aid in article_source_map:
                            unique_sources.add(article_source_map[aid])
                    
                    # Check if similar topic exists
                    existing = find_similar_topic(topic_name, COUNTRY, supabase)
                    
                    if existing:
                        # Merge with existing topic instead of overwriting older articles
                        print(f"  🔄 Updating: {topic_name}")
                        existing_ids = existing.get("article_ids", []) or []
                        existing_stances = existing.get("stances", {}) or {}
                        
                        def merged_list(old, new):
                            seen = set()
                            merged = []
                            for v in old + new:
                                if v not in seen:
                                    merged.append(v)
                                    seen.add(v)
                            return merged
                        
                        merged_stances = {}
                        for sentiment in ["factual", "critical", "supportive"]:
                            merged_stances[sentiment] = merged_list(
                                existing_stances.get(sentiment, []),
                                stances.get(sentiment, [])
                            )
                        merged_stances["keywords"] = stances.get("keywords", existing_stances.get("keywords", []))
                        merged_stances["category"] = stances.get("category", existing_stances.get("category", "Unclassified"))

                        merged_article_ids = merged_list(existing_ids, article_ids)
                        
                        unique_sources = set()
                        for aid in merged_article_ids:
                            if aid in article_source_map:
                                unique_sources.add(article_source_map[aid])
                        
                        supabase.table("mvp2_topics").update({
                            "article_ids": merged_article_ids,
                            "article_count": len(merged_article_ids),
                            "source_count": len(unique_sources),
                            "stances": merged_stances,
                            "keywords": merged_stances.get('keywords', []),
                            "category": merged_stances.get('category', 'Unclassified'),
                            "last_updated_at": datetime.utcnow().isoformat()
                        }).eq("id", existing['id']).execute()
                        updated_count += 1
                    else:
                        # Insert new topic
                        print(f"  ✨ Creating: {topic_name}")
                        supabase.table("mvp2_topics").insert({
                            "country_code": COUNTRY,
                            "topic_name": topic_name,
                            "article_ids": article_ids,
                            "article_count": len(article_ids),
                            "source_count": len(unique_sources),
                            "stances": stances,
                            "keywords": stances.get('keywords', []),
                            "category": stances.get('category', 'Unclassified'),
                            "first_seen_at": datetime.utcnow().isoformat(),
                            "last_updated_at": datetime.utcnow().isoformat()
                        }).execute()
                        inserted_count += 1
                
                print(f"  📊 Updated: {updated_count}, Inserted: {inserted_count}")
                        
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
