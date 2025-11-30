import os
# GRPC DNS Resolver Workaround
os.environ["GRPC_DNS_RESOLVER"] = "native"

import google.generativeai as genai
from dotenv import load_dotenv

# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", "..", "backend", ".env")
load_dotenv(env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def test_gemini():
    print("Testing Gemini API...")
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Hello, are you working?")
        print(f"Response: {response.text}")
        print("✅ Gemini API is working.")
    except Exception as e:
        print(f"❌ Gemini API Failed: {e}")

if __name__ == "__main__":
    test_gemini()
