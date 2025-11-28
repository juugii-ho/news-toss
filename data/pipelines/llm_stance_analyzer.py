#!/Users/sml/gemini_env/bin/python
import os
import time
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

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase environment variables not found.")
    exit(1)

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found.")
    exit(1)

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GOOGLE_API_KEY)

# Model configuration
generation_config = {
    "temperature": 0.1,
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

STANCE_PROMPT = """
You are an expert news analyst with no political bias. Your task is to analyze an article's summary to determine its stance towards a specific topic.

DEFINITIONS:
- SUPPORTIVE: The article's tone and content are clearly in favor of the topic, highlighting benefits, positive outcomes, or defending it against criticism.
- NEUTRAL: The article presents information factually without a clear positive or negative slant. It may present both sides of an argument equally.
- CRITICAL: The article's tone and content are clearly against the topic, highlighting risks, negative outcomes, or problems.

RULES:
1. Analyze the stance based *only* on the provided summary.
2. The output MUST be in JSON format.
3. The stance must be one of: 'SUPPORTIVE', 'NEUTRAL', 'CRITICAL'.
4. The confidence_score must be a float between 0.0 and 1.0.
5. The reasoning must be a single, concise sentence in Korean.

Analyze the following input:

Topic: {topic}
Article Summary: {summary}

Output JSON:
"""

def analyze_stance(article):
    """Analyze stance of the article"""
    try:
        topic = article.get('title_original', '')
        summary = article.get('summary_en') or article.get('summary_ko') or ''
        
        if not summary:
            return {"success": False, "error": "No summary available"}
            
        prompt = STANCE_PROMPT.format(topic=topic, summary=summary)
        
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        
        return {
            "success": True,
            "stance": result.get("stance"),
            "confidence_score": result.get("confidence_score"),
            "reasoning": result.get("reasoning"),
            "prompt": prompt
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("Starting LLM Stance Analysis...")
    
    # Fetch articles that need stance analysis (not in mvp2_article_stance)
    # This requires a left join or a "not in" query.
    # Supabase-py doesn't support complex joins easily in one go for "not in".
    # We can fetch articles and check if they exist in stance table, or just try to insert and ignore conflict?
    # But we want to avoid re-analyzing.
    # A better way is to use a stored procedure or just fetch IDs from stance table and filter.
    # For MVP, let's fetch articles and check existence.
    
    try:
        # Fetch all analyzed article IDs
        analyzed_response = supabase.table("mvp2_article_stance").select("article_id").execute()
        analyzed_ids = {item['article_id'] for item in analyzed_response.data}
        
        # Fetch articles
        articles_response = supabase.table("mvp2_articles") \
            .select("id, title_original, summary_en, summary_ko") \
            .not_.is_("summary_en", "null") \
            .execute()
            
        articles = [a for a in articles_response.data if a['id'] not in analyzed_ids]
        
        print(f"Found {len(articles)} articles needing stance analysis.")
        
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return

    success_count = 0
    
    for article in articles:
        print(f"Analyzing: {article['title_original'][:50]}...")
        
        result = analyze_stance(article)
        
        if result['success']:
            try:
                supabase.table("mvp2_article_stance").insert({
                    "article_id": article['id'],
                    "stance": result['stance'],
                    "confidence_score": result['confidence_score'],
                    "model_name": "gemini-2.5-flash"
                }).execute()
                
                print(f"  ✅ Analyzed: {result['stance']} ({result['confidence_score']})")
                success_count += 1
            except Exception as e:
                print(f"  ❌ Insert failed: {e}")
        else:
            print(f"  ❌ Analysis failed: {result['error']}")
            
        time.sleep(1)

    print(f"Stance Analysis Complete. Analyzed {success_count} articles.")

if __name__ == "__main__":
    main()
