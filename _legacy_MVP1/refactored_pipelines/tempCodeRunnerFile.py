import json
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

THRESHOLDS = np.linspace(0.6, 0.9, 7)  # 필요시 조정
DATA_PATH = Path("/Users/sml/Downloads/code/MVP1/embedded_articles.json")

with open(DATA_PATH, "r") as f:
    arts = json.load(f)

# embedding 필드가 없으면 종료
if not arts or "embedding" not in arts[0]:
    raise SystemExit("embedded_articles.json에 embedding 필드가 없습니다.")

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
        rows.append({"threshold": round(thr,2), "clusters": 0, "avg_size": 0,
"multi_country_ratio": 0})
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
out_path = Path("/Users/sml/Downloads/code/MVP1/cluster_threshold_bubble.html")
fig.write_html(out_path)
print(f"Saved {out_path}")
