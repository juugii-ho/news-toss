import google.generativeai as genai
import socket

# .env 로드 코드를 제거합니다.
# from dotenv import load_dotenv # 제거
# import os # 제거
# GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY') # 제거

# ✅ 실제 사용하신 유효한 API 키 문자열로 대체하여 테스트합니다.
MY_API_KEY = 'AIzaSyAIAU-70ZKQ1eSytD92DBtm8lNN3cKs4js' # 실제 키로 변경 필요

genai.configure(api_key=MY_API_KEY)

print('Testing Gemini API with timeout...')
model = genai.GenerativeModel(
    'gemini-2.5-flash', # 모델명 확인 완료
    generation_config={'temperature': 0.2},
)

socket.setdefaulttimeout(10)

try:
    print('Calling API...')
    response = model.generate_content('Say hello', request_options={'timeout': 10})
    print(f'✅ Success: {response.text}')
except Exception as e:
    print(f'❌ Error Type: {type(e).__name__}')
    print(f'❌ Error Message: {str(e)}')
    import traceback
    traceback.print_exc()