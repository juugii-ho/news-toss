import os
import random
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
from google.genai import types
from sklearn.manifold import TSNE
import plotly.express as px

# 1. Setup
load_dotenv('.env')
load_dotenv('backend/.env')
load_dotenv('.env.local')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not GOOGLE_API_KEY:
    print("Error: Missing environment variables.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = genai.Client(api_key=GOOGLE_API_KEY)

def get_articles_per_country(limit=10):
    print("Fetching articles...", flush=True)
    # Get all distinct countries first (manual list or query)
    # For MVP, let's assume a set of known countries or fetch distinct
    # Supabase doesn't support distinct easily on client, so I'll fetch a large batch of metadata
    
    # Alternative: Iterate known countries
    countries = ['KR', 'US', 'JP', 'CN', 'FR', 'GB', 'DE', 'ES', 'IT', 'IN', 'RU', 'UA', 'IL', 'PS'] # Common ones
    
    all_articles = []
    
    for country in countries:
        print(f"  Fetching for {country}...", flush=True)
        try:
            # Fetch 200 latest to sample from
            res = supabase.table("mvp2_articles") \
                .select("id, title_original, title_en, country_code") \
                .eq("country_code", country) \
                .order("published_at", desc=True) \
                .limit(200) \
                .execute()
            
            data = res.data
            if not data:
                continue
                
            # Random sample 100
            if len(data) > limit:
                sampled = random.sample(data, limit)
            else:
                sampled = data
                
            all_articles.extend(sampled)
        except Exception as e:
            print(f"    Error fetching {country}: {e}")
            
    print(f"Total articles fetched: {len(all_articles)}", flush=True)
    return all_articles

def generate_embeddings(articles):
    print("Generating embeddings...", flush=True)
    embeddings = []
    valid_articles = []
    
    # Batch process? The SDK supports batch? 
    # client.models.embed_content supports single.
    # We can loop. It's only ~1000 articles.
    
    consecutive_errors = 0
    for i, art in enumerate(articles):
        text = art.get('title_en') or art.get('title_original')
        if not text:
            continue
            
        try:
            # Use text-embedding-004
            response = client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
            embedding = response.embeddings[0].values
            embeddings.append(embedding)
            valid_articles.append(art)
            
            if i % 10 == 0:
                print(f"  Processed {i}/{len(articles)}", flush=True)
            consecutive_errors = 0
                
        except Exception as e:
            print(f"  Error embedding {art['id']}: {e}", flush=True)
            consecutive_errors += 1
            if consecutive_errors > 5:
                print("Too many consecutive errors. Stopping.", flush=True)
                break
            
    return valid_articles, embeddings

def visualize(articles, embeddings):
    print("Reducing dimensions and plotting...")
    if not embeddings:
        print("No embeddings to visualize.")
        return

    # t-SNE
    embeddings_array = np.array(embeddings)
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(articles)-1))
    projections = tsne.fit_transform(embeddings_array)
    
    df = pd.DataFrame({
        'x': projections[:, 0],
        'y': projections[:, 1],
        'title': [a.get('title_original') for a in articles],
        'country': [a.get('country_code') for a in articles]
    })
    
    fig = px.scatter(
        df, 
        x='x', 
        y='y', 
        color='country', 
        hover_data=['title'],
        title='Article Embeddings Map (100 Random Samples per Country)',
        template='plotly_dark'
    )
    
    output_path = "outputs/article_map.html"
    os.makedirs("outputs", exist_ok=True)
    fig.write_html(output_path)
    print(f"✅ Visualization saved to {output_path}")

def main():
    articles = get_articles_per_country(limit=100)
    if not articles:
        print("No articles found.")
        return
        
    valid_articles, embeddings = generate_embeddings(articles)
    visualize(valid_articles, embeddings)

if __name__ == "__main__":
    main()
