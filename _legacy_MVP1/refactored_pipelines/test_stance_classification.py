import os
import json
import requests
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

# Load environment
root_dir = Path(__file__).resolve().parent
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_classification():
    print("Fetching 5 'factual' articles (score 50)...")
    res = supabase.table("mvp_articles").select("id, title, title_en, summary, stance_score").eq("stance_score", 50).limit(5).execute()
    articles = res.data
    
    if not articles:
        print("No articles with score 50 found.")
        return

    print(f"Testing {len(articles)} articles...")
    
    for article in articles:
        print(f"\n--- Article: {article['title']} ---")
        title = article.get('title_en') or article.get('title')
        summary = article.get('summary') or ""
        
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        # New Nuanced Prompt
        prompt_text = f"""
        Analyze the stance, tone, and framing of the following news article regarding its main topic.
        Even if the article is factual, detect any subtle positive or negative implications.
        
        Provide a 'Stance Score' from 0 to 100.
        
        Guidelines:
        - 0-40: Critical / Negative (Focuses on problems, conflicts, failures, or warnings)
        - 41-59: Purely Neutral (Dry statistics, simple announcements without adjectives)
        - 60-100: Supportive / Positive (Focuses on solutions, achievements, progress, or praise)

        * Do NOT default to 50 unless it is absolutely devoid of emotion or bias.
        * If it mentions a crisis, attack, or failure, it is likely Critical (<50).
        * If it mentions a deal, recovery, or success, it is likely Supportive (>50).

        Title: {title}
        Summary: {summary}

        Return JSON format:
        {{
            "score": <int>,
            "category": "<string>"
        }}
        """
        
        data = {
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            if response.ok:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"Gemini Response: {content}")
                else:
                    print("Gemini returned no candidates.")
            else:
                print(f"API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_classification()
