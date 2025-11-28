import os
import json
import time
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def test_large_batch():
    print("Generating 200 dummy headlines...")
    # Mix of languages to test translation
    dummy_headlines = [
        "Trump announces new tariffs on Mexico and Canada",
        "South Korea launches Nuri rocket successfully",
        "Japan's economy shows signs of recovery",
        "Bitcoin hits $100k milestone",
        "New study reveals benefits of coffee",
    ] * 40 # 5 * 40 = 200 items
    
    print(f"Total items: {len(dummy_headlines)}")
    
    prompt = """You are a professional translator. 
Translate the following news headlines into BOTH English and Korean.
Output a JSON array of objects, where each object has "en" and "kr" keys.
Maintain the order exactly.

Example Output:
[
  {"en": "Headline in English", "kr": "한국어 헤드라인"},
  ...
]

Headlines:
"""
    # Add numbered list to help model keep track (optional, but good for alignment)
    for i, text in enumerate(dummy_headlines):
        prompt += f"{i+1}. {text}\n"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json" # Force JSON mode
        }
    }

    print("Sending request to Gemini (Batch 200, Combined EN/KR)...")
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=300) # 5 min timeout
        response.raise_for_status()
        
        duration = time.time() - start_time
        print(f"Request finished in {duration:.2f} seconds.")
        
        result = response.json()
        content = result['candidates'][0]['content']['parts'][0]['text']
        
        # Parse JSON
        parsed = json.loads(content)
        print(f"Successfully parsed JSON. Items: {len(parsed)}")
        
        if len(parsed) == 200:
            print("SUCCESS: Count matches exactly!")
            print("Sample 0:", parsed[0])
            print("Sample 199:", parsed[-1])
        else:
            print(f"WARNING: Count mismatch. Expected 200, got {len(parsed)}")
            
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_large_batch()
