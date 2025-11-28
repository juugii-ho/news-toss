import os
import sys
import numpy as np
from datetime import datetime, timedelta
from supabase import create_client, Client
from sklearn.metrics.pairwise import cosine_distances
from dotenv import load_dotenv

# Load env vars
load_dotenv()
load_dotenv(".env.local")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found. Please set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or NEXT_PUBLIC_SUPABASE_ANON_KEY).")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_date_str(days_offset=0):
    return (datetime.now() + timedelta(days=days_offset)).strftime('%Y-%m-%d')

def calculate_category(intensity: int) -> int:
    """
    Calculate Storm Category (1-5) based on intensity.
    Category 1: <20
    Category 2: 20-50
    Category 3: 50-100
    Category 4: 100-150
    Category 5: 150+
    """
    if intensity < 20: return 1
    if intensity < 50: return 2
    if intensity < 100: return 3
    if intensity < 150: return 4
    return 5

def estimate_status(drift_score: float, is_new: bool) -> str:
    """
    Estimate Topic Status based on drift.
    - forming: New topic
    - strengthening: High drift (> 0.15) implying active development
    - mature: Moderate drift (0.05 - 0.15)
    - weakening: Low drift (< 0.05) implying stagnation
    """
    if is_new:
        return 'forming'
    if drift_score is None:
        return 'mature'
    if drift_score > 0.15:
        return 'strengthening'
    if drift_score > 0.05:
        return 'mature'
    return 'weakening'

def match_topics():
    today_str = get_date_str(0)
    yesterday_str = get_date_str(-1)
    
    print(f"Matching topics for {today_str} (comparing with {yesterday_str})...")
    
    # 1. Fetch Today's Topics
    # We need to fetch topics created/updated today. 
    # Assuming mvp_topics has 'created_at' or we just fetch all active ones?
    # Better: fetch topics that don't have a history entry for today yet?
    # For MVP, let's fetch ALL topics from mvp_topics (assuming it holds current state)
    # and try to match them.
    
    # Fetch today's topics (limit 100 for safety)
    today_response = supabase.table("mvp_topics").select("*").order("country_count", desc=True).limit(100).execute()
    today_topics = today_response.data
    
    if not today_topics:
        print("No topics found for today.")
        return

    # 2. Fetch Yesterday's History
    # We look for history records with date = yesterday
    yesterday_response = supabase.table("mvp_topic_history").select("*").eq("date", yesterday_str).execute()
    yesterday_history = yesterday_response.data
    
    print(f"Found {len(today_topics)} topics today, {len(yesterday_history)} history records from yesterday.")
    
    # 3. Match Logic
    # If yesterday_history is empty (first run), all today's topics are NEW.
    
    new_history_records = []
    
    for topic in today_topics:
        # Check if we already have a history record for this topic TODAY
        # (Idempotency check)
        existing = supabase.table("mvp_topic_history").select("id").eq("topic_id", topic['id']).eq("date", today_str).execute()
        if existing.data:
            print(f"Skipping topic {topic['title'][:20]}... (already processed)")
            continue
            
        best_match = None
        min_drift = float('inf')
        
        # Parse embedding (it comes as string or list?)
        # Supabase pgvector returns string usually? Or python client handles it?
        # Let's assume list. If string, need json.loads.
        today_emb = topic.get('centroid_embedding')
        if isinstance(today_emb, str):
            import json
            today_emb = json.loads(today_emb)
            
        if not today_emb:
            print(f"Warning: No embedding for topic {topic['id']}")
            continue
            
        today_countries = set(topic.get('countries', []))
        
        if yesterday_history:
            for hist in yesterday_history:
                hist_emb = hist.get('centroid_embedding')
                if isinstance(hist_emb, str):
                    import json
                    hist_emb = json.loads(hist_emb)
                
                if not hist_emb: continue
                
                # Calculate Drift (Cosine Distance)
                # cosine_distances expects 2D arrays
                drift = cosine_distances([today_emb], [hist_emb])[0][0]
                
                # Check Country Overlap
                # (Optional but good for verification)
                # For now, rely mainly on embedding + maybe title similarity?
                # Let's stick to embedding drift as primary signal.
                
                if drift < min_drift:
                    min_drift = drift
                    best_match = hist
        
        # Thresholds
        # Drift < 0.25 AND (maybe) Country Overlap?
        # Let's use strict drift threshold for now.
        
        is_new = True
        parent_id = None
        final_drift = None
        
        if best_match and min_drift < 0.25:
            is_new = False
            parent_id = best_match['id']
            final_drift = float(min_drift)
            print(f"Match: '{topic['title'][:20]}' <- '{best_match['title_en'][:20]}' (Drift: {final_drift:.4f})")
        else:
            print(f"New: '{topic['title'][:20]}' (Min Drift: {min_drift:.4f})")
            
        # Calculate Metadata
        article_count = topic.get('article_count', 0)
        country_count = topic.get('country_count', 0)
        intensity = article_count * country_count
        
        # Use Helper Functions
        category = calculate_category(intensity)
        status = estimate_status(final_drift, is_new)
        
        # Countries
        # Fetch from mvp_topic_country_stats
        countries_res = supabase.table("mvp_topic_country_stats").select("country_code").eq("topic_id", topic['id']).execute()
        countries = [c['country_code'] for c in countries_res.data] if countries_res.data else []
        
        # Stance Variance
        # We need to fetch articles for this topic to calculate variance of 'stance_score'
        # Assuming mvp_articles has 'stance_score' (0-100)
        articles_res = supabase.table("mvp_articles").select("stance_score").eq("topic_id", topic['id']).execute()
        stance_scores = [a['stance_score'] for a in articles_res.data if a.get('stance_score') is not None]
        
        stance_variance = 0.0
        if len(stance_scores) > 1:
            stance_variance = float(np.var(stance_scores))
        
        # Prepare Record
        record = {
            "topic_id": topic['id'],
            "date": today_str,
            "title_en": topic.get('title'), # Use 'title' as English title
            "title_kr": topic.get('title_kr'),
            "centroid_embedding": topic.get('centroid_embedding'), # Pass as is (list or string)
            "article_count": article_count,
            "country_count": country_count,
            "avg_stance_score": topic.get('avg_stance_score'), 
            "stance_variance": stance_variance,
            "drift_score": final_drift,
            "is_new_topic": is_new,
            "parent_topic_id": parent_id,
            "intensity": intensity,
            "category": category,
            "status": status,
            "countries": countries
        }
        new_history_records.append(record)
        
    # 4. Batch Insert
    if new_history_records:
        print(f"Inserting {len(new_history_records)} history records...")
        # Supabase insert can handle batch?
        # Yes, usually.
        try:
            supabase.table("mvp_topic_history").insert(new_history_records).execute()
            print("Success!")
        except Exception as e:
            print(f"Error inserting history: {e}")
            # Fallback: insert one by one
            for rec in new_history_records:
                try:
                    supabase.table("mvp_topic_history").insert(rec).execute()
                except Exception as inner_e:
                    print(f"Failed to insert record for {rec['title_en']}: {inner_e}")

if __name__ == "__main__":
    match_topics()
