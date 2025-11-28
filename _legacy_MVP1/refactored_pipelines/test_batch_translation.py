import os
import requests
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env.local')
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def batch_translate_to_korean(texts):
    print(f"Testing with Key: {GEMINI_API_KEY[:5]}...")
    
    texts_numbered = "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts)])
    prompt = f"""Translate the following news headlines into natural Korean.
Output ONLY the translated lines corresponding to the numbers. Do not add explanations.

Originals:
{texts_numbered}

Format:
1. [Translation 1]
2. [Translation 2]
...
"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        print("Sending request...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.ok:
            result = response.json()
            # print(json.dumps(result, indent=2))
            if 'candidates' in result and result['candidates']:
                content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                print("Raw Content:\n", content)
                
                translations = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        cleaned = line.split('.', 1)[-1].strip() if '.' in line else line.strip('- ')
                        translations.append(cleaned)
                
                return translations
        else:
            print("Error Response:", response.text)
    except Exception as e:
        print(f"Exception: {e}")
        
    return []

if __name__ == "__main__":
    titles = [
        "Trump says he will visit China in April after call with Xi",
        "Judge dismisses cases against ex-FBI director Comey",
        "Pentagon to review Senator Mark Kelly misconduct allegations"
    ]
    
    results = batch_translate_to_korean(titles)
    print("\nResults:")
    for i, r in enumerate(results):
        print(f"{i+1}. {r}")
