import os
import json
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
env_path = os.path.join(project_root, 'backend', '.env')
load_dotenv(env_path)

# Init Gemini
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash-lite') # Use the lite model as configured

# Init Supabase
url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def test_labeling():
    print("🚀 Starting Labeling Test...")
    
    # 1. Fetch 5 random articles from KR
    print("Fetching 5 articles from KR...")
    response = supabase.table("mvp2_articles") \
        .select("id, title_en, title_ko") \
        .eq("country_code", "KR") \
        .limit(5) \
        .execute()
        
    articles = response.data
    if not articles:
        print("❌ No articles found.")
        return

    print(f"Fetched {len(articles)} articles.")
    
    # 2. Construct Prompt (EXACTLY as in the main script)
    input_text = "\n".join([f"[{a['id']}] {a['title_en']}" for a in articles])
    
    prompt = f"""
Role: Expert Media Analyst
Task: Analyze these {len(articles)} news headlines about the SAME event.

Input:
{input_text}

Requirements:
1. **Topic Name**: Create a specific, descriptive topic name in KOREAN.
2. **Stance**: Analyze the stance of each article (factual/critical/supportive).
3. **Keywords**: Extract 3-5 key entities/keywords (KOREAN).
4. **Category**: Classify into one of: Politics, Economy, Society, World, Tech, Culture, Sports.

Output JSON:
{{
  "topic_name": "Topic Name in Korean",
  "keywords": ["Keyword1", "Keyword2"],
  "category": "Category Name",
  "stances": {{
    "factual": [id, id],
    "critical": [id],
    "supportive": []
  }}
}}
"""
    print("\n--- Prompt Sent to LLM ---")
    print(prompt[:500] + "...")
    
    # 3. Call LLM
    print("\n⏳ Calling Gemini...")
    try:
        response = model.generate_content(prompt)
        text = response.text
        print(f"\n🔍 Raw LLM Response:\n{text}")
        
        # 4. Test Parsing Logic
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        parsed = json.loads(text)
        print("\n✅ Parsed JSON:")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
        
        # Check fields
        if "keywords" in parsed and parsed["keywords"]:
            print("\n🎉 Keywords found!")
        else:
            print("\n⚠️ Keywords MISSING or EMPTY.")
            
        if "category" in parsed and parsed["category"] != "Unclassified":
            print("🎉 Category found!")
        else:
            print("⚠️ Category MISSING or Unclassified.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_labeling()
