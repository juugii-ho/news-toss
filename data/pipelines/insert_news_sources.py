#!/usr/bin/env python3
"""
Insert news sources data into mvp2_news_sources
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "..", "..", "backend", ".env")
load_dotenv(env_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("📰 Inserting news sources...")

# Read SQL file
with open("/tmp/insert_news_sources.sql", "r") as f:
    sql_content = f.read()

# Execute via Supabase RPC or manually parse and insert
# Since Supabase doesn't support raw SQL execution easily, we'll insert manually

sources = [
    # US (5)
    {'name': 'New York Times', 'country_code': 'US', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', 'language': 'en'},
    {'name': 'Washington Post', 'country_code': 'US', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://feeds.washingtonpost.com/rss/national', 'language': 'en'},
    {'name': 'Fox News', 'country_code': 'US', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://moxie.foxnews.com/google-publisher/latest.xml', 'language': 'en'},
    {'name': 'CNN', 'country_code': 'US', 'political_bias': 'NEUTRAL', 'rss_url': 'http://rss.cnn.com/rss/edition.rss', 'language': 'en'},
    {'name': 'The Hill', 'country_code': 'US', 'political_bias': 'NEUTRAL', 'rss_url': 'https://thehill.com/feed/', 'language': 'en'},
    # UK (6)
    {'name': 'BBC', 'country_code': 'UK', 'political_bias': 'NEUTRAL', 'rss_url': 'https://feeds.bbci.co.uk/news/rss.xml', 'language': 'en'},
    {'name': 'The Guardian', 'country_code': 'UK', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.theguardian.com/uk/rss', 'language': 'en'},
    {'name': 'Financial Times', 'country_code': 'UK', 'political_bias': 'NEUTRAL', 'rss_url': 'https://www.ft.com/rss/home', 'language': 'en'},
    {'name': 'The Independent', 'country_code': 'UK', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.independent.co.uk/news/uk/rss', 'language': 'en'},
    {'name': 'Sky News', 'country_code': 'UK', 'political_bias': 'NEUTRAL', 'rss_url': 'https://feeds.skynews.com/feeds/rss/home.xml', 'language': 'en'},
    {'name': 'The Telegraph', 'country_code': 'UK', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://www.telegraph.co.uk/news/rss.xml', 'language': 'en'},
    # DE (4)
    {'name': 'Der Spiegel', 'country_code': 'DE', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.spiegel.de/schlagzeilen/index.rss', 'language': 'de'},
    {'name': 'FAZ', 'country_code': 'DE', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://www.faz.net/rss/aktuell/', 'language': 'de'},
    {'name': 'Süddeutsche Zeitung', 'country_code': 'DE', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://rss.sueddeutsche.de/rss/Topthemen', 'language': 'de'},
    {'name': 'Deutsche Welle', 'country_code': 'DE', 'political_bias': 'NEUTRAL', 'rss_url': 'https://rss.dw.com/rdf/rss-en-all', 'language': 'en'},
    # FR (4)
    {'name': 'Le Monde', 'country_code': 'FR', 'political_bias': 'PROGRESSIVE', 'rss_url': 'http://www.lemonde.fr/rss/une.xml', 'language': 'fr'},
    {'name': 'Le Figaro', 'country_code': 'FR', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://www.lefigaro.fr/rss/figaro_flash-actu.xml', 'language': 'fr'},
    {'name': 'France 24', 'country_code': 'FR', 'political_bias': 'NEUTRAL', 'rss_url': 'https://www.france24.com/en/rss', 'language': 'en'},
    {'name': 'Mediapart', 'country_code': 'FR', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.mediapart.fr/articles/feed', 'language': 'fr'},
    # IT (2)
    {'name': 'La Repubblica', 'country_code': 'IT', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.repubblica.it/rss/homepage/rss2.0.xml', 'language': 'it'},
    {'name': 'Corriere della Sera', 'country_code': 'IT', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://www.corriere.it/rss/homepage.xml', 'language': 'it'},
    # JP (4)
    {'name': 'Yomiuri Shimbun', 'country_code': 'JP', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://japannews.yomiuri.co.jp/feed', 'language': 'en'},
    {'name': 'Nikkei Asia', 'country_code': 'JP', 'political_bias': 'NEUTRAL', 'rss_url': 'https://asia.nikkei.com/rss/feed/nar', 'language': 'en'},
    {'name': 'NHK', 'country_code': 'JP', 'political_bias': 'NEUTRAL', 'rss_url': 'https://www3.nhk.or.jp/rss/news/cat0.xml', 'language': 'ja'},
    {'name': 'Asahi Shimbun', 'country_code': 'JP', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.asahi.com/rss/asahi/newsheadlines.rdf', 'language': 'ja'},
    # KR (5)
    {'name': 'Google News Korea', 'country_code': 'KR', 'political_bias': 'NEUTRAL', 'rss_url': 'https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko', 'language': 'ko'},
    {'name': 'SBS', 'country_code': 'KR', 'political_bias': 'NEUTRAL', 'rss_url': 'https://news.sbs.co.kr/news/TopicRssFeed.do?plink=RSSREADER', 'language': 'ko'},
    {'name': '조선일보', 'country_code': 'KR', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml', 'language': 'ko'},
    {'name': '동아일보', 'country_code': 'KR', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://rss.donga.com/total.xml', 'language': 'ko'},
    {'name': '경향신문', 'country_code': 'KR', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.khan.co.kr/rss/rssdata/total_news.xml', 'language': 'ko'},
    # CA (4 active + 1 inactive)
    {'name': 'National Post', 'country_code': 'CA', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://nationalpost.com/feed', 'language': 'en'},
    {'name': 'Globe and Mail - Business', 'country_code': 'CA', 'political_bias': 'NEUTRAL', 'rss_url': 'https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/', 'language': 'en'},
    {'name': 'Globe and Mail - Canada', 'country_code': 'CA', 'political_bias': 'NEUTRAL', 'rss_url': 'https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/canada/', 'language': 'en'},
    {'name': 'Globe and Mail - Politics', 'country_code': 'CA', 'political_bias': 'NEUTRAL', 'rss_url': 'https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/politics/', 'language': 'en'},
    {'name': 'CBC', 'country_code': 'CA', 'political_bias': 'NEUTRAL', 'rss_url': 'https://www.cbc.ca/cmlink/rss-topstories', 'language': 'en', 'is_active': False, 'notes': 'Timeout issue - too slow'},
    # AU (3)
    {'name': 'ABC Australia', 'country_code': 'AU', 'political_bias': 'NEUTRAL', 'rss_url': 'https://www.abc.net.au/news/feed/51120/rss.xml', 'language': 'en'},
    {'name': 'Sydney Morning Herald', 'country_code': 'AU', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.smh.com.au/rss/feed.xml', 'language': 'en'},
    {'name': 'The Age', 'country_code': 'AU', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.theage.com.au/rss/feed.xml', 'language': 'en'},
    # BE (2 active + 1 inactive)
    {'name': 'La Libre', 'country_code': 'BE', 'political_bias': 'NEUTRAL', 'rss_url': 'https://www.lalibre.be/rss.xml', 'language': 'fr'},
    {'name': 'RTBF', 'country_code': 'BE', 'political_bias': 'NEUTRAL', 'rss_url': 'https://rss.rtbf.be/article/rss/highlight_rtbf_info.xml?source=internal', 'language': 'fr'},
    {'name': 'Le Soir', 'country_code': 'BE', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.lesoir.be/rss2/2/cible_principale', 'language': 'fr', 'is_active': False, 'notes': 'Access denied - blocked'},
    # NL (4)
    {'name': 'NRC', 'country_code': 'NL', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.nrc.nl/rss/', 'language': 'nl'},
    {'name': 'De Telegraaf', 'country_code': 'NL', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://www.telegraaf.nl/rss', 'language': 'nl'},
    {'name': 'NOS', 'country_code': 'NL', 'political_bias': 'NEUTRAL', 'rss_url': 'https://feeds.nos.nl/nosnieuwsalgemeen', 'language': 'nl'},
    {'name': 'De Volkskrant', 'country_code': 'NL', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://www.volkskrant.nl/voorpagina/rss.xml', 'language': 'nl'},
    # RU (4)
    {'name': 'RT (Russia Today)', 'country_code': 'RU', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://www.rt.com/rss/news/', 'language': 'en'},
    {'name': 'TASS', 'country_code': 'RU', 'political_bias': 'CONSERVATIVE', 'rss_url': 'https://tass.com/rss/v2.xml', 'language': 'en'},
    {'name': 'Kommersant', 'country_code': 'RU', 'political_bias': 'NEUTRAL', 'rss_url': 'https://www.kommersant.ru/RSS/news.xml', 'language': 'ru'},
    {'name': 'Novaya Gazeta', 'country_code': 'RU', 'political_bias': 'PROGRESSIVE', 'rss_url': 'https://novayagazeta.eu/feed/rss/en', 'language': 'en'},
    # CN (2)
    {'name': 'Xinhua', 'country_code': 'CN', 'political_bias': 'CONSERVATIVE', 'rss_url': 'http://www.xinhuanet.com/english/rss/chinarss.xml', 'language': 'en'},
    {'name': 'South China Morning Post', 'country_code': 'CN', 'political_bias': 'NEUTRAL', 'rss_url': 'https://www.scmp.com/rss/91/feed', 'language': 'en'},
]

try:
    result = supabase.table("mvp2_news_sources").insert(sources).execute()
    print(f"✅ Inserted {len(sources)} news sources successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
