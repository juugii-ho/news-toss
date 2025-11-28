import os
import json
import time
import sys
import math
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

# Model configuration
generation_config = {
    "temperature": 0.3, # Lower temperature for stricter adherence to rules
    "top_p": 0.8,
    "max_output_tokens": 8192,
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
    print(f"Fetching articles for {country_code} (Korean Titles)...")
    response = supabase.table("mvp2_articles") \
        .select("id, title_ko") \
        .eq("country_code", country_code) \
        .not_.is_("title_ko", "null") \
        .execute()
    return response.data

def get_balanced_batches(articles, target_size=200):
    """
    Recursively split articles into balanced batches close to target_size.
    Example: 900 -> 450, 450 -> 225, 225, 225, 225
    """
    n = len(articles)
    if n <= target_size * 1.5: # Allow up to 300 if target is 200, to avoid splitting into 150
        return [articles]
    
    mid = n // 2
    left = articles[:mid]
    right = articles[mid:]
    
    return get_balanced_batches(left, target_size) + get_balanced_batches(right, target_size)

def call_llm_clustering(articles, country_code):
    # Calculate dynamic target topics (approx 1 per 7 articles)
    target_topics = max(3, len(articles) // 7)
    
    input_text = "\n".join([f"[{article['id']}] {article['title_ko']}" for article in articles])
    
    prompt = f"""
Role:
You are an expert media analyst evaluating news headlines based on strict **Journalistic Objectivity** and **Linguistic Evidence**.
Your goal is to extract key topics and analyze the 'Stance' of each headline.

Input Data:
{len(articles)} news headlines from {country_code} (Korean Translated):
{input_text}

Task Instructions:

1. **Topic Extraction (Scope: Micro-Events Only)**:
    - Extract exactly {target_topics} distinct and **highly specific** topics.
    - **Granularity Rule:** A topic should cover only 5~10 articles. If it's too broad, split it into sub-events.
    - **CRITICAL:** The topic names (keys in JSON) MUST be written in KOREAN (No underscores, use spaces).

2. **Stance Classification (Based on Explicit Linguistic Markers)**:
    - For each topic, select relevant articles from the input.
    - Classify each article into one of the following three stances:

    * **Factual (Fact-based / Neutral)**:
      - Pure delivery of information (Who, What, Where, When).
      - Absence of emotionally charged adjectives or value judgments.
      - *Standard baseline for journalism.*

    * **Critical (Negative / Opposing)**:
      - Contains linguistic markers of concern, doubt, opposition, blame, or anxiety.
      - (e.g., "Crisis," "Failure," "Plummet," "Threat," "Warning", "Dashed hopes")
      - ✅ **PRIORITY RULE:** Even if the tone is calm/objective, reports focusing on **"bad news," "losses," "failures," or "negative outcomes"** (e.g., "Export thwarted," "Stock crashed") MUST be classified as **'critical'**, NOT 'factual'.

    * **Supportive (Positive / Favoring)**:
      - Contains linguistic markers of hope, praise, agreement, defense, or expectation.
      - (e.g., "Breakthrough," "Surge," "Success," "Welcome," "Recovery")

3. **Constraint**:
    - If the stance is ambiguous, default to 'factual'.
    - Use article numbers [ ] provided in the input.
    - **Ensure EVERY input article ID is assigned to a topic.**

4. **Output Format**:
    - Return ONLY a valid JSON object. No explanations.
    - **Topic names must be in Korean.**
    - Structure:
    {{
      "구체적 토픽명 (한글)": {{
        "factual": [1, 3],
        "critical": [2, 5],
        "supportive": [4]
      }},
      ...
    }}
"""
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"  ❌ LLM Call Failed: {e}")
        return None

def main():
    # Default to RU if no argument, otherwise take from command line
    COUNTRY = sys.argv[1] if len(sys.argv) > 1 else 'RU'
    
    articles = fetch_articles(COUNTRY)
    print(f"Total articles for {COUNTRY}: {len(articles)}")
    
    if not articles:
        print("No articles found.")
        return

    # Balanced Batching
    batches = get_balanced_batches(articles, target_size=200)
    print(f"Split into {len(batches)} balanced batches.")
    for i, b in enumerate(batches):
        print(f"  Batch {i+1}: {len(b)} articles")
    
    all_clusters = {}
    
    for i, batch in enumerate(batches):
        print(f"\n--- Processing Batch {i+1}/{len(batches)} ({len(batch)} articles) ---")
        
        # Retry logic for safety filter (Simple retry, no exclusion for now as per user request to try prompt first)
        # If this fails, we might need to revert to exclusion or embeddings
        clusters = call_llm_clustering(batch, COUNTRY)
        
        if clusters:
            print(f"  ✅ Success! Generated {len(clusters)} topics.")
            # Merge clusters
            for topic, data in clusters.items():
                key = topic
                if key in all_clusters:
                    key = f"{topic}_{i}"
                all_clusters[key] = data
        else:
            print("  ❌ Batch failed completely (likely Safety Filter).")
            
        time.sleep(2)
        
    # Save intermediate result
    output_file = f"data/pipelines/clusters_{COUNTRY}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_clusters, f, ensure_ascii=False, indent=2)
        
    print(f"\n✅ Clustering Complete. Saved to {output_file}")
    print(f"Total Topics: {len(all_clusters)}")
    
    # Preview
    print("\n--- Cluster Preview (First 5) ---")
    for k, v in list(all_clusters.items())[:5]:
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
