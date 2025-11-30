import os
# GRPC DNS Resolver Workaround
os.environ["GRPC_DNS_RESOLVER"] = "native"

import json
import numpy as np
from supabase import create_client, Client
from dotenv import load_dotenv
from sklearn.manifold import MDS
from sklearn.preprocessing import MinMaxScaler
import google.generativeai as genai

# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", "..", "backend", ".env")
load_dotenv(env_path)

url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

# Gemini Setup (for embeddings)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_embeddings(text_list):
    if not text_list:
        return []
    # Batch processing
    batch_size = 100
    all_embeddings = []
    for i in range(0, len(text_list), batch_size):
        batch = text_list[i:i+batch_size]
        try:
            print(f"    Getting embeddings for batch {i//batch_size + 1}...")
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=batch,
                task_type="clustering",
            )
            emb = result['embedding']
            print(f"    Got {len(emb)} embeddings. First vec sample: {emb[0][:3]}...")
            all_embeddings.extend(emb)
        except Exception as e:
            print(f"    ⚠️ Error embedding batch: {e}")
            # Fallback: zero vectors
            all_embeddings.extend([[0]*768 for _ in range(len(batch))])
    return all_embeddings

def main():
    print("🚀 Calculating Constellation Coordinates...")
    
    # 1. Fetch Megatopics
    response = supabase.table("mvp2_megatopics").select("*").execute()
    megatopics = response.data
    
    if not megatopics:
        print("No megatopics found.")
        return

    print(f"Found {len(megatopics)} megatopics.")
    
    # 2. Embed Megatopics
    mega_titles = [m['name'] for m in megatopics]
    mega_embeddings = get_embeddings(mega_titles)
    
    # 3. Calculate Megatopic Coordinates (MDS for global layout)
    # Use MDS to project 768-dim to 2-dim preserving distances
    mds = MDS(n_components=2, random_state=42, dissimilarity='euclidean')
    mega_coords = mds.fit_transform(mega_embeddings)
    
    # Normalize to range [-100, 100] for easier visualization
    scaler = MinMaxScaler(feature_range=(-80, 80)) # Leave some margin
    mega_coords_scaled = scaler.fit_transform(mega_coords)
    
    # 4. Update Megatopics in DB
    for i, m in enumerate(megatopics):
        mx, my = mega_coords_scaled[i]
        supabase.table("mvp2_megatopics").update({"x": mx, "y": my}).eq("id", m['id']).execute()
        print(f"  Updated Megatopic: {m['name']} -> ({mx:.2f}, {my:.2f})")
        
        # 5. Process Local Topics (Satellites)
        topic_ids = m['topic_ids']
        if not topic_ids:
            continue
            
        # Fetch local topics
        # Note: We don't need embeddings for local topics relative to megatopic, 
        # just random distribution around the center is enough for MVP.
        # Or we can use force-directed layout if we want them to cluster by country.
        # For now, let's use a simple "Orbit" layout.
        
        # Fetch local topic data to check countries (optional, for sorting)
        # local_topics = supabase.table("mvp2_topics").select("*").in_("id", topic_ids).execute().data
        
        num_locals = len(topic_ids)
        radius = 15.0 # Radius of the orbit
        
        for j, tid in enumerate(topic_ids):
            # Distribute evenly in a circle (or random)
            # Adding some randomness to make it look natural
            angle = (2 * np.pi * j) / num_locals
            noise_r = np.random.uniform(-2, 2)
            noise_a = np.random.uniform(-0.1, 0.1)
            
            lx = mx + (radius + noise_r) * np.cos(angle + noise_a)
            ly = my + (radius + noise_r) * np.sin(angle + noise_a)
            
            supabase.table("mvp2_topics").update({"x": lx, "y": ly}).eq("id", tid).execute()
            # print(f"    Updated Local Topic: {tid} -> ({lx:.2f}, {ly:.2f})")
            
    print("✅ Coordinates calculation complete.")

if __name__ == "__main__":
    main()
