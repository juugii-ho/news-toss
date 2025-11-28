#!/usr/bin/env python3
"""
Saves final processed megatopics to the Supabase database.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from utils import get_supabase_client, get_logger

# Initialize logger
logger = get_logger(__name__)

def calculate_centroids(megatopics):
    """Calculates and adds centroid embeddings to each megatopic in place."""
    logger.info("Calculating topic centroids...")
    for mega in megatopics:
        embeddings = []
        for a in mega.get('articles', []):
            emb = a.get('embedding')
            if emb and isinstance(emb, list):
                embeddings.append(np.array(emb, dtype=float))
        
        if embeddings:
            mega['centroid_embedding'] = np.mean(embeddings, axis=0).tolist()
        else:
            mega['centroid_embedding'] = None
    logger.info("Centroid calculation complete.")

def save_megatopics(megatopics):
    """Saves a list of megatopics and their related data to Supabase."""
    logger.info(f"Attempting to save {len(megatopics)} megatopics to Supabase...")
    supabase = get_supabase_client()
    saved_count = 0
    
    for mega in megatopics:
        title_kr = mega.get('title_kr', 'Unknown Topic')
        try:
            # 1. Prepare and insert the main topic record
            topic_data = {
                "title": mega.get('title_en', ''),
                "title_kr": title_kr,
                "date": datetime.now(timezone.utc).isoformat(),
                "country_count": len(mega.get('countries_involved', [])),
                "centroid_embedding": mega.get('centroid_embedding'),
                "merged_from_topics": mega.get('merged_topic_ids', []),
                "extraction_method": "llm"
            }
            topic_result = supabase.table("mvp_topics").insert(topic_data).execute()
            topic_id = topic_result.data[0]['id']
            logger.info(f"  ✓ Saved topic: '{title_kr}' (ID: {topic_id})")
            
            # 2. Update associated articles with the new topic_id
            article_ids = [a['id'] for a in mega.get('articles', []) if 'id' in a]
            if article_ids:
                supabase.table("mvp_articles").update({"topic_id": topic_id}).in_("id", article_ids).execute()
                logger.info(f"    - Linked {len(article_ids)} articles.")

            # 3. Calculate and save per-country statistics
            stats_by_country = {}
            for article in mega.get('articles', []):
                country = article.get('country_code')
                if country:
                    if country not in stats_by_country:
                        stats_by_country[country] = {'articles': [], 'sources': set()}
                    stats_by_country[country]['articles'].append(article)
                    stats_by_country[country]['sources'].add(article.get('source', ''))
            
            for country, data in stats_by_country.items():
                stance_scores = [a.get('stance_score', 50) for a in data['articles']]
                
                sql = f"""
                INSERT INTO mvp_topic_country_stats 
                (topic_id, country_code, article_count, source_count, total_supportive, total_factual, total_critical)
                VALUES (
                    {topic_id}, '{country}', {len(data['articles'])}, {len(data['sources'])},
                    {sum(1 for s in stance_scores if s > 66)},
                    {sum(1 for s in stance_scores if 33 <= s <= 66)},
                    {sum(1 for s in stance_scores if s < 33)}
                )
                ON CONFLICT (topic_id, country_code) DO UPDATE SET 
                    article_count = EXCLUDED.article_count, source_count = EXCLUDED.source_count,
                    total_supportive = EXCLUDED.total_supportive, total_factual = EXCLUDED.total_factual,
                    total_critical = EXCLUDED.total_critical;
                """
                # Use rpc to execute raw SQL
                supabase.rpc('exec_sql', {'query': sql}).execute()
            logger.info(f"    - Saved stats for {len(stats_by_country)} countries.")

            saved_count += 1
                
        except Exception as e:
            logger.error(f"  ✗ Error saving '{title_kr}': {e}", exc_info=True)
    
    logger.info(f"Successfully saved {saved_count}/{len(megatopics)} megatopics.")
    return saved_count

def main():
    """Main execution block."""
    # Define input path relative to this script, pointing to the project's outputs dir
    input_filename = "megatopics_full.json" # Or whatever the previous step produces
    input_path = Path(__file__).resolve().parents[2] / "outputs" / input_filename

    if not input_path.exists():
        logger.error(f"Input file not found at {input_path}")
        sys.exit(1)
    
    logger.info(f"Loading megatopics from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        megatopics = json.load(f)
    
    calculate_centroids(megatopics)
    save_megatopics(megatopics)
    
    logger.info("🎉 Save to DB pipeline finished.")

if __name__ == "__main__":
    main()