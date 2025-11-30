import os
import glob
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load env
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", "..", "backend", ".env")
load_dotenv(env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def extract_topics():
    summary_dir = os.path.join(script_dir, "..", "..", "outputs", "topic_summaries")
    files = glob.glob(os.path.join(summary_dir, "*_topics.md"))
    
    all_topics = []
    
    for fpath in files:
        country = os.path.basename(fpath).split("_")[0]
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Find headers like "## 1. Topic Title"
        matches = re.findall(r"## \d+\. (.+)", content)
        for title in matches:
            all_topics.append(f"[{country}] {title.strip()}")
            
    return all_topics

def simulate_clustering(topics):
    model = genai.GenerativeModel("gemini-2.5-pro")
    
    topics_str = "\n".join(topics)
    
    prompt = f"""
Role: Global News Editor
Task: Analyze the following list of local news topics from various countries and group them into "Megatopics" (Global Issues).

Input Topics:
{topics_str}

Instructions:
1. Group topics that refer to the SAME event or closely related themes.
2. Ignore purely local/domestic issues that don't have cross-border relevance (unless they are major).
3. Create a list of Megatopics with a Global Headline and the list of included local topics.
4. Finally, count how many Megatopics you found.

Output Format:
- **Megatopic 1: [Global Headline]**
  - [Country] Local Topic A
  - [Country] Local Topic B
...
- **Total Megatopics**: N
"""
    print(f"Analyzing {len(topics)} topics...")
    response = model.generate_content(prompt)
    print(response.text)

if __name__ == "__main__":
    topics = extract_topics()
    if not topics:
        print("No topics found.")
    else:
        simulate_clustering(topics)
