import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(".env.local")

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API Key found")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    print("Testing Image Generation with client.chats.create...")
    chat = client.chats.create(
        model="gemini-3-pro-image-preview",
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
        )
    )
    response = chat.send_message("Create a vibrant infographic that explains photosynthesis. Aspect Ratio 16:9.")
    
    print("Success!")
    print(f"Response type: {type(response)}")
    print(f"Response dir: {dir(response)}")
    try:
        if hasattr(response, 'candidates') and response.candidates:
            print("Found candidates.")
            for part in response.candidates[0].content.parts:
                print(f"Part dir: {dir(part)}")
                if hasattr(part, 'as_image'):
                    print("Found as_image() method.")
                    img = part.as_image()
                    if img:
                         print("Image extracted via as_image().")
                if hasattr(part, 'inline_data') and part.inline_data:
                    print("Found inline_data.")
    except Exception as e:
        print(f"Error parsing candidates: {e}")
except Exception as e:
    print(f"Failed: {e}")
