import json
from collections import Counter

def analyze_clusters():
    try:
        with open("classified_topics.json", "r") as f:
            clusters = json.load(f)
    except FileNotFoundError:
        print("classified_topics.json not found.")
        return

    print(f"Total Clusters: {len(clusters)}")
    
    sizes = [len(c) for c in clusters]
    size_counts = Counter(sizes)
    
    print("\nCluster Size Distribution:")
    for size in sorted(size_counts.keys()):
        print(f"Size {size}: {size_counts[size]} clusters")
        
    print("\n--- Top 5 Largest Clusters ---")
    clusters.sort(key=len, reverse=True)
    for i, c in enumerate(clusters[:5]):
        countries = set(a['country_code'] for a in c)
        print(f"\nCluster {i+1} (Size: {len(c)}, Countries: {len(countries)} - {countries})")
        print(f"Title: {c[0]['title']}")
        # Print first 3 titles to see coherence
        for a in c[:3]:
            print(f"  - [{a['country_code']}] {a['title']}")

    print("\n--- 5 Random 'Global' Clusters (Size < 5) ---")
    # Check small "global" clusters to see if they are noise
    small_globals = [c for c in clusters if len(c) < 5 and len(set(a['country_code'] for a in c)) >= 2]
    for i, c in enumerate(small_globals[:5]):
        countries = set(a['country_code'] for a in c)
        print(f"\nSmall Global {i+1} (Size: {len(c)}, Countries: {countries})")
        for a in c:
            print(f"  - [{a['country_code']}] {a['title']}")

if __name__ == "__main__":
    analyze_clusters()
