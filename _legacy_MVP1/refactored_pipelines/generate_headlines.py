import os
import json
import requests
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env.local')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not GEMINI_API_KEY:
    print("Error: Environment variables missing.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_headlines_batch(titles):
    """
    Generate headlines for a batch of titles using Gemini 2.5 Flash
    """
    prompt = """
    You are a witty and sensible editor for 'News Spectrum', a Gen-Z targeted news service like Newneek.
    Your goal is to rewrite hard news titles into engaging and conversational headlines, BUT maintain journalistic integrity.
    
    Rules:
    1. Tone: Casual, friendly, and curious. Like a friend telling you breaking news.
    2. Style: Use questions ("왜 그럴까?"), exclamations ("충격!"), or short summaries.
    3. Prohibition 1: NEVER end with a noun (e.g., "논란", "개최", "발표"). Always use a complete sentence or a question.
    4. Prohibition 2: NO CLICKBAIT. Do not exaggerate or mislead. Stick to the facts.
    5. Length: Keep it short (under 45 chars).
    6. Language: Korean.
    7. Emojis: Allowed if relevant (use sparingly).

    Examples:
    - Input: "‘최악의 참사’ 홍콩 아파트 화재, 피해 키운 원인은 ‘대나무 비계’였다?"
    - Output: "홍콩 아파트 화재가 ‘최악의 참사’ 되어버린 2가지 이유"

    - Input: "“내 집에 누가 사는지 알고 싶어!” ‘임차인 면접 제도’가 뜨거운 감자로 떠오른 이유"
    - Output: "전셋집 구하고 싶으면 면접부터 보라고요? 🏠"

    - Input: "사상 최고 실적 기록한 엔비디아, ‘AI 거품론’에 “엔비디아는 다르다?”"
    - Output: "“AI? 거품 맞아. 언빌리버블.” 사상 최고 실적 기록한 엔비디아"

    - Input: "제2의 닷컴버블? AI 버블론 반복되는 이유와 ‘순환거래’ 논란 분석"
    - Output: "제2의 닷컴버블? AI 거품론 반복되는 이유, ‘순환거래’가 뭐길래?"

    - Input: "누리호 4차 발사 성공, 민간 기업이 이끄는 ‘뉴 스페이스’ 시대 첫걸음 뗀 거라고?"
    - Output: "대한민국은 누리호 타고 ‘뉴 스페이스’ 시대로 갑니다 🚀"

    - Input: "감사원 윤석열 정부 의대 증원 감사 결과: “근거도 절차도 부족했어!”"
    - Output: "윤석열 정부 의대 증원, 근거도 부족한데 밀어붙인 거였다고?"

    - Input: "1050원짜리 ‘초코파이 절도’ 사건, 항소심이 ‘무죄’ 선고한 이유"
    - Output: "‘초코파이 절도’ 사건의 결말: “무죄를 선고합니다.”"

    Input Titles:
    """ + json.dumps(titles, ensure_ascii=False)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}

    # Add safety settings to prevent blocking
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"API Error: {response.status_code} - {response.text}")
            return {}
            
        try:
            result = response.json()
        except json.JSONDecodeError:
            print(f"JSON Decode Error. Response text: {response.text}")
            return {}
            
        if 'candidates' not in result or not result['candidates']:
            print(f"No candidates returned. Safety ratings: {result.get('promptFeedback', 'Unknown')}")
            return {}
            
        text = result['candidates'][0]['content']['parts'][0]['text']
        
        # Clean up code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
            
        parsed = json.loads(text)
        
        # Handle list response (convert to dict if possible)
        if isinstance(parsed, list):
            # Assuming list of objects or list of strings?
            # If list of objects with title/headline keys:
            if parsed and isinstance(parsed[0], dict) and 'headline' in parsed[0]:
                return {item.get('title', ''): item.get('headline', '') for item in parsed}
            # If just list of headlines, we can't map back easily unless order is preserved
            # Let's assume it returns a dict as requested, but if it's a list, try to map by index if length matches
            if len(parsed) == len(titles):
                return {titles[i]: parsed[i] for i in range(len(titles))}
            return {}
            
        return parsed
    except Exception as e:
        print(f"Error generating headlines: {e}")
        return {}

def main():
    print("Fetching topics without headlines for 2025-11-27...")
    
    # Fetch all topics for today to regenerate headlines
    response = supabase.table("mvp_topics") \
        .select("id, title, title_kr") \
        .eq("date", "2025-11-27") \
        .execute()
        
    topics = response.data
    print(f"Found {len(topics)} topics needing headlines.")
    
    if not topics:
        return

    # Process in batches of 10
    batch_size = 10
    for i in range(0, len(topics), batch_size):
        batch = topics[i:i+batch_size]
        titles = [t['title_kr'] or t['title'] for t in batch]
        
        print(f"Generating headlines for batch {i//batch_size + 1}...")
        headlines_map = generate_headlines_batch(titles)
        
        # Update DB
        for t in batch:
            original_title = t['title_kr'] or t['title']
            new_headline = headlines_map.get(original_title)
            
            if new_headline:
                print(f"  {original_title} -> {new_headline}")
                supabase.table("mvp_topics") \
                    .update({"headline": new_headline}) \
                    .eq("id", t['id']) \
                    .execute()
            else:
                print(f"  Failed to generate headline for: {original_title}")

    print("Done!")

if __name__ == "__main__":
    main()
