import os
import json
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
root_dir = Path(__file__).resolve().parent
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found. Please check .env.local")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

THRESHOLDS = np.linspace(0.6, 0.9, 7)  # 필요시 조정

def fetch_articles_with_embeddings():
    print("Fetching articles with embeddings from Supabase...")
    all_articles = []
    offset = 0
    BATCH_SIZE = 1000
    
    while True:
        response = supabase.table("mvp_articles") \
            .select("country_code, embedding") \
            .not_.is_("embedding", "null") \
            .range(offset, offset + BATCH_SIZE - 1) \
            .execute()
            
        batch = response.data
        if not batch:
            break
            
        for art in batch:
            if isinstance(art['embedding'], str):
                art['embedding'] = json.loads(art['embedding'])
                
        all_articles.extend(batch)
        offset += BATCH_SIZE
        print(f"Fetched {len(all_articles)} articles...")
        
    return all_articles

def main():
    arts = fetch_articles_with_embeddings()

    if not arts:
        print("No articles found in Supabase.")
        exit(0)

    emb = np.array([a["embedding"] for a in arts])
    sim = cosine_similarity(emb)

    def cluster_by_threshold(sim, thr):
        n = sim.shape[0]
        parent = list(range(n))
        def find(x):
            while parent[x]!=x:
                parent[x]=parent[parent[x]]
                x=parent[x]
            return x
        def union(a,b):
            ra, rb = find(a), find(b)
            if ra!=rb: parent[rb]=ra
        for i in range(n):
            for j in range(i+1,n):
                if sim[i,j] >= thr:
                    union(i,j)
        comps = {}
        for i in range(n):
            r = find(i)
            comps.setdefault(r, []).append(i)
        return list(comps.values())

    rows=[]
    for thr in THRESHOLDS:
        clusters = cluster_by_threshold(sim, thr)
        if not clusters:
            rows.append({"threshold": round(thr,2), "clusters": 0, "avg_size": 0, "multi_country_ratio": 0})
            continue
        sizes = [len(c) for c in clusters]
        multi = 0
        for c in clusters:
            cc = {arts[i].get("country_code","") for i in c}
            if len(cc) >= 3:
                multi += 1
        rows.append({
            "threshold": round(thr,2),
            "clusters": len(clusters),
            "avg_size": float(np.mean(sizes)),
            "multi_country_ratio": multi/len(clusters)
        })

    df = pd.DataFrame(rows)
    fig = px.scatter(
        df, x="threshold", y="clusters",
        size="avg_size", color="multi_country_ratio",
        title="Threshold vs Clusters (size=avg_size, color=multi_country_ratio)",
        labels={"multi_country_ratio":"≥3-country ratio"}
    )
    out_path = root_dir / "cluster_threshold_bubble.html"
    fig.write_html(out_path)
    print(f"Saved {out_path}")

if __name__ == "__main__":
    main()
