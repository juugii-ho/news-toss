#!/usr/bin/env python3
"""
Save corrected LLM topics (megatopics + national) to Supabase
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


def save_megatopics(megatopics):
    """Save global megatopics"""
    print(f"\n{'='*60}")
    print(f"Saving {len(megatopics)} global megatopics")
    print(f"{'='*60}")
    
    for mega in megatopics:
        title_kr = mega.get('title_kr', '')
        headline = mega.get('headline') or title_kr  # Fallback to title_kr if headline is missing
        
        # Check if topic already exists today
        today = datetime.now(timezone.utc).date().isoformat()
        existing = supabase.table("mvp_topics").select("id").eq("date", today).eq("title_kr", title_kr).execute()
        
        if existing.data:
            topic_id = existing.data[0]['id']
            print(f"  ⚠️ Topic already exists: {title_kr[:30]}... (ID: {topic_id})")
        else:
            topic_data = {
                "title": mega.get('title_en', ''),
                "title_kr": title_kr,
                "headline": headline,  # 뉴닉 스타일 뉴스 제목
                "date": datetime.now(timezone.utc).isoformat(),
                "country_count": len(mega.get('countries_involved', [])),
                "merged_from_topics": mega.get('merged_topic_ids', []),
                "extraction_method": "llm"
            }
            # print(f"  DEBUG: Headline for {title_kr[:20]}... -> {headline}")
            
            result = supabase.table("mvp_topics").insert(topic_data).execute()
            topic_id = result.data[0]['id']
            print(f"  ✅ Created: {title_kr[:30]}...")
        
        # Update articles (Always update to fix missing links)
        article_ids = [a['id'] for a in mega.get('articles', [])]
        if article_ids:
            supabase.table("mvp_articles").update({"topic_id": topic_id}).in_("id", article_ids).execute()
            # print(f"    -> Linked {len(article_ids)} articles")
    
    print(f"✅ Processed {len(megatopics)} megatopics")


def save_national_topics(country_topics, merged_ids_set):
    """Save national topics (excluding merged ones)"""
    print(f"\n{'='*60}")
    print(f"Saving national topics (excluding merged)")
    print(f"{'='*60}")
    
    saved_count = 0
    today = datetime.now(timezone.utc).date().isoformat()
    
    for country, data in country_topics.items():
        topics = data.get('topics', [])
        
        for i, topic in enumerate(topics, 1):
            topic_id_str = f"{country}-topic-{i}"
            
            # Skip if already merged into megatopic
            if topic_id_str in merged_ids_set:
                continue
            
            title_kr = topic['name']
            
            # Check existence
            existing = supabase.table("mvp_topics").select("id").eq("date", today).eq("title_kr", title_kr).execute()
            
            if existing.data:
                topic_id_db = existing.data[0]['id']
                # print(f"  ⚠️ Topic exists: {title_kr[:20]}...")
            else:
                topic_data = {
                    "title": topic.get('title_en', topic['name']),
                    "title_kr": title_kr,
                    "headline": topic.get('headline', topic['name'][:50]),  # 뉴닉 제목
                    "date": datetime.now(timezone.utc).isoformat(),
                    "country_count": 1,
                    "extraction_method": "llm"
                }
                
                result = supabase.table("mvp_topics").insert(topic_data).execute()
                topic_id_db = result.data[0]['id']
                # print(f"  ✅ Created: {title_kr[:20]}...")
            
            # Update articles
            article_ids = [a['id'] for a in topic.get('articles', [])]
            if article_ids:
                supabase.table("mvp_articles").update({"topic_id": topic_id_db}).in_("id", article_ids).execute()
            
            saved_count += 1
    
    print(f"✅ Processed {saved_count} national topics")
    return saved_count


def main():
    # Load megatopics
    with open('data/pipelines/megatopics.json', 'r') as f:
        megatopics = json.load(f)
    
    # Get merged IDs
    merged_ids = set()
    for mega in megatopics:
        merged_ids.update(mega.get('merged_topic_ids', []))
    
    print(f"Merged topic IDs: {len(merged_ids)}")
    
    # Save megatopics
    save_megatopics(megatopics)
    
    # Load country topics
    with open('data/pipelines/country_topics.json', 'r') as f:
        country_topics = json.load(f)
    
    # Save national topics
    national_count = save_national_topics(country_topics, merged_ids)
    
    print(f"\n🎉 Complete!")
    print(f"  Global megatopics: {len(megatopics)}")
    print(f"  National topics: {national_count}")
    print(f"  Total: {len(megatopics) + national_count}")


if __name__ == "__main__":
    main()
