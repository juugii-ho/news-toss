import os
import requests
from dotenv import load_dotenv
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def list_models():
    if not GEMINI_API_KEY:
        print("No API Key")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    try:
        response = requests.get(url)
        if response.ok:
            models = response.json()
            print("Available Models:")
            for m in models.get('models', []):
                print(f"- {m['name']} ({m['supportedGenerationMethods']})")
        else:
            print(f"Error listing models: {response.status_code} {response.text}")
            
            # Try v1
            print("\nTrying v1...")
            url_v1 = f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_API_KEY}"
            response_v1 = requests.get(url_v1)
            if response_v1.ok:
                 models = response_v1.json()
                 print("Available Models (v1):")
                 for m in models.get('models', []):
                     print(f"- {m['name']}")
            else:
                 print(f"Error listing models v1: {response_v1.status_code} {response_v1.text}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    list_models()
