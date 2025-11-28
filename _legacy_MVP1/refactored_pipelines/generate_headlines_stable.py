import os
import json
import time
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
    1. Tone: Casual and friendly, BUT informative.
    2. Style: Use short summaries.
    3. Prohibition 1: NEVER end with a noun (e.g., "논란", "개최", "발표"). Always use a complete sentence.
    4. Prohibition 2: NO CLICKBAIT. Do not exaggerate. Stick to the facts.
    5. Prohibition 3: NO VAGUE QUESTIONS. Do NOT use "무슨 일이야?", "알아볼까?", "궁금해?", "어떤 상황일까?".
    6. Prohibition 4: NO FILLER PHRASES. Do NOT use "지금 이렇대요", "여기 다 있어요", "알려드릴게요", "모았어요", "만나봐요". These sound fake.
    7. Fallback: If the input is vague (e.g., "Sports News"), just translate it naturally or say "주요 소식을 정리했어요."
    8. Length: Keep it short (under 45 chars).
    9. Language: Korean.
    10. Emojis: Allowed if relevant (use sparingly).
    11. Output: ONLY the list of headlines. NO introductory text. NO numbering.

    Examples:
    - Input: "‘최악의 참사’ 홍콩 아파트 화재, 피해 키운 원인은 ‘대나무 비계’였다?"
    - Output: "홍콩 아파트 화재, ‘최악의 참사’가 된 이유"

    - Input: "Sports results and analysis"
    - Output: "스포츠 경기 결과와 분석을 정리했어요." (O)
    - Output: "스포츠 소식, 여기 다 있어요!" (X - Filler)

    - Input: "Social issues in UK"
    - Output: "영국의 주요 사회 이슈들을 모았어요." (O)
    - Output: "영국 사회 문제, 지금 이렇대요!" (X - Filler)

    - Input: "“내 집에 누가 사는지 알고 싶어!” ‘임차인 면접 제도’가 뜨거운 감자로 떠오른 이유"
    - Output: "전셋집 구하고 싶으면 면접부터 보라고요? 🏠"

    - Input: "사상 최고 실적 기록한 엔비디아, ‘AI 거품론’에 “엔비디아는 다르다?”"
    - Output: "“AI? 거품 맞아. 언빌리버블.” 엔비디아 사상 최고 실적!"

    - Input: "제2의 닷컴버블? AI 버블론 반복되는 이유와 ‘순환거래’ 논란 분석"
    - Output: "제2의 닷컴버블? AI 거품론과 ‘순환거래’ 논란"

    - Input: "누리호 4차 발사 성공, 민간 기업이 이끄는 ‘뉴 스페이스’ 시대 첫걸음 뗀 거라고?"
    - Output: "대한민국은 누리호 타고 ‘뉴 스페이스’ 시대로 갑니다 🚀"

    - Input: "감사원 윤석열 정부 의대 증원 감사 결과: “근거도 절차도 부족했어!”"
    - Output: "윤석열 정부 의대 증원, 근거도 부족한데 밀어붙였다고?"

    - Input: "1050원짜리 ‘초코파이 절도’ 사건, 항소심이 ‘무죄’ 선고한 이유"
    - Output: "‘초코파이 절도’ 사건의 결말: “무죄를 선고합니다.”"

    Input Titles:
    """ + json.dumps(titles, ensure_ascii=False)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    for attempt in range(3):
        try:
            # Increased timeout to 300s as requested by user
            response = requests.post(url, headers=headers, json=data, timeout=300)
            
            if response.status_code != 200:
                print(f"API Error ({attempt+1}/3): {response.status_code} - {response.text}")
                if response.status_code == 429:
                    time.sleep(30)
                else:
                    time.sleep(5)
                continue
                
            try:
                result = response.json()
            except Exception as e:
                print(f"JSON Parse Error ({attempt+1}/3): {e}")
                print(f"Response Status: {response.status_code}")
                # Print first 1000 chars to see what's wrong
                print(f"Response Text: {response.text[:1000]}")
                time.sleep(5)
                continue

            if 'candidates' not in result or not result['candidates']:
                print(f"No candidates ({attempt+1}/3). Feedback: {result.get('promptFeedback', 'None')}")
                time.sleep(5)
                continue
                
            text = result['candidates'][0]['content']['parts'][0]['text'].strip()
            # Clean up markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
                
            try:
                parsed = json.loads(text)
            except Exception:
                # Fallback: Parse line by line if not JSON
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                parsed = []
                for line in lines:
                    # Skip intro lines
                    if line.endswith(':') or "Here are" in line or "Sure" in line or "다음은" in line:
                        continue
                        
                    # Remove leading numbers (e.g., "1. ", "2. ")
                    if line[0].isdigit():
                        parts = line.split('.', 1)
                        if len(parts) > 1:
                            line = parts[1].strip()
                    parsed.append(line)
            
            # Handle list response (JSON list or parsed lines)
            if isinstance(parsed, list):
                # If we have more items than titles, maybe first line is still intro?
                if len(parsed) > len(titles):
                    parsed = parsed[-len(titles):]
                    
                if len(parsed) == len(titles):
                    return {titles[i]: parsed[i] for i in range(len(titles))}
                # If lengths don't match, try to map as many as possible
                min_len = min(len(parsed), len(titles))
                return {titles[i]: parsed[i] for i in range(min_len)}
                
                # Try to match by key if list of dicts
                if parsed and isinstance(parsed[0], dict) and 'headline' in parsed[0]:
                    return {item.get('title', ''): item.get('headline', '') for item in parsed}
            
            return parsed
            
        except Exception as e:
            print(f"Error ({attempt+1}/3): {e}")
            time.sleep(5)
            
    return {}

def main():
    print("Fetching topics for 2025-11-27...")
    
    response = supabase.table("mvp_topics") \
        .select("id, title, title_kr") \
        .eq("date", "2025-11-27") \
        .execute()
        
    topics = response.data
    print(f"Found {len(topics)} topics.")
    
    # Process in batches of 50
    batch_size = 50
    for i in range(0, len(topics), batch_size):
        batch = topics[i:i+batch_size]
        titles = [t['title_kr'] or t['title'] for t in batch]
        
        print(f"[{i+1}/{len(topics)}] Generating batch of {len(batch)}...")
        
        headlines_map = generate_headlines_batch(titles)
        
        if headlines_map:
            for t in batch:
                original_title = t['title_kr'] or t['title']
                new_headline = headlines_map.get(original_title)
                
                if new_headline:
                    # print(f"  {original_title[:20]}... -> {new_headline}")
                    supabase.table("mvp_topics") \
                        .update({"headline": new_headline}) \
                        .eq("id", t['id']) \
                        .execute()
            print(f"  Batch {i//batch_size + 1} completed.")
        else:
            print("  Batch failed.")
            
        # Rate limit friendly
        time.sleep(2)

if __name__ == "__main__":
    main()
