#!/Users/sml/gemini_env/bin/python
import os
import time
import json
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client, Client
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40,
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

UNIVERSAL_TRANSLATION_PROMPT = """
You are a professional news translator. Translate the provided news article content into Korean and English.

RULES:
1. Maintain a neutral, journalistic tone.
2. Output MUST be in JSON format with "title_ko", "summary_ko", "title_en", "summary_en" keys.
3. If summary is missing, return empty strings for summary fields.
"""

def process_article(article):
    """Process a single article with fallback logic"""
    try:
        # 1. Try Title + Summary
        prompt = f"""
{UNIVERSAL_TRANSLATION_PROMPT.strip()}

Input:
Title: {article.get('title_original', '')}
Summary: {article.get('summary_original') or ''}

Output JSON:
"""
        try:
            response = model.generate_content(prompt)
            result = json.loads(response.text)
        except Exception:
            # 2. Fallback: Title Only
            prompt = f"""
{UNIVERSAL_TRANSLATION_PROMPT.strip()}

Input (TITLE ONLY):
Title: {article.get('title_original', '')}
Summary: (No summary provided)

Output JSON:
"""
            response = model.generate_content(prompt)
            result = json.loads(response.text)

        # Prepare update data
        update_data = {}
        if not article['title_ko']: update_data['title_ko'] = result.get('title_ko')
        if not article['title_en']: update_data['title_en'] = result.get('title_en')
        if not article['summary_ko']: update_data['summary_ko'] = result.get('summary_ko') or ""
        if not article['summary_en']: update_data['summary_en'] = result.get('summary_en') or ""
        
        if update_data:
            supabase.table("mvp2_articles").update(update_data).eq("id", article['id']).execute()
            return True, article['title_original']
        return False, "No updates needed"

    except Exception as e:
        return False, str(e)

def main():
    print("Starting Parallel LLM Translation...")
    
    try:
        # Fetch articles needing translation
        # Optimized query: check if ANY target field is null, but avoid fully completed ones
        response = supabase.table("mvp2_articles") \
            .select("id, title_original, summary_original, title_ko, title_en, summary_ko, summary_en") \
            .not_.is_("summary_original", "null") \
            .or_("title_ko.is.null,title_en.is.null") \
            .execute()
            
        articles = response.data
        print(f"Found {len(articles)} articles needing translation.")
        
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return

    success_count = 0
    total = len(articles)
    
    # Parallel Processing
    MAX_WORKERS = 20  # Increased to 20 for higher throughput
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_article = {executor.submit(process_article, article): article for article in articles}
        
        for i, future in enumerate(as_completed(future_to_article)):
            article = future_to_article[future]
            try:
                success, msg = future.result()
                if success:
                    success_count += 1
                    print(f"[{i+1}/{total}] ✅ {msg[:30]}...")
                else:
                    print(f"[{i+1}/{total}] ❌ {article['title_original'][:30]}... : {msg}")
            except Exception as exc:
                print(f"[{i+1}/{total}] 💥 Exception: {exc}")
                
            # Rate limit throttling if needed (Gemini Flash has high limits, but good to be safe)
            # With 10 workers, we might hit RPM limits. If so, reduce workers or add sleep.
            
    print(f"Translation Complete. Updated {success_count}/{total} articles.")

if __name__ == "__main__":
    main()