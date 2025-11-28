import os
import time
import requests
from dotenv import load_dotenv
from pathlib import Path
from supabase import create_client
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def batch_embed_contents(texts, model="models/text-embedding-004", retries=3):
    """
    Embeds a list of texts using Gemini API batchEmbedContents.
    """
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found.")
        return [None] * len(texts)

    url = f"https://generativelanguage.googleapis.com/v1beta/{model}:batchEmbedContents?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # Prepare requests
    requests_payload = [
        {
            "model": model,
            "content": {"parts": [{"text": text}]}
        }
        for text in texts
    ]
    
    data = {"requests": requests_payload}

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Extract embeddings
            embeddings = []
            if 'embeddings' in result:
                for item in result['embeddings']:
                    embeddings.append(item['values'])
            return embeddings
            
        except Exception as e:
            print(f"Error getting batch embeddings (Attempt {attempt+1}): {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                return [None] * len(texts)

def process_batch_db(articles):
    """
    Process a batch of articles: generate embeddings and update DB.
    """
    texts = []
    for article in articles:
        # Use English title for embedding
        text_to_embed = article.get('title_en', article['title'])
        # Add summary if available
        summary = article.get('summary', '')
        text = f"{text_to_embed} {summary}"
        text = text[:1000] # Truncate to avoid token limits
        texts.append(text)
        
    embeddings = batch_embed_contents(texts)
    
    # Update DB
    for i, embedding in enumerate(embeddings):
        if embedding:
            art_id = articles[i]['id']
            try:
                # Debug info
                # print(f"Updating article {art_id} with embedding of length {len(embedding)}")
                supabase.table("mvp_articles").update({'embedding': embedding}).eq('id', art_id).execute()
            except Exception as e:
                print(f"Error updating embedding for {art_id}: {e}")
                import traceback
                traceback.print_exc()

def embed_articles_db():
    print("Fetching articles needing embedding from Supabase...")
    
    BATCH_SIZE = 100
    
    while True:
        # Fetch articles where embedding is NULL AND title_en is NOT NULL
        # (We need English title to embed effectively)
        response = supabase.table("mvp_articles") \
            .select("id, title, title_en, summary") \
            .is_("embedding", "null") \
            .not_.is_("title_en", "null") \
            .limit(BATCH_SIZE) \
            .execute()
            
        articles = response.data
        
        if not articles:
            print("No more articles needing embedding (or waiting for translation).")
            break
            
        print(f"Processing batch of {len(articles)} articles for embedding...")
        
        # Process in parallel (sub-batches of 10?)
        # Actually, since we are updating DB one by one or in small batches, 
        # let's just use the main thread or a simple executor for the batch API calls.
        # The batch API takes up to 100 requests.
        
        process_batch_db(articles)
        
        time.sleep(1)

if __name__ == "__main__":
    embed_articles_db()
