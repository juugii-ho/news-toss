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
    "temperature": 0.4, # Slightly higher for "witty" tone
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 2048,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    generation_config=generation_config,
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
)

# User's requested prompt adapted for JSON output
VS_CARD_PROMPT = """
당신은 글로벌 뉴스 큐레이션 서비스 '뉴스 스펙트럼'의 메인 에디터입니다.
당신의 페르소나는 **'세상 돌아가는 일에 밝고, 위트 있는, 친한 친구'**입니다.
더 스키머(The Skimm)나 뉴닉(NEWNEEK)처럼 **쉽고, 재밌고, 쫀득한 문체**를 구사합니다.

아래 제공된 [기사 목록]을 분석하여, 이 이슈에 대한 **국가별 혹은 입장별 대립 구도(VS Card)**를 추출해주세요.

====================================================
🚫 절대 어기면 안 되는 규칙 (Strict Rules)
====================================================
1. **속마음 문장화:**
   - '비판', '옹호' 같은 딱딱한 단어 대신, **그 나라/입장의 속마음을 대변하는 구어체 문장**을 쓰세요.
   - 예: 🇺🇸(비판) -> 🇺🇸("이거 진짜 위험한 거 아냐?")
2. **이모지 제어:**
   - 문장 중간/끝에 장식용 이모지(😊, 😢) 금지. 텍스트로만 담백하게.
   - 단, **국기 이모지**는 필수입니다.
3. **인용의 투명성:**
   - 출처 관계를 명확히 하세요.
4. **JSON 출력:**
   - 결과는 반드시 아래 정의된 JSON 포맷으로만 출력해야 합니다.

====================================================
데이터:
[토픽 제목]: {topic_title}
[기사 목록]:
{articles_text}
====================================================

<출력 포맷 (JSON)>
{{
  "stances": [
    {{
      "country_code": "US", // ISO 2자리 코드 (알 수 없으면 'GLOBAL')
      "country_name_ko": "미국",
      "flag_emoji": "🇺🇸",
      "stance": "우려/반대/환영 등 (한 단어 요약)",
      "one_liner_ko": "짧은 속마음 문장 (구어체)",
      "summary_ko": "이 입장에 대한 1-2문장 설명 (친근한 해요체)",
      "source_link": "대표 기사 URL (없으면 null)"
    }},
    ... (최대 3개 입장)
  ],
  "one_line_question": "이 이슈를 관통하는 흥미로운 질문 하나 (예: 미국은 왜 반대할까요?)"
}}
"""

def analyze_megatopic_stances(megatopic):
    """Analyze stances for a megatopic"""
    try:
        topic_id = megatopic['id']
        title = megatopic.get('name') or megatopic.get('title')
        
        # Fetch related articles (limit 10 for context)
        # Assuming megatopic has 'article_ids' or we query by topic_id mapping
        # For MVP2, megatopics map to topics, topics map to articles.
        # Let's try to fetch articles linked to the topics in this megatopic.
        
        topic_ids = megatopic.get('topic_ids', [])
        if not topic_ids:
            return {"success": False, "error": "No topics linked"}

        # Fetch articles for these topics
        articles_response = supabase.table("mvp2_articles") \
            .select("title_original, source_name, url, summary_ko") \
            .in_("local_topic_id", topic_ids) \
            .limit(15) \
            .execute()
            
        articles = articles_response.data
        if not articles:
            return {"success": False, "error": "No articles found"}

        # Format articles for prompt
        articles_text = ""
        for i, art in enumerate(articles):
            articles_text += f"{i+1}. [{art['source_name']}] {art['title_original']}\n   Summary: {art.get('summary_ko', '')}\n   URL: {art['url']}\n\n"

        prompt = VS_CARD_PROMPT.format(topic_title=title, articles_text=articles_text)
        
        # Generate
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        
        return {
            "success": True,
            "stances": result.get("stances", []),
            "one_line_question": result.get("one_line_question", "")
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("Starting LLM VS Card Analysis (Megatopics)...")
    
    # Fetch recent megatopics that don't have stances yet
    # Or just fetch all recent ones for update
    try:
        response = supabase.table("mvp2_megatopics") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(5) \
            .execute()
            
        megatopics = response.data
        print(f"Found {len(megatopics)} megatopics.")
        
    except Exception as e:
        print(f"Error fetching megatopics: {e}")
        return

    for mt in megatopics:
        print(f"Analyzing: {mt.get('name')}...")
        
        result = analyze_megatopic_stances(mt)
        
        if result['success']:
            try:
                # Update megatopic with stances
                supabase.table("mvp2_megatopics").update({
                    "stances": result['stances'],
                    "intro_ko": result['one_line_question'] # Use the question as intro/hook
                }).eq("id", mt['id']).execute()
                
                print(f"  ✅ Updated Stances: {len(result['stances'])} perspectives found.")
            except Exception as e:
                print(f"  ❌ Update failed: {e}")
        else:
            print(f"  ❌ Analysis failed: {result['error']}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()
