import os
import json
import time
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load env
# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
load_dotenv(os.path.join(project_root, 'backend', '.env'))

# Setup Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    print("❌ GOOGLE_API_KEY not found.")
    exit(1)

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

# Setup Supabase
url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("❌ Supabase credentials not found.")
    exit(1)

supabase: Client = create_client(url, key)

def fetch_article_titles(article_ids):
    """Fetch up to 3 article titles for context."""
    if not article_ids:
        return []
    try:
        # Limit to 3 IDs to avoid huge queries
        target_ids = article_ids[:3]
        response = supabase.table("mvp2_articles").select("title_ko, title_original").in_("id", target_ids).execute()
        titles = []
        for row in response.data:
            # Prefer Korean title, fallback to original
            t = row.get('title_ko') or row.get('title_original')
            if t:
                titles.append(t)
        return titles
    except Exception as e:
        print(f"    ⚠️ Failed to fetch articles: {e}")
        return []

def generate_headline(title, context="", article_titles=[]):
    """
    Generate a witty, Newneek-style headline for a given title.
    """
    articles_context = ""
    if article_titles:
        articles_context = "\nRelated Articles (Use these for facts):\n" + "\n".join([f"- {t}" for t in article_titles])

    prompt = f"""
Role: Professional News Editor for Gen-Z (Newneek Style)
Task: Rewrite the following news title into a catchy, conversational, yet INFORMATIVE headline.

Original Title: {title}
Context: {context}{articles_context}

Rules:
1. Tone: Smart, friendly, and clear. Like a knowledgeable friend explaining the news.
2. Structure: Use "Hook: Summary" or "Fact + Context" structure.
3. Prohibition: Avoid vague clickbait questions (e.g., "Why is this happening?"). Explain WHAT is happening.
4. Prohibition: NEVER end with a noun (e.g., "논란", "개최"). Use complete sentences.
5. Prohibition: NO SENSATIONALISM. Do not use words like "충격", "멘붕", "경악", "썰", "알고보니". Stick to facts.
6. Length: Under 60 characters.
7. Language: Korean.
8. Emoji: Optional, max 1.

Examples (Good):
- "유니클로X니들스 협업, 왜 이렇게 화제일까? 🔥: 패스트 패션이 만들어가는 새로운 콜라보의 세계"
- "445억 원 규모 업비트 해킹 사고: 배후에 북한 해킹 조직이 있다는 말이 나오는 이유"
- "법원: “방통위의 유진그룹 YTN 인수 승인 결정은 취소야!” 🧑‍⚖️"
- "서울영화센터 개관, 내년 3월까지 충무로에서 공짜 영화 보는 법 🎥"

Examples (Bad - Avoid these styles):
- "기자들 멘붕시킨 썰: 알고 보니 충격적 사실! 😱" (Too clickbaity/YouTube style)
- "트럼프, 마약 전 대통령 풀어준다고? 🤔" (Too vague)
- "협박범 체포 소식, 왜 나만 몰라?" (Too personal/vague)

Output: Just the headline string.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '').replace("'", "")
    except Exception as e:
        print(f"    ⚠️ Headline generation failed: {e}")
        return None

def process_megatopics():
    print("\n🌍 Processing Global Megatopics...")
    try:
        # Calculate 24 hours ago
        time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        
        response = supabase.table("mvp2_megatopics") \
            .select("*") \
            .gte("created_at", time_threshold) \
            .order("total_articles", desc=True) \
            .execute()
            
        topics = response.data
        print(f"Found {len(topics)} recent megatopics.")
        
        count = 0
        for t in topics:
            # Force regeneration
            # if t.get('headline'): continue
                
            print(f"  Generating headline for: {t['name']}")
            
            # Fetch representative articles from the first topic in this megatopic
            article_titles = []
            if t.get('topic_ids') and len(t['topic_ids']) > 0:
                # Get the first local topic to find article IDs
                first_topic_id = t['topic_ids'][0]
                topic_res = supabase.table("mvp2_topics").select("article_ids").eq("id", first_topic_id).execute()
                if topic_res.data and topic_res.data[0].get('article_ids'):
                    article_titles = fetch_article_titles(topic_res.data[0]['article_ids'])

            headline = generate_headline(t['name'], f"Keywords: {t.get('keywords', [])}", article_titles)
            if headline:
                print(f"    -> {headline}")
                supabase.table("mvp2_megatopics").update({"headline": headline}).eq("id", t['id']).execute()
                time.sleep(1) # Rate limit
                count += 1
            else:
                print("    -> Failed.")
        print(f"Generated {count} new headlines.")
                
    except Exception as e:
        print(f"❌ Error processing megatopics: {e}")

def process_local_topics():
    print("\n🇰🇷 Processing Local Topics (KR)...")
    try:
        # Calculate 24 hours ago
        time_threshold = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        
        response = supabase.table("mvp2_topics") \
            .select("*") \
            .eq("country_code", "KR") \
            .gte("created_at", time_threshold) \
            .order("article_count", desc=True) \
            .execute()
            
        topics = response.data
        print(f"Found {len(topics)} recent local topics.")
        
        count = 0
        for t in topics:
            # Force regeneration
            # if t.get('headline'): continue

            print(f"  Generating headline for: {t['topic_name']}")
            
            # Fetch articles
            article_titles = []
            if t.get('article_ids'):
                article_titles = fetch_article_titles(t['article_ids'])
            
            headline = generate_headline(t['topic_name'], f"Summary: {t.get('summary', '')}", article_titles)
            if headline:
                print(f"    -> {headline}")
                supabase.table("mvp2_topics").update({"headline": headline}).eq("id", t['id']).execute()
                time.sleep(1)
                count += 1
            else:
                print("    -> Failed.")
        print(f"Generated {count} new headlines.")

    except Exception as e:
        print(f"❌ Error processing local topics: {e}")

def main():
    print("🚀 Starting Headline Generator...")
    process_megatopics()
    process_local_topics()
    print("✅ Headline Generation Complete.")

if __name__ == "__main__":
    main()
