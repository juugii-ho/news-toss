#!/usr/bin/env python3
"""
LLM-based Topic Extractor using standardized utilities.
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import our standardized utilities
from utils import get_supabase_client, get_gemini_model, get_logger

# Initialize logger
logger = get_logger(__name__)

# Constants
COUNTRY_NAMES = {
    'KR': '대한민국', 'US': '미국', 'CN': '중국', 'JP': '일본',
    'GB': '영국', 'DE': '독일', 'FR': '프랑스', 'RU': '러시아',
    'IT': '이탈리아', 'BE': '벨기에', 'NL': '네덜란드', 'AU': '호주'
}
LIVE_KEYWORDS = [
    'live', 'breaking', 'latest', 'update', 'news live',
    '속보', '긴급', '최신', '종합', '라이브'
]

def is_live_news(title):
    title_lower = title.lower()
    if any(kw in title_lower for kw in LIVE_KEYWORDS):
        if ';' in title or '|' in title:
            return True
        if 'live' in title_lower and ('update' in title_lower or 'news' in title_lower):
            return True
    return False

def calculate_title_similarity(title1, title2):
    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio()

def remove_near_duplicates(articles, threshold=0.95):
    seen = []
    unique = []
    for article in articles:
        title = article.get('title_kr') or article['title']
        if not any(calculate_title_similarity(title, seen_title) > threshold for seen_title in seen):
            seen.append(title)
            unique.append(article)
    return unique

def preprocess_articles_for_llm(articles, country_code):
    logger.info(f"Preprocessing {len(articles)} articles for {country_code}...")
    filtered = [a for a in articles if not is_live_news(a.get('title_kr') or a['title'])]
    logger.info(f"  After LIVE filter: {len(filtered)} articles")
    deduped = remove_near_duplicates(filtered, threshold=0.95)
    logger.info(f"  After deduplication: {len(deduped)} articles")
    final = sorted(deduped, key=lambda x: x.get('published_at', ''), reverse=True)
    logger.info(f"  Final count for LLM: {len(final)} articles")
    return final

def call_gemini_with_retry(prompt, retries=3):
    """Calls the Gemini model with a prompt and handles retries."""
    try:
        model = get_gemini_model()
        generation_config = {
            "temperature": 0.3, "topP": 0.95, "topK": 40, "maxOutputTokens": 16384,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]

        for attempt in range(retries):
            try:
                response = model.generate_content(
                    contents=prompt,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini API call failed on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    wait_time = 2 ** (attempt + 1)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Gemini API call failed after all retries.")
                    return None
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}")
        return None

def process_batch(batch_index, batch_articles, preprocessed_articles, country_code, batch_size):
    """Processes a single batch of articles to extract topics."""
    articles_text = "\n".join([
        f"[{i+1}] {a.get('title_kr') or a['title']}"
        for i, a in enumerate(batch_articles)
    ])
    
    prompt = f"""Role: You are an expert media analyst for \"News Spectrum,\" a global news aggregator.
Task: Analyze these {len(batch_articles)} articles from {COUNTRY_NAMES.get(country_code, country_code)} and group them into distinct micro-topics.
CRITICAL: You MUST assign ALL {len(batch_articles)} articles to topics.

Rules:
1. Create topics based on content. Each topic must be a distinct news event.
2. Every article MUST be assigned to a topic. This is the most important rule.
3. Topics should be mutually exclusive.
4. If an article doesn't fit, create a new topic or assign to the closest match.

Input Data:
{articles_text}

Instructions:
1. Topic Naming:
   - `name`: Standard journalistic title in Korean (e.g., \"독일 AfD 방화벽 논쟁\").
   - `headline`: Newnic-style engaging headline in Korean (casual, curious tone, complete sentence, under 45 chars).
2. Article Mapping:
   - Assign article IDs [1, 2, 3...] to each topic. Each ID must appear in ONLY ONE topic.
3. Output Format (JSON only, no explanations):
{{
  "topics": [
    {{
      "name": "독일 AfD 방화벽 논쟁",
      "headline": "독일 기업들, AfD에 등 돌린 진짜 이유 🚫",
      "article_ids": [1, 4, 8],
      "title_en": "German AfD firewall debate"
    }}
  ],
  "unassigned_article_ids": []
}}"""

    response_text = call_gemini_with_retry(prompt)
    if not response_text:
        logger.error(f"Failed to get response for batch {batch_index + 1}")
        return []

    try:
        if '```json' in response_text:
            json_text = response_text.split('```json')[1].split('```')[0].strip()
        else:
            json_text = response_text.strip()
        
        result = json.loads(json_text)
        batch_topics = result.get('topics', [])
        
        global_offset = batch_index * batch_size
        for topic in batch_topics:
            topic['articles'] = []
            global_ids = []
            if 'article_ids' in topic:
                for local_id in topic['article_ids']:
                    if 0 < local_id <= len(batch_articles):
                        global_idx = global_offset + (local_id - 1)
                        if global_idx < len(preprocessed_articles):
                            global_ids.append(global_idx + 1)
                            topic['articles'].append(preprocessed_articles[global_idx])
            topic['article_ids'] = global_ids
            topic['country_code'] = country_code
            if 'headline' not in topic:
                topic['headline'] = topic['name']
        return batch_topics

    except Exception as e:
        logger.error(f"Error parsing JSON for batch {batch_index + 1}: {e}")
        return []

def extract_country_topics(country_code, articles, target_topics=15):
    logger.info(f"Extracting topics for {country_code} ({COUNTRY_NAMES.get(country_code, country_code)})")
    
    preprocessed = preprocess_articles_for_llm(articles, country_code)
    if len(preprocessed) < 10:
        logger.warning(f"Only {len(preprocessed)} articles after preprocessing. Skipping topic extraction for {country_code}.")
        return None

    BATCH_SIZE = 20
    batches = [preprocessed[i:i + BATCH_SIZE] for i in range(0, len(preprocessed), BATCH_SIZE)]
    logger.info(f"Split into {len(batches)} batches. Processing in parallel...")
    
    all_topics = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_batch = {
            executor.submit(process_batch, i, batch, preprocessed, country_code, BATCH_SIZE):
            i
            for i, batch in enumerate(batches)
        }
        for future in as_completed(future_to_batch):
            batch_idx = future_to_batch[future]
            try:
                topics = future.result()
                if topics:
                    all_topics.extend(topics)
                    logger.info(f"  ✓ Batch {batch_idx + 1}/{len(batches)} done ({len(topics)} topics)")
                else:
                    logger.error(f"  ✗ Batch {batch_idx + 1}/{len(batches)} failed or returned no topics.")
            except Exception as exc:
                logger.error(f"  ✗ Batch {batch_idx + 1} generated an exception: {exc}", exc_info=True)

    assigned_count = sum(len(t.get('articles', [])) for t in all_topics)
    logger.info(f"Total extracted {len(all_topics)} topics from {len(preprocessed)} articles.")
    logger.info(f"Article coverage: {assigned_count}/{len(preprocessed)} assigned.")
    
    return {'country_code': country_code, 'topics': all_topics}

def save_results(data, filename):
    """Saves data to a JSON file in the outputs directory."""
    if not data:
        logger.warning("No data to save.")
        return

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'outputs'))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Successfully saved results to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save results to {output_path}: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description='Extract country-level topics using LLM')
    parser.add_argument('--country', type=str, help='Country code (e.g., KR, US)')
    parser.add_argument('--all', action='store_true', help='Process all countries')
    parser.add_argument('--limit', type=int, default=150, help='Max articles per country')
    parser.add_argument('--topics', type=int, default=15, help='Target number of topics')
    parser.add_argument('--output', type=str, default='llm_extracted_topics.json', help='Output file name')
    args = parser.parse_args()

    countries_to_process = list(COUNTRY_NAMES.keys()) if args.all else [args.country] if args.country else []
    if not countries_to_process:
        logger.error("Error: Specify --country CODE or --all")
        sys.exit(1)

    all_results = {}
    supabase = get_supabase_client()
    since = datetime.now(timezone.utc) - timedelta(hours=36)

    for i, country in enumerate(countries_to_process):
        if i > 0:
            logger.info("Sleeping for 2 seconds to avoid rate limiting...")
            time.sleep(2)
        
        try:
            logger.info(f"Fetching articles for {country}...")
            response = supabase.table('mvp_articles').select('*').eq('country_code', country).gte('published_at', since.isoformat()).order('published_at', desc=True).limit(args.limit).execute()
            articles = response.data
            
            if not articles:
                logger.warning(f"No recent articles found for {country}")
                continue

            result = extract_country_topics(country, articles, target_topics=args.topics)
            if result:
                all_results[country] = result
                save_results({country: result}, f"topics_partial_{country}.json")

        except Exception as e:
            logger.error(f"An error occurred while processing {country}: {e}", exc_info=True)

    save_results(all_results, args.output)
    logger.info("Topic extraction process finished.")

if __name__ == "__main__":
    main()