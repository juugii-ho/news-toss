import os
import json
import argparse
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase setup
url: str = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key: str = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise ValueError("Supabase credentials not found in environment variables")

supabase: Client = create_client(url, key)

# Gemini setup
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=GEMINI_API_KEY)
model_id = "gemini-2.5-flash"
google_search_tool = Tool(
    google_search = GoogleSearch()
)

def get_global_topics_needing_summary(limit=10, force=False):
    query = supabase.from_("mvp2_global_topics").select("id, title_ko, title_en")
    
    if not force:
        query = query.is_("ai_summary", "null")
        
    query = query.order("created_at", desc=True).limit(limit)
    
    response = query.execute()
    return response.data

def get_global_topic_context(global_topic_id):
    # Fetch related articles (limit 20 for context)
    response = supabase.from_("mvp2_articles")\
        .select("title_ko, title_original, source_name, country_code")\
        .eq("global_topic_id", global_topic_id)\
        .limit(20)\
        .execute()
        
    return response.data

def generate_summary(topic_title, articles):
    # Group headlines by country for better context
    headlines_by_country = {}
    for a in articles:
        cc = a.get('country_code') or "Unknown"
        title = a.get('title_ko') or a.get('title_original')
        if cc not in headlines_by_country:
            headlines_by_country[cc] = []
        headlines_by_country[cc].append(title)
        
    context_str = ""
    for cc, titles in headlines_by_country.items():
        context_str += f"\n[{cc}]\n" + "\n".join([f"- {t}" for t in titles])
    
    prompt = f"""
다음은 글로벌 토픽 '{topic_title}'에 대한 국가별 주요 기사 헤드라인입니다.

[기사 헤드라인]
{context_str}

이 헤드라인들의 맥락을 종합하고 Google Search를 활용하여,
이 글로벌 이슈가 현재 어떤 상황인지, 각국은 어떤 입장을 보이고 있는지,
이 토픽을 처음 접하는 사람도 이해하기 쉽게 육하원칙을 자연스럽게 녹여내어 500자 이내로 설명해 주세요.
말투는 쉽고 친절하며 자상하게(해요체) 작성해 주세요.
결과는 JSON 형식이 아닌, 순수 텍스트로 작성해 주세요. 제목이나 서두 없이 바로 본문 내용을 작성해 주세요.
"""

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=GenerateContentConfig(
                tools=[google_search_tool]
            )
        )
        return response.text
    except Exception as e:
        print(f"❌ Gemini API Error for {topic_title}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate AI summaries for global topics")
    parser.add_argument("--limit", type=int, default=5, help="Number of topics to process")
    parser.add_argument("--force", action="store_true", help="Reprocess topics that already have summaries")
    parser.add_argument("--all", action="store_true", help="Process all topics in batches")
    args = parser.parse_args()

    if args.all:
        print("Processing ALL global topics in batches...")
        while True:
            topics = get_global_topics_needing_summary(args.limit, args.force)
            if not topics:
                print("No more topics to process.")
                break
            
            print(f"Processing batch of {len(topics)} topics...")
            process_batch(topics)
    else:
        topics = get_global_topics_needing_summary(args.limit, args.force)
        print(f"Found {len(topics)} topics to process")
        process_batch(topics)

def process_batch(topics):
    for topic in topics:
        title = topic.get('title_ko') or topic.get('title_en')
        print(f"\nProcessing: {title}")
        
        articles = get_global_topic_context(topic['id'])
        
        if not articles:
            print("  - No related articles found, skipping")
            continue
            
        summary = generate_summary(title, articles)
        
        if summary:
            print("  - Summary generated, updating DB...")
            supabase.from_("mvp2_global_topics").update({"ai_summary": summary}).eq("id", topic['id']).execute()
            print("  - Done")
        else:
            print("  - Failed to generate summary")

if __name__ == "__main__":
    main()
