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
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") # Service Role Key preferred for Storage Upload if RLS is on
# But user provided ANON KEY in previous scripts. 
# If Storage requires authentication, we might need Service Role Key.
# I will check if SUPABASE_SERVICE_ROLE_KEY is available.
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Use Service Role if available, else Anon
KEY_TO_USE = SUPABASE_SERVICE_ROLE_KEY if SUPABASE_SERVICE_ROLE_KEY else SUPABASE_KEY

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not KEY_TO_USE or not GOOGLE_API_KEY:
    print("Error: Environment variables missing.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, KEY_TO_USE)
client = genai.Client(api_key=GOOGLE_API_KEY)

def fetch_article_titles(article_ids):
    if not article_ids: return {}
    try:
        response = supabase.table("mvp2_articles").select("id, title_ko, title_en").in_("id", article_ids).execute()
        return {row['id']: (row.get('title_ko') or row.get('title_en')) for row in response.data}
    except Exception as e:
        print(f"  ⚠️ Error fetching articles: {e}")
        return {}

def generate_thumbnail_prompt(topic, article_map):
    country = topic['country_code']
    topic_name = topic['topic_name']
    stances = topic.get('stances', {})
    
    # Flatten articles with sentiment
    articles_list = []
    for sentiment in ['factual', 'critical', 'supportive']:
        ids = stances.get(sentiment, [])
        for aid in ids:
            title = article_map.get(aid)
            if title:
                articles_list.append({'sentiment': sentiment, 'title': title})
                
    total_count = len(articles_list)
    if total_count == 0:
        return None

    # Group by sentiment
    sentiment_groups = {}
    for art in articles_list:
        sent = art['sentiment']
        if sent not in sentiment_groups:
            sentiment_groups[sent] = []
        sentiment_groups[sent].append(art['title'])

    selected_titles = []
    dominant_found = False

    # 50% Rule
    for sentiment, titles in sentiment_groups.items():
        ratio = len(titles) / total_count
        if ratio > 0.5:
            selected_titles = titles[:3]
            dominant_found = True
            break
            
    if not dominant_found:
        for sentiment, titles in sentiment_groups.items():
            if titles:
                selected_titles.append(titles[0])

    quoted_titles = [f"'{t}'" for t in selected_titles]
    sentence = "과 ".join(quoted_titles)

    final_prompt = f"{country}의 '{topic_name}' 주제로 {sentence} 내용이 담긴 언론사진 느낌의 한국어 썸네일. **주의사항** : 1.마침표 사용 금지, 2. 같은 문장 재사용 절대 금지 3.하단에 'AI로 생성된 이미지'라는 문구 삽입 "
    
    # Post-processing replacements (from user snippet)
    final_prompt = final_prompt.replace('李', '이')
    final_prompt = final_prompt.replace('이 대통령', '이재명 대통령') # Context-specific, maybe risky to generalize but user had it.
    # I will keep it as user requested "using my code".
    
    return final_prompt

def generate_and_upload_image(topic_id, prompt):
    print(f"  🎨 Generating image for topic {topic_id}...")
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview", # Use the preview model as requested
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['Image'],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                )
            )
        )
        
        image = None
        for part in response.parts:
            if part.as_image():
                image = part.as_image()
                break
                
        if not image:
            print("    ❌ No image generated.")
            return False

        print(f"    DEBUG: Image type: {type(image)}")
        print(f"    DEBUG: Image attributes: {dir(image)}")
        # Save to temp file
        temp_filename = f"/tmp/temp_{topic_id}.png"
        try:
            image.save(temp_filename)
            
            # Read bytes
            with open(temp_filename, "rb") as f:
                img_bytes = f.read()
                
            # Clean up
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
        except Exception as e:
            print(f"    ❌ Error saving/reading temp file: {e}")
            return False

        # Upload to Supabase Storage
        file_path = f"thumbnails/{topic_id}.png"
        print(f"    📤 Uploading to {file_path}...")
        
        try:
            # Check if bucket exists? No, just try upload.
            # upsert=True to overwrite
            res = supabase.storage.from_("thumbnails").upload(
                path=file_path,
                file=img_bytes,
                file_options={"content-type": "image/png", "upsert": "true"}
            )
            
            # Get Public URL
            # Assuming bucket is public
            public_url = supabase.storage.from_("thumbnails").get_public_url(file_path)
            
            # Update Topic
            supabase.table("mvp2_topics").update({"thumbnail_url": public_url}).eq("id", topic_id).execute()
            print(f"    ✅ Saved URL: {public_url}")
            return True
            
        except Exception as e:
            print(f"    ❌ Storage Upload Failed: {e}")
            return False

    except Exception as e:
        print(f"    ❌ Image Generation Failed: {e}")
        return False

def main():
    print("🚀 Starting Thumbnail Generator...")
    
    # Fetch recent topics without thumbnail
    time_threshold = (datetime.utcnow() - timedelta(days=7)).isoformat()  # Last 7 days
    
    try:
        response = supabase.table("mvp2_topics") \
            .select("*") \
            .is_("thumbnail_url", "null") \
            .gte("created_at", time_threshold) \
            .order("article_count", desc=True) \
            .execute()  # Process all topics
            
        topics = response.data
        print(f"Found {len(topics)} topics needing thumbnails.")
        
        for topic in topics:
            print(f"\nProcessing: {topic['topic_name']}")
            
            # 1. Get Article Titles
            stances = topic.get('stances', {})
            all_ids = stances.get('factual', []) + stances.get('critical', []) + stances.get('supportive', [])
            article_map = fetch_article_titles(all_ids)
            
            # 2. Generate Prompt
            prompt = generate_thumbnail_prompt(topic, article_map)
            if not prompt:
                print("    ⚠️ Could not generate prompt (no articles?).")
                continue
                
            print(f"    📝 Prompt: {prompt[:100]}...")
            
            # 3. Generate & Upload
            generate_and_upload_image(topic['id'], prompt)
            
            time.sleep(2) # Rate limit
            
    except Exception as e:
        print(f"❌ Error in main loop: {e}")

if __name__ == "__main__":
    main()
