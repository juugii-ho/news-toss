import json
from collections import Counter
from pathlib import Path

root_dir = Path(__file__).resolve().parents[2]
input_file = root_dir / "data/pipelines/embedded_articles.json"

if not input_file.exists():
    print("File not found")
    exit(1)

with open(input_file, "r") as f:
    data = json.load(f)
    
print("Total articles:", len(data))
print("Country distribution:", Counter(d.get('country_code') for d in data))
