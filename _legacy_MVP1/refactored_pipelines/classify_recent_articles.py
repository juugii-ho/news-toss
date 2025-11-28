import os
import time
import json
import requests
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

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

def classify_recent_articles():
    print("Fetching recent topics (last 2 days)...")
    # Fetch topics created recently (or just all active ones?)
    # Let's fetch topics that have articles with null stance
    
    # 1. Get IDs of articles with null stance
    print("Fetching unclassified articles...")
    res = supabase.table("mvp_articles").select("id, title, title_en, summary, topic_id").is_("stance_score", "null").limit(200).execute()
    articles = res.data
    
    if not articles:
        print("No unclassified articles found.")
        return
        
    print(f"Found {len(articles)} unclassified articles. Processing...")
    
    processed_count = 0
    
    for article in articles:
        title = article.get('title_en') or article.get('title')
        summary = article.get('summary') or ""
        
        if not title:
            continue
            
        # Prompt
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
        
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
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
                    parsed = json.loads(content)
                    score = parsed.get('score')
                    category = parsed.get('category')
                    
                    # Normalize category
                    cat_lower = category.lower()
                    if 'critical' in cat_lower or 'negative' in cat_lower:
                        final_stance = 'critical'
                    elif 'supportive' in cat_lower or 'positive' in cat_lower:
                        final_stance = 'supportive'
                    else:
                        final_stance = 'factual'
                    
                    # Update Supabase
                    supabase.table("mvp_articles").update({
                        "stance": final_stance,
                        "stance_score": score
                    }).eq("id", article['id']).execute()
                    
                    processed_count += 1
                    print(f"[{processed_count}/{len(articles)}] Classified: {title[:30]}... -> {score}")
                else:
                    print(f"No candidates for {article['id']}")
            else:
                print(f"API Error: {response.status_code}")
                time.sleep(2) # Backoff
                
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(0.5) # Rate limit
        
    print("Done.")

if __name__ == "__main__":
    classify_recent_articles()
