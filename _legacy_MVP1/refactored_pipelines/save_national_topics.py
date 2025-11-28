#!/usr/bin/env python3
"""
Save both global megatopics AND national topics to Supabase
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from supabase import create_client
from dotenv import load_dotenv

# Load environment
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_national_topics(country_topics):
    """
    Save country-level topics to database
    """
    print(f"\n{'='*60}")
    print(f"Saving national topics to Supabase")
    print(f"{'='*60}")
    
    saved_count = 0
    
    for country_code, country_data in country_topics.items():
        topics = country_data.get('topics', [])
        
        print(f"\n{country_code}: {len(topics)}개 토픽")
        
        for topic in topics:
            try:
                # Prepare topic record
                topic_data = {
                    "title": topic.get('title_en', topic['name']),
                    "title_kr": topic['name'],
                    "date": datetime.now(timezone.utc).isoformat(),
                    "country_count": 1,  # National topic = 1 country
                    "centroid_embedding": None,
                    "extraction_method": "llm",
                    "merged_from_topics": []  # National topics don't merge
                }
                
                # Insert topic
                topic_result = supabase.table("mvp_topics").insert(topic_data).execute()
                topic_id = topic_result.data[0]['id']
                
                # Update articles
                article_ids = [a['id'] for a in topic.get('articles', [])]
                if article_ids:
                    supabase.table("mvp_articles").update({"topic_id": topic_id}).in_("id", article_ids).execute()
                
                saved_count += 1
                print(f"  ✅ {topic['name'][:50]}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Saved {saved_count} national topics")
    print(f"{'='*60}")
    
    return saved_count


def main():
    # Load country topics
    country_topics_path = Path('data/pipelines/country_topics.json')
    
    if not country_topics_path.exists():
        print(f"Error: {country_topics_path} not found")
        sys.exit(1)
    
    with open(country_topics_path, 'r', encoding='utf-8') as f:
        country_topics = json.load(f)
    
    print(f"Loaded {len(country_topics)} countries")
    
    total_topics = sum(len(data.get('topics', [])) for data in country_topics.values())
    print(f"Total national topics: {total_topics}")
    
    # Save
    saved = save_national_topics(country_topics)
    
    print(f"\n🎉 Complete! {saved} national topics saved to database")
    
    # Summary
    all_topics = supabase.table('mvp_topics').select('extraction_method').eq('extraction_method', 'llm').execute()
    print(f"\nTotal LLM topics in DB: {len(all_topics.data)}")


if __name__ == "__main__":
    main()
