#!/usr/bin/env python3
"""
Full LLM-First Topic Clustering Pipeline

Orchestrates the complete pipeline:
1. Country-level topic extraction (LLM)
2. Global megatopic merging (LLM)  
3. Save to Supabase with vector calculation

Usage:
    python run_llm_pipeline.py --countries KR US JP --save-db

Cost: ~$0.15 for 13 countries (single run)
      ~$18/month for 13 countries × 2 runs/day × 30 days
      With optimizations: ~$1.70/month
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
import numpy as np
from supabase import create_client
from dotenv import load_dotenv

# Import our modules
sys.path.insert(0, str(Path(__file__).parent))
from llm_topic_extractor import extract_country_topics, preprocess_articles_for_llm, COUNTRY_NAMES
from llm_megatopic_merger import merge_into_megatopics

# Load environment
root_dir = Path(__file__).resolve().parents[2]
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def calculate_topic_centroids(megatopics):
    """
    Calculate centroid embedding for each megatopic
    """
    print("\nCalculating topic centroids...")
    
    for mega in megatopics:
        embeddings = [
            a.get('embedding') 
            for a in mega.get('articles', [])
            if a.get('embedding')
        ]
        
        if embeddings:
            mega['centroid_embedding'] = np.mean(embeddings, axis=0).tolist()
        else:
            mega['centroid_embedding'] = None
    
    return megatopics


def save_to_supabase(megatopics):
    """
    Save megatopics to Supabase mvp_topics table
    """
    print(f"\n{'='*60}")
    print(f"Saving {len(megatopics)} megatopics to Supabase")
    print(f"{'='*60}")
    
    saved_count = 0
    
    for mega in megatopics:
        try:
            # Prepare topic record
            topic_data = {
                "title": mega['title_en'],
                "title_kr": mega['title_kr'],
                "date": datetime.now(timezone.utc).isoformat(),
                "country_count": len(mega['countries_involved']),
                "centroid_embedding": mega.get('centroid_embedding'),
                "merged_from_topics": mega.get('merged_topic_ids', []),
                "extraction_method": "llm"
            }
            
            # Insert topic
            topic_result = supabase.table("mvp_topics").insert(topic_data).execute()
            topic_id = topic_result.data[0]['id']
            
            # Update articles
            article_ids = [a['id'] for a in mega.get('articles', [])]
            if article_ids:
                supabase.table("mvp_articles").update({"topic_id": topic_id}).in_("id", article_ids).execute()
            
            # Calculate stats per country
            stats_by_country = {}
            for article in mega.get('articles', []):
                country = article.get('country_code')
                if country:
                    if country not in stats_by_country:
                        stats_by_country[country] = {
                            'articles': [],
                            'sources': set()
                        }
                    stats_by_country[country]['articles'].append(article)
                    stats_by_country[country]['sources'].add(article.get('source', ''))
            
            # Save country stats
            for country, data in stats_by_country.items():
                stat_record = {
                    "topic_id": topic_id,
                    "country_code": country,
                    "article_count": len(data['articles']),
                    "source_count": len(data['sources']),
                    "total_supportive": sum(1 for a in data['articles'] if (a.get('stance_score') or 50) > 66),
                    "total_factual": sum(1 for a in data['articles'] if 33 <= (a.get('stance_score') or 50) <= 66),
                    "total_critical": sum(1 for a in data['articles'] if (a.get('stance_score') or 50) < 33)
                }
                supabase.table("mvp_topic_country_stats").insert(stat_record).execute()
            
            saved_count += 1
            if saved_count % 10 == 0:
                print(f"  Saved {saved_count}/{len(megatopics)} topics...")
                
        except Exception as e:
            print(f"  Error saving topic '{mega.get('title_kr', 'Unknown')}': {e}")
    
    print(f"\n✅ Successfully saved {saved_count} megatopics to database")
    return saved_count


def main():
    parser = argparse.ArgumentParser(description='Run full LLM-First clustering pipeline')
    parser.add_argument('--countries', nargs='+', help='Country codes (e.g., KR US JP)')
    parser.add_argument('--all', action='store_true', help='Process all countries')
    parser.add_argument('--save-db', action='store_true', help='Save results to Supabase')
    parser.add_argument('--output-dir', type=str, default='data/pipelines', help='Output directory')
    
    args = parser.parse_args()
    
    # Determine countries
    if args.all:
        countries = list(COUNTRY_NAMES.keys())
    elif args.countries:
        countries = args.countries
    else:
        print("Error: Specify --countries CODE1 CODE2 or --all")
        sys.exit(1)
    
    print(f"\n{'#'*60}")
    print(f"# LLM-First Topic Clustering Pipeline")
    print(f"# Countries: {', '.join(countries)}")
    print(f"{'#'*60}")
    
    # Step 1: Extract country topics
    print(f"\n{'='*60}")
    print(f"STEP 1: Extracting country-level topics")
    print(f"{'='*60}")
    
    country_topics_dict = {}
    since = datetime.now(timezone.utc) - timedelta(hours=72)
    
    for country in countries:
        # Fetch articles
        response = supabase.table('mvp_articles') \
            .select('*') \
            .eq('country_code', country) \
            .gte('published_at', since.isoformat()) \
            .order('published_at', desc=True) \
            .limit(200) \
            .execute()
        
        articles = response.data
        
        if not articles:
            print(f"\nNo articles for {country}, skipping...")
            continue
        
        # Extract topics
        result = extract_country_topics(country, articles, target_topics=15)
        
        if result:
            country_topics_dict[country] = result
    
    # Step 2: Merge into megatopics
    print(f"\n{'='*60}")
    print(f"STEP 2: Merging into global megatopics")
    print(f"{'='*60}")
    
    megatopics = merge_into_megatopics(country_topics_dict, target_megas=80)
    
    if not megatopics:
        print("Error: Failed to create megatopics")
        sys.exit(1)
    
    # Step 3: Calculate vectors
    print(f"\n{'='*60}")
    print(f"STEP 3: Calculating topic centroids")
    print(f"{'='*60}")
    
    megatopics = calculate_topic_centroids(megatopics)
    
    # Save intermediate results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / 'country_topics_full.json', 'w', encoding='utf-8') as f:
        json.dump(country_topics_dict, f, ensure_ascii=False, indent=2)
    
    with open(output_dir / 'megatopics_full.json', 'w', encoding='utf-8') as f:
        json.dump(megatopics, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved intermediate results to {output_dir}")
    
    # Step 4: Save to DB
    if args.save_db:
        saved = save_to_supabase(megatopics)
        print(f"\n{'='*60}")
        print(f"✅ Pipeline complete! Saved {saved} topics to database")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"✅ Pipeline complete! (Dry run - not saved to DB)")
        print(f"Use --save-db to save to database")
        print(f"{'='*60}")
    
    # Summary
    total_articles = sum(m['article_count'] for m in megatopics)
    avg_countries = sum(len(m['countries_involved']) for m in megatopics) / len(megatopics) if megatopics else 0
    
    print(f"\nFinal Summary:")
    print(f"  Countries processed: {len(country_topics_dict)}")
    print(f"  Global megatopics: {len(megatopics)}")
    print(f"  Total articles: {total_articles}")
    print(f"  Avg countries per topic: {avg_countries:.1f}")


if __name__ == "__main__":
    main()
