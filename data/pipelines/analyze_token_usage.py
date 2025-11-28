#!/Users/sml/gemini_env/bin/python
import os
import json
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

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def count_tokens(text):
    return model.count_tokens(text).total_tokens

def main():
    print("Fetching one article per source...")
    
    # Get all sources
    sources = supabase.table("mvp2_news_sources").select("id, name").execute().data
    
    samples = []
    for source in sources:
        # Get one article for this source
        resp = supabase.table("mvp2_articles") \
            .select("title_original, summary_original") \
            .eq("source_id", source['id']) \
            .not_.is_("summary_original", "null") \
            .limit(1) \
            .execute()
        
        if resp.data:
            samples.append({
                "source": source['name'],
                "title": resp.data[0]['title_original'],
                "summary": resp.data[0]['summary_original']
            })

    print(f"Collected {len(samples)} samples.")
    
    total_input_tokens = 0
    max_input_tokens = 0
    
    # Estimate output tokens (Translation + JSON overhead)
    # Rule of thumb: Korean tokens are roughly 1.5x-2x English words, but token count API handles this.
    # We will assume output length is roughly 1.5x input length (conservative for translation) + JSON keys.
    
    print("\n--- Token Analysis ---")
    for s in samples[:5]: # Show first 5 details
        text = f"Title: {s['title']}\nSummary: {s['summary']}"
        tokens = count_tokens(text)
        print(f"[{s['source']}] Input Tokens: {tokens}")
        
    all_tokens = [count_tokens(f"Title: {s['title']}\nSummary: {s['summary']}") for s in samples]
    avg_input = sum(all_tokens) / len(all_tokens)
    max_input = max(all_tokens)
    
    # JSON Overhead per item roughly:
    # "title_ko": "...", "summary_ko": "...", "title_en": "...", "summary_en": "..."
    # Plus braces and newlines.
    # Let's estimate output tokens per article as: Input Tokens * 2 (Translation x2 for KR/EN) + 50 (JSON overhead)
    
    avg_output_per_article = (avg_input * 2.5) + 50 # 2.5x to be safe (KR + EN translation)
    
    print(f"\nAverage Input Tokens per Article: {avg_input:.2f}")
    print(f"Max Input Tokens per Article: {max_input}")
    print(f"Estimated Output Tokens per Article: {avg_output_per_article:.2f}")
    
    # Target: 80% of Max Output Tokens (8192 for Flash usually, but let's check model info or assume 8192)
    # Actually Gemini 1.5 Flash has 8192 output token limit.
    TARGET_OUTPUT_LIMIT = 8192 * 0.8
    
    batch_size = int(TARGET_OUTPUT_LIMIT / avg_output_per_article)
    
    print(f"\n--- Recommendation ---")
    print(f"Target Output Token Limit (80%): {TARGET_OUTPUT_LIMIT:.0f}")
    print(f"Recommended Batch Size: {batch_size}")
    
    # Safety cap
    if batch_size > 50:
        print("(Capped at 50 for safety)")
        batch_size = 50
        
    print(f"Final Batch Size: {batch_size}")

if __name__ == "__main__":
    main()
