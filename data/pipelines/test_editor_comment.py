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
supabase: Client = create_client(url, key)

# Gemini setup
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
model_id = "gemini-2.5-flash"
google_search_tool = Tool(google_search=GoogleSearch())

def get_test_topic():
    # Find a topic with the most countries
    response = supabase.from_("mvp2_global_topics").select("*").limit(50).execute()
    
    best_topic = None
    max_countries = 0
    
    print(f"Fetched {len(response.data)} topics.")
    for topic in response.data:
        countries = topic.get('countries') or []
        print(f"Topic: {topic.get('title_ko')}, Countries: {len(countries)}")
        if len(countries) > max_countries:
            max_countries = len(countries)
            best_topic = topic
            
    if not best_topic and response.data:
        print("No topic with countries found. Using the first topic as fallback.")
        best_topic = response.data[0]
            
    if best_topic:
        print(f"Selected topic '{best_topic.get('title_ko')}' with {max_countries} countries.")
    else:
        print("No topics found in the first 50 results.")
        
    return best_topic

def get_global_topic_context(global_topic_id):
    response = supabase.from_("mvp2_articles")\
        .select("title_ko, title_original, source_name, country_code")\
        .eq("global_topic_id", global_topic_id)\
        .limit(30)\
        .execute()
    return response.data

def generate_editor_comment(topic_title, articles):
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
    당신은 글로벌 뉴스 큐레이션 서비스 '뉴스 스펙트럼'의 메인 에디터입니다.
    당신의 페르소나는 **'세상 돌아가는 일에 밝고, 위트 있는, 친한 친구'**입니다.
    더 스키머(The Skimm)나 뉴닉(NEWNEEK)처럼 **쉽고, 재밌고, 쫀득한 문체**를 구사합니다.

    아래 데이터를 분석하여, 독자가 쉽고 재미있게 읽을 수 있는 고품질의 에디터 분석글을 작성해주세요.
    
    [분석 대상 토픽]: {topic_title}
    [관련 기사 헤드라인]:
    {context_str}

    ====================================================
    🚫 절대 어기면 안 되는 규칙 (Strict Rules)
    ====================================================
    1. **헤더 괄호 사용 금지:**
       - 국가별 헤더 요약문에 **절대 괄호()를 넣지 마세요.** `|` 뒤에 바로 문장을 쓰세요.
       - ❌ `## 🇰🇷 한국 | (안타까운 소식)` -> ⭕️ `## 🇰🇷 한국 | 안타까운 사고 소식이 들려왔어요`

    2. **속마음 문장화:**
       - '비판', '옹호' 단어 금지. **그 나라의 입장을 대변하는 구어체 문장**을 쓰세요.
       - ❌ `🇺🇸(비판)` -> ⭕️ `🇺🇸("이거 진짜 위험한 거 아냐?")`

    3. **이모지 제어:**
       - **고슴도치(🦔) 절대 사용 금지.**
       - 문장 중간/끝에 장식용 이모지(😊, 😢) 금지. 텍스트로만 담백하게.
       - (국기, 섹션 아이콘은 허용)

    4. **톤앤매너 차별화:**
       - 일반 토픽: "그거 들었어?", "~더라고요" (친근한 대화체)
       - **사건/사고/범죄:** "사상자가 발생했습니다", "논란이 되고 있습니다" (건조하고 차분한 뉴스 톤)

    5. **인용의 투명성 (Source Attribution):**
       - 🇷🇺러시아 매체가 🇺🇦우크라이나 소식을 전할 때 등, 매체 국적과 내용의 국적이 다르면 "러시아 언론이 인용한 우크라이나의 입장은~" 처럼 출처 관계를 명확히 밝히세요.


    ====================================================
    📝 작성 구조 (Output Structure)
    ====================================================


    ### 에디터의 시선 🧐

    **"여기에 호기심을 자극하는 낚시성 부제 작성"**
    (이 이슈가 왜 핫한지 배경 설명. 문장 내 이모지 사용 금지)

    **⚡ 결정적 차이** 
        🇺🇸("짧은 속마음 문장") 
    vs 🇨🇳("짧은 속마음 문장") 
    vs 🇪🇺("짧은 속마음 문장")

    (상세 설명: "미국은 ~라고 걱정하는데, 중국은 오히려 ~라며 반기는 분위기예요. 그 이유는...", 문장 내 이모지 사용 금지)
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
        return f"Error: {e}"

def main():
    topic = get_test_topic()
    if not topic:
        print("No suitable topic found (>= 3 countries).")
        return

    print(f"Testing with topic: {topic.get('title_ko') or topic.get('title_en')} (ID: {topic['id']})")
    articles = get_global_topic_context(topic['id'])
    
    result = generate_editor_comment(topic.get('title_ko') or topic.get('title_en'), articles)
    print("\n--- Generated Output ---\n")
    print(result)

if __name__ == "__main__":
    main()
