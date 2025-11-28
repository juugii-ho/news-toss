#!/usr/bin/env python3
"""
LLM-based Megatopic Merger using standardized utilities.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from utils import get_logger, call_gemini_with_retry, generate_headlines_batch

# Initialize logger
logger = get_logger(__name__)

def merge_into_megatopics(country_topics_dict: dict) -> list | None:
    """
    Merges country-level topics into global megatopics using an LLM.
    """
    logger.info("Merging country topics into global megatopics...")

    topics_text = ""
    topic_index = {}
    for country, country_data in country_topics_dict.items():
        for i, topic in enumerate(country_data.get('topics', []), 1):
            topic_id = f"{country}-topic-{i}"
            topic_index[topic_id] = {'country': country, 'topic': topic}
            topics_text += f'{topic_id}: "{topic["name"]}"\n'
    
    total_topics = len(topic_index)
    if total_topics == 0:
        logger.warning("No country topics to merge.")
        return []
        
    logger.info(f"Total country topics to merge: {total_topics}")

    prompt = f"""Role: You are an expert editor for a global news aggregator.
Task: Merge {total_topics} country-level topics by identifying the SAME events across countries.
CRITICAL: Be conservative. Merge ONLY when events are clearly identical. When in doubt, keep them separate.

Input Data (ID: "Topic Name"):
{topics_text}

Instructions:
1. Identify Same Events: Merge if topics describe the EXACT SAME event (e.g., "Hong Kong fire" in KR, CN, GB).
2. Keep Distinct Events Separate: DO NOT merge related but different events (e.g., "Trump peace proposal" vs "Europe's reaction to Trump").
3. Output: List all merged groups. Each group needs a unified Korean headline (casual, complete sentence), an English title, and the list of merged topic IDs.

Output Format (JSON only):
{{
  "megatopics": [
    {{
      "id": "mega-001",
      "title_kr": "홍콩 아파트 화재, 왜 참사가 됐을까?",
      "title_en": "Hong Kong Apartment Fire Tragedy",
      "merged_topic_ids": ["KR-topic-7", "US-topic-3"]
    }}
  ]
}}"""

    logger.info("Calling Gemini API for global merging...")
    response_text = call_gemini_with_retry(prompt)
    if not response_text:
        logger.error("Failed to get a response from Gemini for merging.")
        return None

    try:
        if '```json' in response_text:
            json_text = response_text.split('```json')[1].split('```')[0].strip()
        else:
            json_text = response_text.strip()
        
        result = json.loads(json_text)
        megatopics = result.get('megatopics')

        if megatopics is None:
            logger.error("Response from LLM is missing the 'megatopics' key.")
            return None
        
        logger.info(f"LLM created {len(megatopics)} global megatopics.")
        
        # Enrich megatopics with original article data
        for mega in megatopics:
            mega['articles'] = []
            mega['countries_involved'] = set()
            for topic_id in mega.get('merged_topic_ids', []):
                if topic_id in topic_index:
                    topic_data = topic_index[topic_id]
                    mega['articles'].extend(topic_data['topic'].get('articles', []))
                    mega['countries_involved'].add(topic_data['country'])
            mega['countries_involved'] = list(mega['countries_involved'])
            mega['article_count'] = len(mega['articles'])

        # Generate headlines in a single batch call
        logger.info(f"Generating {len(megatopics)} megatopic headlines in batch...")
        headline_data = [
            {'name': m.get('title_kr', ''), 'article_titles': [a.get('title_kr', a.get('title', '')) for a in m['articles'][:5]]}
            for m in megatopics
        ]
        headlines = generate_headlines_batch(headline_data)
        for mega, headline in zip(megatopics, headlines):
            mega['headline'] = headline
        
        return megatopics

    except Exception as e:
        logger.error(f"Error processing LLM response for megatopics: {e}", exc_info=True)
        logger.error(f"Problematic response text (first 500 chars): {response_text[:500]}")
        return None

def save_results(data, filename):
    """Saves data to a JSON file in the outputs directory."""
    if not data:
        logger.warning("No data to save.")
        return
    output_dir = Path(__file__).resolve().parents[2] / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Saved results to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save results to {output_path}: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description='Merge country topics into global megatopics.')
    parser.add_argument('--input', type=str, default='llm_extracted_topics.json', help='Input file from topic extraction step, located in the outputs directory.')
    parser.add_argument('--output', type=str, default='megatopics_full.json', help='Output file name to be saved in the outputs directory.')
    args = parser.parse_args()

    input_path = Path(__file__).resolve().parents[2] / "outputs" / args.input
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}. Run llm_topic_extractor.py first.")
        sys.exit(1)
        
    logger.info(f"Loading country topics from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        country_topics = json.load(f)

    megatopics = merge_into_megatopics(country_topics)
    if not megatopics:
        logger.error("Megatopic merging process failed.")
        sys.exit(1)
        
    save_results(megatopics, args.output)
    
    logger.info("Megatopic merging pipeline finished.")
    # ... (summary printout can be added here if needed)

if __name__ == "__main__":
    main()