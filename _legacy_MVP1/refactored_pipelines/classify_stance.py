import json
import os
import time
import requests
from dotenv import load_dotenv
from pathlib import Path
from supabase import create_client, Client

# Load environment variables
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env") # Fallback

url: str = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def classify_stance_gemini_batch(articles):
    """
    Classify stance using Gemini REST API in batch (if possible) or loop.
    Gemini doesn't support batch classification easily in one prompt without complex parsing.
    For now, we will loop with sequential with rate limit handling.
    """
    results = []
    
    for article in articles:
        title = article.get('title_en') or article.get('title')
        summary = article.get('summary') or ""
        
        if not title:
            continue
            
        # Mock fallback if no API key
        if not GEMINI_API_KEY:
            results.append({
                "id": article['id'],
                "stance": "factual",
                "stance_score": 50
            })
            continue

        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
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

        success = False
        for attempt in range(3):
            try:
                response = requests.post(api_url, headers=headers, json=data, timeout=30)
                if response.status_code == 429 or response.status_code == 503:
                    print(f"  [API Error] {response.status_code} - Rate Limit/Service Unavailable. Retrying in {2 ** attempt}s...")
                    time.sleep(2 ** attempt)
                    continue
                
                if response.ok:
                    result = response.json()
                    if 'candidates' in result and result['candidates']:
                        content = result['candidates'][0]['content']['parts'][0]['text']
                        parsed = json.loads(content)
                        category = parsed.get('category', 'factual').lower()
                        score = parsed.get('score', 50)
                        
                        # Normalize category
                        if 'support' in category: category = 'supportive'
                        elif 'critic' in category: category = 'critical'
                        else: category = 'factual'
                        
                        results.append({
                            "id": article['id'],
                            "stance": category,
                            "stance_score": score
                        })
                        success = True
                        break
            except Exception as e:
                print(f"Error classifying article {article['id']}: {e}. Retrying...")
                time.sleep(1)
        
        if not success:
            # Fallback to factual on failure
            results.append({
                "id": article['id'],
                "stance": "factual",
                "stance_score": 50
            })
            
        # Rate limit pause (Gemini free tier is ~15 RPM, so 4s delay is safe, but slow. 
        # We can try 1s and rely on retry.)
        time.sleep(1) 
        
    return results

def process_stances():
    print("Fetching articles needing stance classification...")
    
    while True:
        # Fetch articles where stance is NULL
        response = supabase.table("mvp_articles").select("id, title, title_en, summary").is_("stance", "null").limit(50).execute() # Limit to 50 for batch
        articles = response.data
        
        if not articles:
            print("No more articles to classify.")
            break
    
        print(f"Classifying batch of {len(articles)} articles...")
        results = classify_stance_gemini_batch(articles)
        
        print(f"Updating {len(results)} articles in Supabase...")
        for res in results:
            try:
                supabase.table("mvp_articles").update({
                    "stance": res['stance'],
                    "stance_score": res['stance_score']
                }).eq("id", res['id']).execute()
            except Exception as e:
                print(f"Error updating article {res['id']}: {e}")
            
        # Small pause between batches
        time.sleep(1)
        
    print("Done.")

if __name__ == "__main__":
    process_stances()
            

