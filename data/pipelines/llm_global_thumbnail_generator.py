import os
import io
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
from google.genai import types
from PIL import Image

# Load environment variables
load_dotenv('backend/.env')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Use Service Role if available, else Anon
KEY_TO_USE = SUPABASE_SERVICE_ROLE_KEY if SUPABASE_SERVICE_ROLE_KEY else SUPABASE_KEY

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not KEY_TO_USE or not GOOGLE_API_KEY:
    print("Error: Environment variables missing.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, KEY_TO_USE)
client = genai.Client(api_key=GOOGLE_API_KEY)

def fetch_local_topics(local_topic_ids):
    """Fetch local topics linked to this global topic"""
    if not local_topic_ids or len(local_topic_ids) == 0:
        return []
    try:
        # Get local topics
        topics_response = supabase.table("mvp2_topics").select("topic_name, country_code").in_("id", local_topic_ids).execute()
        return topics_response.data
    except Exception as e:
        print(f"  ⚠️ Error fetching local topics: {e}")
        return []

def generate_thumbnail_prompt(topic, local_topics):
    topic_name = topic.get('title_ko') or topic.get('topic_name') or topic.get('title_en')
    
    if not local_topics or len(local_topics) == 0:
        return None
    
    # Get country codes
    countries = list(set([lt.get('country_code') for lt in local_topics if lt.get('country_code')]))
    country_str = ", ".join(countries[:3])  # Use up to 3 countries
    
    # Get topic names
    topic_names = [lt.get('topic_name') for lt in local_topics if lt.get('topic_name')]
    selected_topics = topic_names[:3]  # Use up to 3 topics
    
    quoted_topics = [f"'{t}'" for t in selected_topics]
    sentence = "과 ".join(quoted_topics)
    
    final_prompt = f"{country_str} 국가들의 '{topic_name}' 글로벌 주제로 {sentence} 내용이 담긴 언론사진 느낌의 썸네일. **주의사항** : 1. 글자 사용 금지"
    
    return final_prompt

def generate_and_upload_image(topic_id, prompt):
    print(f"  🎨 Generating image for global topic {topic_id}...")
    try:
        # Use chat create pattern for gemini-3-pro-image-preview
        chat = client.chats.create(
            model="gemini-3-pro-image-preview",
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
            )
        )
        
        # Append Aspect Ratio to prompt as config might not support it directly in this SDK version for this model
        full_prompt = prompt + " Aspect Ratio 16:9."
        
        response = chat.send_message(full_prompt)
        
        image_bytes = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    break
                
        if not image_bytes:
            print("    ❌ No image generated (no inline_data found).")
            return False

        # Convert to WebP
        try:
            image = Image.open(io.BytesIO(image_bytes))
            webp_io = io.BytesIO()
            image.save(webp_io, format="WEBP", quality=80)
            webp_bytes = webp_io.getvalue()
        except Exception as e:
            print(f"    ❌ WebP Conversion Failed: {e}")
            return False

        # Upload to Supabase Storage
        file_path = f"thumbnails/{topic_id}.webp"
        print(f"    📤 Uploading to {file_path}...")
        
        try:
            res = supabase.storage.from_("thumbnails").upload(
                path=file_path,
                file=webp_bytes,
                file_options={"content-type": "image/webp", "upsert": "true"}
            )
            
            # Get Public URL
            public_url = supabase.storage.from_("thumbnails").get_public_url(file_path)
            
            # Update Global Topic (Megatopic)
            supabase.table("mvp2_megatopics").update({"thumbnail_url": public_url}).eq("id", topic_id).execute()
            print(f"    ✅ Saved URL: {public_url}")
            return True
            
        except Exception as e:
            print(f"    ❌ Storage Upload Failed: {e}")
            return False

    except Exception as e:
        print(f"    ❌ Image Generation Failed: {e}")
        return False

def main():
    print("🚀 Starting Global Thumbnail Generator...")
    
    # Fetch recent global topics without thumbnail
    time_threshold = (datetime.utcnow() - timedelta(days=7)).isoformat()
    
    try:
        response = supabase.table("mvp2_megatopics") \
            .select("*") \
            .is_("thumbnail_url", "null") \
            .gte("created_at", time_threshold) \
            .order("country_count", desc=True) \
            .execute()
            
        topics = response.data
        print(f"Found {len(topics)} global topics needing thumbnails.")
        
        for topic in topics:
            topic_name = topic.get('title_ko') or topic.get('topic_name') or topic.get('title_en')
            print(f"\nProcessing: {topic_name}")
            
            # 1. Get Local Topics
            local_topics = fetch_local_topics(topic.get('topic_ids', []))
            
            # 2. Generate Prompt
            prompt = generate_thumbnail_prompt(topic, local_topics)
            if not prompt:
                print("    ⚠️ Could not generate prompt (no local topics?).")
                continue
                
            print(f"    📝 Prompt: {prompt[:100]}...")
            
            # 3. Generate & Upload
            generate_and_upload_image(topic['id'], prompt)
            
            time.sleep(2)  # Rate limit
            
    except Exception as e:
        print(f"❌ Error in main loop: {e}")

if __name__ == "__main__":
    main()
