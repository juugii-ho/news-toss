import os
import requests
from dotenv import load_dotenv
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def test_rest():
    if not GEMINI_API_KEY:
        print("No API Key")
        return

    models = ["gemini-1.0-pro", "gemini-1.5-flash-latest", "gemini-1.5-flash-001"]
    versions = ["v1beta", "v1"]

    for model in models:
        for version in versions:
            url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={GEMINI_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{"parts": [{"text": "Hello"}]}]
            }
            
            print(f"Testing {model} on {version}...")
            try:
                response = requests.post(url, headers=headers, json=data, timeout=5)
                print(f"Status: {response.status_code}")
                if response.ok:
                    print("Success!")
                else:
                    print(f"Error: {response.text[:100]}...")
            except Exception as e:
                print(f"Exception: {e}")
            print("-" * 20)

if __name__ == "__main__":
    test_rest()
