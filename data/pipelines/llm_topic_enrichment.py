import os
import json
import time
import sys
from collections import Counter
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

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
    "temperature": 0.7, # Slightly higher for creative titles
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

def fetch_article_details(article_ids):
    """Fetch details for a list of article IDs"""
    # Chunking to avoid URL length limits
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
    
    if dominance > 0.5 and total > 2: # Only apply if significant
        # print(f"    ✂️ Source Dedup: {top_source} has {dominance:.1%} ({top_count}/{total})")
        
        # Separate the dominant source articles
        dominant_articles = [a for a in cluster_articles if a.get('source_name') == top_source]
        other_articles = [a for a in cluster_articles if a.get('source_name') != top_source]
        
        # Sort dominant articles by published_at (descending) and keep top 2
        dominant_articles.sort(key=lambda x: x.get('published_at') or '', reverse=True)
        kept_dominant = dominant_articles[:2]
        
        # Combine back
        return other_articles + kept_dominant
        
    return cluster_articles

def generate_metadata_batch(batch_topics):
    """
    Generate metadata for a batch of topics using LLM.
    batch_topics: List of (topic_key, articles) tuples
    """
    input_text = ""
    for i, (topic_key, articles) in enumerate(batch_topics):
        input_text += f"\n--- TOPIC {i+1}: {topic_key} ---\n"
        for a in articles[:10]: # Limit context
            title = a.get('title_ko') or a.get('title_en') or "No Title"
            input_text += f"- {title}\n"

    prompt = f"""
Role: You are 'News Toss', a witty, friendly, and knowledgeable news curator.
Tone: Casual, engaging, sexy, yet informative. Use Korean. (e.g., "~했어요", "~인가요?", "결국...", "충격!")

Task: Analyze {len(batch_topics)} separate news topics and generate metadata for EACH.

Input:
{input_text}

Requirements for EACH topic:
1. **topic_name_ko**: A catchy, clickable title in Korean.
2. **summary_ko**: A 3-line summary.
3. **keywords**: 3-5 hashtags.
4. **category**: One of [Politics, Economy, Society, Tech, World, Culture, Sports, Entertainment].
5. **stances**: Classify article IDs (if possible, otherwise just return empty lists).

Output JSON List:
[
  {{
    "original_topic_key": "TOPIC 1 key...",
    "topic_name_ko": "...",
    "summary_ko": "...",
    "keywords": [...],
    "category": "...",
    "stances": {{ "factual": [], "critical": [], "supportive": [] }}
  }},
  ...
]
"""
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"    ⚠️ Batch Generation failed: {e}")
        return None

def main():
    # Default to KR if no argument
    COUNTRY = sys.argv[1] if len(sys.argv) > 1 else 'KR'
    
    input_file = f"data/pipelines/clusters_{COUNTRY}_hdbscan.json"
    output_file = f"data/pipelines/enriched_topics_{COUNTRY}.json"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
        
    print(f"🚀 Starting Source Deduplication for {COUNTRY}...")
    
    with open(input_file, "r", encoding="utf-8") as f:
        clusters = json.load(f)
        
    enriched_data = {}
    
    # Collect all IDs to fetch details
    all_ids = []
    for data in clusters.values():
        all_ids.extend(data.get("factual", []) + data.get("critical", []) + data.get("supportive", []))
        
    print(f"  Fetching details for {len(all_ids)} articles...")
    article_map = fetch_article_details(all_ids)
    
    total_clusters = len(clusters)
    print(f"  Processing {total_clusters} clusters...")
    
    for i, (topic_key, data) in enumerate(clusters.items()):
        cluster_ids = data.get("factual", []) + data.get("critical", []) + data.get("supportive", [])
        cluster_articles = [article_map.get(aid) for aid in cluster_ids if article_map.get(aid)]
        
        # 1. Source Deduplication (The ONLY task)
        filtered_articles = deduplicate_sources(cluster_articles)
        
        if not filtered_articles:
            continue
            
        # 2. Save without LLM Generation
        # Use existing topic key (centroid title) and filtered article list
        enriched_data[topic_key] = {
            "topic_name_ko": topic_key, # Keep original title
            "summary_ko": "", # Empty
            "keywords": [],
            "category": "Unclassified",
            "stances": {
                "factual": [a['id'] for a in filtered_articles],
                "critical": [],
                "supportive": []
            }
        }
        
    # Final Save
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Deduplication Complete. Saved {len(enriched_data)} topics to {output_file}")

if __name__ == "__main__":
    main()
