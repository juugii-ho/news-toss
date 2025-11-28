import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time
from utils import get_supabase_client, get_logger

# Initialize logger
logger = get_logger(__name__)

# G10 + Russia + China RSS Feeds
RSS_FEEDS = {
    # ... (rest of the feed list remains the same)
    # 🇺🇸 미국
    "US": [
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://feeds.washingtonpost.com/rss/national",
        "https://moxie.foxnews.com/google-publisher/latest.xml",
        "http://rss.cnn.com/rss/edition.rss",
        "https://thehill.com/feed/"
    ],
    # 🇬🇧 영국
    "GB": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://www.theguardian.com/uk/rss",
        "https://www.ft.com/rss/home",
        "https://www.independent.co.uk/news/uk/rss",
        "https://feeds.skynews.com/feeds/rss/home.xml"
        "https://www.telegraph.co.uk/news/rss.xml"
    ],
    # ... and so on for all other countries
    "DE": ["https://www.spiegel.de/schlagzeilen/index.rss", 
           "https://www.faz.net/rss/aktuell/", 
           "https://rss.sueddeutsche.de/rss/Topthemen", 
           "https://rss.dw.com/rdf/rss-en-all"],
    "FR": ["http://www.lemonde.fr/rss/une.xml", 
           "https://www.lefigaro.fr/rss/figaro_flash-actu.xml", 
           "https://www.france24.com/en/rss", 
           "https://www.mediapart.fr/articles/feed"],
    "IT": ["https://www.repubblica.it/rss/homepage/rss2.0.xml",
           "https://www.corriere.it/rss/homepage.xml"],
    "JP": ["https://japannews.yomiuri.co.jp/feed", 
           "https://asia.nikkei.com/rss/feed/nar", 
           "https://www3.nhk.or.jp/rss/news/cat0.xml",
           "https://www.asahi.com/rss/asahi/newsheadlines.rdf"],
    "KR": ["https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko", 
           "https://news.sbs.co.kr/news/TopicRssFeed.do?plink=RSSREADER", 
           "https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml", 
           "https://rss.donga.com/total.xml", 
           "https://www.khan.co.kr/rss/rssdata/total_news.xml"],
    "CA": ["https://nationalpost.com/feed",
           "https://www.cbc.ca/cmlink/rss-topstories",
           "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/",
           "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/canada/",
           "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/politics/",
           "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/canada/"],
    "AU": ["https://www.abc.net.au/news/feed/51120/rss.xml", 
           "https://www.smh.com.au/rss/feed.xml",
           "https://www.theage.com.au/rss/feed.xml"],
    "BE": ["https://www.lalibre.be/rss.xml",
           "https://rss.rtbf.be/article/rss/highlight_rtbf_info.xml?source=internal",
           "https://www.lesoir.be/rss2/2/cible_principale"],
    "NL": ["https://www.nrc.nl/rss/", 
           "https://www.telegraaf.nl/rss",
           "https://feeds.nos.nl/nosnieuwsalgemeen",
           "https://www.volkskrant.nl/voorpagina/rss.xml"],
    "RU": ["https://www.rt.com/rss/news/", 
           "https://tass.com/rss/v2.xml", 
           "https://www.kommersant.ru/RSS/news.xml", 
           "https://novayagazeta.eu/feed/rss/en"],
    "CN": ["http://www.xinhuanet.com/english/rss/chinarss.xml", 
           "https://www.scmp.com/rss/91/feed",
           ""]
}
# 참고 : Awesome RSS Feeds https://github.com/plenaryapp/awesome-rss-feeds?tab=readme-ov-file#with-category-and-without-category

def parse_rss_feed(url, retries=3):
    """Parses an RSS feed and returns a list of items and the source title."""
    for attempt in range(retries):
        try:
            logger.info(f"Fetching {url} (Attempt {attempt+1})...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            channel = root.find('channel')
            if channel is None:
                channel = root

            source_title = "Unknown Source"
            if channel is not None:
                title_elem = channel.find('title')
                if title_elem is not None and title_elem.text:
                    source_title = title_elem.text
                else:
                    ns_title = channel.find('.//{http://purl.org/rss/1.0/}title')
                    if ns_title is not None and ns_title.text:
                        source_title = ns_title.text

            items = channel.findall('item') if channel is not None else []
            if not items:
                items = root.findall('.//{http://purl.org/rss/1.0/}item')
            if not items:
                items = root.findall('.//item')

            parsed_items = []
            for item in items:
                title = (item.find('title') or item.find('.//{http://purl.org/rss/1.0/}title'))
                title = title.text if title is not None else "No Title"

                link = (item.find('link') or item.find('.//{http://purl.org/rss/1.0/}link'))
                link = link.text if link is not None else ""

                pub_date = (item.find('pubDate') or item.find('.//{http://purl.org/dc/elements/1.1/}date'))
                pub_date = pub_date.text if pub_date is not None else datetime.now().isoformat()
                
                description = (item.find('description') or item.find('.//{http://purl.org/rss/1.0/}description'))
                description = description.text if description is not None else ""

                parsed_items.append({
                    "title": title,
                    "url": link,
                    "published_at": pub_date,
                    "summary": description
                })

            if parsed_items:
                logger.info(f"  ✓ Parsed {len(parsed_items)} items from {source_title}")
            else:
                logger.warning(f"  ⚠ No items found in feed (source: {source_title})")

            return parsed_items, source_title
            
        except Exception as e:
            logger.error(f"  ✗ Error parsing {url}: {type(e).__name__}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error(f"  ✗ Failed after {retries} attempts")
                return [], "Unknown"

def fetch_and_save_feeds():
    """Fetches articles from all RSS feeds and saves them to the database."""
    total_fetched = 0
    supabase = get_supabase_client()
    
    for country, urls in RSS_FEEDS.items():
        for url in urls:
            items, source = parse_rss_feed(url)
            if not items:
                continue
                
            batch_dict = {}
            for item in items:
                if not item.get('url') or not item.get('title'):
                    continue
                
                item_url = item['url'].strip()
                if item_url not in batch_dict:
                    batch_dict[item_url] = {
                        "url": item_url,
                        "title": item['title'].strip(),
                        "source": source,
                        "country_code": country,
                        "published_at": item['published_at'],
                        "summary": item.get('summary', '')
                    }

            batch_data = list(batch_dict.values())

            if batch_data:
                try:
                    response = supabase.table("mvp_articles").upsert(batch_data, on_conflict="url").execute()
                    count = len(batch_data)
                    total_fetched += count
                    logger.info(f"  -> Upserted {count} articles from {source}")
                except Exception as e:
                    logger.error(f"  -> Error upserting batch for {source}: {e}")
                    
    logger.info(f"Total articles processed: {total_fetched}")

if __name__ == "__main__":
    logger.info("Starting RSS feed fetching process...")
    fetch_and_save_feeds()
    logger.info("RSS feed fetching process finished.")