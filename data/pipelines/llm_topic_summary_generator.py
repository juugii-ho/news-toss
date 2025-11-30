import os
import json
import argparse
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase setup
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

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

def get_topics_needing_summary(limit=10, force=False, country=None):
    query = supabase.from_("mvp2_topics").select("id, topic_name, country_code, keywords")
    
    if country:
        query = query.eq("country_code", country)

    if not force:
        query = query.is_("ai_summary", "null")
        
    # We might want to filter by recent topics or specific countries
    # For now, let's just take the most recent ones
    query = query.order("created_at", desc=True).limit(limit)
    
    response = query.execute()
    return response.data

def get_topic_headlines(topic_id):
    # Join topics -> topic_articles -> articles
    # Assuming mvp2_topic_articles linking table exists, or direct link
    # Based on previous code, it seems mvp2_articles has local_topic_id
    
    response = supabase.from_("mvp2_articles")\
        .select("title_ko, title_original, source_name")\
        .eq("local_topic_id", topic_id)\
        .limit(10)\
        .execute()
        
    return [a.get('title_ko') or a.get('title_original') for a in response.data]

def generate_summary(country, topic_title, headlines):
    existing_headlines_str = "\n".join([f"- {h}" for h in headlines])
    
    prompt = f"""
다음은 '{country}'의 '{topic_title}'에 대한 기존 기사들의 헤드라인 목록입니다.

[기존 헤드라인]
{existing_headlines_str}

이 헤드라인의 맥락을 기반으로 Google Search를 사용하여,
새롭게 업데이트된 후속 기사나, 기존 기사에 깊이를 더하는 최신 기사를 검색해 이 토픽을 모르는 이들을 위한 육하원칙을 드러나지 않게 녹여낸 500자 이내의 쉽고 친절하며 자상한 말투로 상세한 설명해 주세요.
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
    parser = argparse.ArgumentParser(description="Generate AI summaries for local topics")
    parser.add_argument("--limit", type=int, default=5, help="Number of topics to process per batch (or per country)")
    parser.add_argument("--force", action="store_true", help="Reprocess topics that already have summaries")
    parser.add_argument("--all", action="store_true", help="Process all topics in batches")
    parser.add_argument("--per-country", action="store_true", help="Process top N topics per country")
    args = parser.parse_args()

    if args.per_country:
        # List of countries to process
        countries = ["KR", "US", "JP", "CN", "GB", "FR", "DE", "IT", "CA", "AU", "NL", "BE", "RU", "UA", "IL"]
        print(f"Processing top {args.limit} topics for each of {len(countries)} countries...")
        
        for country in countries:
            print(f"\n--- Processing Country: {country} ---")
            topics = get_topics_needing_summary(args.limit, args.force, country=country)
            if not topics:
                print(f"No topics found for {country}")
                continue
            
            print(f"Found {len(topics)} topics for {country}")
            process_batch(topics)

    elif args.all:
        print("Processing ALL topics in batches...")
        while True:
            topics = get_topics_needing_summary(args.limit, args.force)
            if not topics:
                print("No more topics to process.")
                break
            
            print(f"Processing batch of {len(topics)} topics...")
            process_batch(topics)
    else:
        topics = get_topics_needing_summary(args.limit, args.force)
        print(f"Found {len(topics)} topics to process")
        process_batch(topics)

def process_batch(topics):
    for topic in topics:
        print(f"\nProcessing: {topic['topic_name']} ({topic['country_code']})")
        headlines = get_topic_headlines(topic['id'])
        
        if not headlines:
            print("  - No headlines found, skipping")
            continue
            
        summary = generate_summary(topic['country_code'], topic['topic_name'], headlines)
        
        if summary:
            print("  - Summary generated, updating DB...")
            # Update DB
            supabase.from_("mvp2_topics").update({"ai_summary": summary}).eq("id", topic['id']).execute()
            print("  - Done")
        else:
            print("  - Failed to generate summary")

if __name__ == "__main__":
    main()
