import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from pathlib import Path
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch articles with embeddings from Supabase
print("Fetching articles with embeddings from Supabase...")

all_articles = []
offset = 0
BATCH_SIZE = 1000

while True:
    response = supabase.table("mvp_articles") \
        .select("country_code, embedding, title") \
        .not_.is_("embedding", "null") \
        .range(offset, offset + BATCH_SIZE - 1) \
        .execute()
        
    batch = response.data
    if not batch:
        break
        
    # Parse embedding string to list if necessary
    for art in batch:
        if isinstance(art['embedding'], str):
            art['embedding'] = json.loads(art['embedding'])
            
    all_articles.extend(batch)
    offset += BATCH_SIZE
    print(f"Fetched {len(all_articles)} articles...")

if not all_articles:
    print("No articles with embeddings found.")
    exit(0)

# Extract embeddings and labels
embeddings = []
labels = []

for art in all_articles:
    if art['embedding']:
        embeddings.append(art['embedding'])
        labels.append(art.get('country_code', 'UNK'))

X = np.array(embeddings)

# Reduce to 2D
print("Reducing dimensions...")
pca = PCA(n_components=2)
X_2d = pca.fit_transform(X)

# Plot
plt.figure(figsize=(12, 8))
unique_labels = list(set(labels))
# Use a colormap that handles many categories well
colors = plt.cm.tab20(np.linspace(0, 1, len(unique_labels)))

for i, label in enumerate(unique_labels):
    mask = [l == label for l in labels]
    plt.scatter(X_2d[mask, 0], X_2d[mask, 1], label=label, alpha=0.6, s=10)

plt.title("Article Clusters by Country (PCA) - Supabase Data")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

output_img = root_dir / "cluster_visualization.png"
plt.savefig(output_img)
print(f"Visualization saved to {output_img}")
