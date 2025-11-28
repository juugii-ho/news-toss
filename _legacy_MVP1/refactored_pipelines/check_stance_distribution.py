import os
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd

# Load environment
root_dir = Path(__file__).resolve().parent
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_distribution():
    print("Fetching article stances...")
    # Fetch all article stances
    res = supabase.table("mvp_articles").select("stance, stance_score").not_.is_("stance_score", "null").execute()
    articles = res.data
    
    if not articles:
        print("No articles with stance scores found.")
        return

    df_articles = pd.DataFrame(articles)
    print("\n--- Article Stance Distribution ---")
    print(df_articles['stance'].value_counts())
    print("\nScore Stats:")
    print(df_articles['stance_score'].describe())
    
    print("\nFetching articles with topic_id...")
    # Fetch articles with topic_id and stance_score
    res_articles = supabase.table("mvp_articles").select("topic_id, stance_score").not_.is_("topic_id", "null").not_.is_("stance_score", "null").execute()
    
    if not res_articles.data:
        print("No articles with topic_id found.")
        return
        
    # Group by topic_id
    topic_scores = {}
    for a in res_articles.data:
        tid = a['topic_id']
        score = a['stance_score']
        if tid not in topic_scores:
            topic_scores[tid] = []
        topic_scores[tid].append(score)
        
    # Calculate averages
    topic_avgs = []
    for tid, scores in topic_scores.items():
        avg = sum(scores) / len(scores)
        topic_avgs.append(avg)
        
    df_topics = pd.DataFrame(topic_avgs, columns=['avg_stance_score'])
    print("\n--- Topic Avg Stance Distribution (Calculated) ---")
    print(df_topics['avg_stance_score'].describe())
    
    # Check how many are "Neutral" (34-66)
    neutral_topics = df_topics[(df_topics['avg_stance_score'] >= 34) & (df_topics['avg_stance_score'] <= 66)]
    print(f"\nNeutral Topics (34-66): {len(neutral_topics)} / {len(df_topics)} ({len(neutral_topics)/len(df_topics)*100:.1f}%)")

if __name__ == "__main__":
    check_distribution()
