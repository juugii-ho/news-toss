import os
import time
import feedparser
import signal
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from dotenv import load_dotenv
from supabase import create_client, Client
from bs4 import BeautifulSoup

# Load environment variables
# Go up 4 levels: data/pipelines/github -> data/pipelines -> data -> root -> backend
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
env_path = os.path.join(project_root, 'backend', '.env')
load_dotenv(env_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase environment variables not found.")
    print("Please ensure NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY are set.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def parse_rss_feed(url, timeout=30):
    """Parse RSS feed with timeout"""
    try:
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Feed parsing timeout after {timeout} seconds")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            feed = feedparser.parse(url)
            signal.alarm(0)
        except TimeoutError as e:
            return {"success": False, "error": str(e)}
        
        if feed.bozo and not feed.entries:
            return {"success": False, "error": f"Parsing error: {feed.bozo_exception}"}
        
        if not feed.entries:
            return {"success": False, "error": "No entries found in feed"}
            
        return {"success": True, "feed": feed}
        
    except Exception as e:
        return {"success": False, "error": f"{type(e).__name__}: {str(e)}"}

def parse_date(date_str):
    """Parse date string to ISO format"""
    if not date_str:
        return datetime.now().isoformat()
    try:
        dt = date_parser.parse(date_str)
        return dt.isoformat()
    except:
        return datetime.now().isoformat()

def get_summary(entry):
    """Extract summary from entry"""
    if hasattr(entry, 'summary'):
        return entry.summary
    elif hasattr(entry, 'description'):
        return entry.description
    elif hasattr(entry, 'content') and entry.content:
        return entry.content[0].get('value', '')
    return None

def main():
    print("Starting RSS Collection (GitHub Actions Mode)...")
    
    # 1. Fetch active news sources
    try:
        response = supabase.table("mvp2_news_sources").select("*").eq("is_active", True).execute()
        sources = response.data
        print(f"Found {len(sources)} active news sources.")
    except Exception as e:
        print(f"Error fetching sources: {e}")
        return

    total_articles = 0
    new_articles = 0
    
    for source in sources:
        print(f"\nProcessing {source['name']} ({source['country_code']})...")
        result = parse_rss_feed(source['rss_url'])
        
        if not result['success']:
            print(f"  Failed: {result['error']}")
            continue
            
        feed = result['feed']
        entries = feed.entries
        print(f"  Found {len(entries)} entries.")
        
        source_articles = []
        for entry in entries:
            # Basic validation
            if not hasattr(entry, 'link') or not hasattr(entry, 'title'):
                continue
                
            published_at = parse_date(entry.get('published', entry.get('updated')))
            
            raw_summary = get_summary(entry)
            clean_summary = None
            if raw_summary:
                # Clean HTML
                soup = BeautifulSoup(raw_summary, "html.parser")
                clean_summary = soup.get_text(separator=" ", strip=True)
            
            article = {
                "url": entry.link,
                "title_original": entry.title,
                "title_ko": entry.title if source.get('language') == 'ko' else None,
                "title_en": entry.title if source.get('language') == 'en' else None,
                "summary_original": clean_summary, # Store cleaned original summary
                "summary_ko": clean_summary if source.get('language') == 'ko' else None,
                "summary_en": clean_summary if source.get('language') == 'en' else None,
                "country_code": source['country_code'],
                "source_id": source['id'],
                "source_name": source['name'],
                "published_at": published_at,
                "collected_at": datetime.now().isoformat()
            }
            source_articles.append(article)
            
        # Batch insert (upsert to handle duplicates)
        unique_articles = {}
        for article in source_articles:
            if article['url'] not in unique_articles:
                unique_articles[article['url']] = article
        
        final_batch = list(unique_articles.values())
        
        if final_batch:
            try:
                # Upsert to DB
                data = supabase.table("mvp2_articles").upsert(
                    final_batch, 
                    on_conflict="url",
                    ignore_duplicates=True
                ).execute()
                
                print(f"  Saved {len(final_batch)} articles.")
                new_articles += len(final_batch)
                total_articles += len(final_batch)
            except Exception as e:
                print(f"  Error inserting articles: {e}")
                # Fallback: Insert one by one if batch fails
                print("  Retrying one by one...")
                for article in final_batch:
                    try:
                        supabase.table("mvp2_articles").upsert(
                            article, 
                            on_conflict="url",
                            ignore_duplicates=True
                        ).execute()
                    except Exception as inner_e:
                        pass # Ignore individual errors
        
        time.sleep(0.5) # Be nice to RSS servers

    print(f"\nRSS Collection Complete. Processed {total_articles} articles total.")

if __name__ == "__main__":
    main()
