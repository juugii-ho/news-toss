import os
import io
import time
import difflib
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
from google.genai import types
from PIL import Image

# ... (rest of imports)

def find_similar_thumbnail(target_topic, existing_topics):
    """
    Finds a topic with a similar title that already has a thumbnail.
    Returns the thumbnail_url if found, else None.
    """
    if not existing_topics:
        return None
        
    target_title = target_topic['topic_name']
    best_ratio = 0.0
    best_url = None
    
    for et in existing_topics:
        # Skip self (though unlikely as we filter by null thumbnail)
        if et['id'] == target_topic['id']:
            continue
            
        ratio = difflib.SequenceMatcher(None, target_title, et['topic_name']).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_url = et['thumbnail_url']
            
    # Threshold for similarity (e.g., 80% match)
    if best_ratio > 0.8:
        return best_url
    return None

# Load environment variables
load_dotenv('backend/.env')
load_dotenv('.env.local')
load_dotenv('.env')

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

    # Post-processing replacements (from user snippet)
    final_prompt = final_prompt.replace('李', '이')
    final_prompt = final_prompt.replace('이 대통령', '이재명 대통령') # Context-specific, maybe risky to generalize but user had it.
    # I will keep it as user requested "using my code".
    final_prompt = f"{country}의 '{topic_name}' 주제로 {sentence} 내용이 담긴 언론사진 느낌의 썸네일. **주의사항** : 1. 글자 사용 금지"

    
    return final_prompt

def generate_and_upload_image(topic_id, prompt):
    print(f"  🎨 Generating image for topic {topic_id}...")
    
    # Append aspect ratio to prompt since config doesn't support it for this model
    prompt += " Aspect Ratio 16:9."

    try:
        chat = client.chats.create(
            model="gemini-3-pro-image-preview",
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
            )
        )
        response = chat.send_message(prompt)
        
        image_bytes = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    break
                
        if not image_bytes:
            print("    ❌ No image generated.")
            return False

        # Convert to WebP
        try:
            image = Image.open(io.BytesIO(img_bytes))
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
            # Check if bucket exists? No, just try upload.
            # upsert=True to overwrite
            res = supabase.storage.from_("thumbnails").upload(
                path=file_path,
                file=webp_bytes,
                file_options={"content-type": "image/webp", "upsert": "true"}
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
        
        # Fetch topics WITH thumbnails for comparison
        res_existing = supabase.table("mvp2_topics") \
            .select("id, topic_name, thumbnail_url") \
            .not_.is_("thumbnail_url", "null") \
            .execute()
        topics_with_thumbnails = res_existing.data
        print(f"Found {len(topics_with_thumbnails)} existing thumbnails for reuse check.")
        
        for topic in topics:
            print(f"\nProcessing: {topic['topic_name']}")
            
            # 1. Get Article Titles
            stances = topic.get('stances', {})
            all_ids = stances.get('factual', []) + stances.get('critical', []) + stances.get('supportive', [])
            article_map = fetch_article_titles(all_ids)
            
            # 2. Check for Similar Topic (Reuse Thumbnail)
            similar_url = find_similar_thumbnail(topic, topics_with_thumbnails)
            if similar_url:
                print(f"    ♻️ Found similar topic! Reusing thumbnail.")
                supabase.table("mvp2_topics").update({"thumbnail_url": similar_url}).eq("id", topic['id']).execute()
                continue

            # 3. Generate Prompt
            prompt = generate_thumbnail_prompt(topic, article_map)
            if not prompt:
                print("    ⚠️ Could not generate prompt (no articles?).")
                continue
                
            print(f"    📝 Prompt: {prompt[:100]}...")
            
            # 4. Generate & Upload
            generate_and_upload_image(topic['id'], prompt)
            
            time.sleep(2) # Rate limit
            
    except Exception as e:
        print(f"❌ Error in main loop: {e}")

if __name__ == "__main__":
    main()
