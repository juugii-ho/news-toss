import os
import json
from utils import get_supabase_client, get_logger

# Initialize logger
logger = get_logger(__name__)

# Country Mapping (Emoji/Name -> Code)
COUNTRY_MAP = {
    "🇺🇸 미국": "US", "🇬🇧 영국": "GB", "🇫🇷 프랑스": "FR", "🇩🇪 독일": "DE",
    "🇮🇹 이탈리아": "IT", "🇨🇦 캐나다": "CA", "🇯🇵 일본": "JP", "🇰🇷 대한민국": "KR",
    "🇨🇳 중국": "CN", "🇷🇺 러시아": "RU",
    # Fallbacks
    "미국": "US", "영국": "GB", "프랑스": "FR", "독일": "DE", "이탈리아": "IT",
    "캐나다": "CA", "일본": "JP", "대한민국": "KR", "중국": "CN", "러시아": "RU"
}

def fetch_recent_articles(limit=200):
    """
    Fetches recent articles from the Supabase 'mvp_articles' table.
    """
    logger.info(f"Fetching latest {limit} articles from Supabase 'mvp_articles' table...")
    
    try:
        supabase = get_supabase_client()
        response = supabase.table("mvp_articles").select("*").order("created_at", desc=True).limit(limit).execute()
        
        data = response.data
        logger.info(f"Fetched {len(data)} articles from DB.")
        
        formatted_articles = []
        for row in data:
            country_raw = row.get('country_code', '') # Assuming country_code is now directly available
            country_code = COUNTRY_MAP.get(country_raw, 'XX') # Use .get for safety

            article = {
                "title": row.get('title'),
                "title_kr": row.get('title_kr'),
                "link": row.get('url'),
                "summary": row.get('summary', ''),
                "published": row.get('published_at'),
                "source": row.get('source'),
                "country_code": country_code,
                "original_id": row.get('id')
            }
            formatted_articles.append(article)
            
        return formatted_articles

    except Exception as e:
        logger.error(f"Exception fetching from DB: {e}", exc_info=True)
        return []

def save_articles_to_json(articles, filename="fetched_articles_from_db.json"):
    """Saves a list of articles to a JSON file in the outputs directory."""
    if not articles:
        logger.warning("No articles to save.")
        return

    # ../../outputs/filename
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'outputs'))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    try:
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(articles)} articles to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save articles to JSON: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("Starting script to fetch articles from database...")
    fetched_articles = fetch_recent_articles()
    save_articles_to_json(fetched_articles)
    logger.info("Script finished.")