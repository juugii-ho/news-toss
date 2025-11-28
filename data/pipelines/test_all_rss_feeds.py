"""
RSS Feed Validation Script - ALL FEEDS
전체 52개 언론사 RSS 피드를 모두 테스트
"""

import feedparser
import json
from datetime import datetime
import time

# 레거시 파일에서 가져온 전체 RSS 피드 목록
ALL_RSS_FEEDS = {
    # 🇺🇸 미국 (5개)
    "US": [
        {"name": "New York Times", "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "bias": "PROGRESSIVE"},
        {"name": "Washington Post", "url": "https://feeds.washingtonpost.com/rss/national", "bias": "PROGRESSIVE"},
        {"name": "Fox News", "url": "https://moxie.foxnews.com/google-publisher/latest.xml", "bias": "CONSERVATIVE"},
        {"name": "CNN", "url": "http://rss.cnn.com/rss/edition.rss", "bias": "NEUTRAL"},
        {"name": "The Hill", "url": "https://thehill.com/feed/", "bias": "NEUTRAL"},
    ],
    # 🇬🇧 영국 (6개)
    "GB": [
        {"name": "BBC", "url": "https://feeds.bbci.co.uk/news/rss.xml", "bias": "NEUTRAL"},
        {"name": "The Guardian", "url": "https://www.theguardian.com/uk/rss", "bias": "PROGRESSIVE"},
        {"name": "Financial Times", "url": "https://www.ft.com/rss/home", "bias": "NEUTRAL"},
        {"name": "The Independent", "url": "https://www.independent.co.uk/news/uk/rss", "bias": "PROGRESSIVE"},
        {"name": "Sky News", "url": "https://feeds.skynews.com/feeds/rss/home.xml", "bias": "NEUTRAL"},
        {"name": "The Telegraph", "url": "https://www.telegraph.co.uk/news/rss.xml", "bias": "CONSERVATIVE"},
    ],
    # 🇩🇪 독일 (4개)
    "DE": [
        {"name": "Der Spiegel", "url": "https://www.spiegel.de/schlagzeilen/index.rss", "bias": "PROGRESSIVE"},
        {"name": "FAZ", "url": "https://www.faz.net/rss/aktuell/", "bias": "CONSERVATIVE"},
        {"name": "Süddeutsche Zeitung", "url": "https://rss.sueddeutsche.de/rss/Topthemen", "bias": "PROGRESSIVE"},
        {"name": "Deutsche Welle", "url": "https://rss.dw.com/rdf/rss-en-all", "bias": "NEUTRAL"},
    ],
    # 🇫🇷 프랑스 (4개)
    "FR": [
        {"name": "Le Monde", "url": "http://www.lemonde.fr/rss/une.xml", "bias": "PROGRESSIVE"},
        {"name": "Le Figaro", "url": "https://www.lefigaro.fr/rss/figaro_flash-actu.xml", "bias": "CONSERVATIVE"},
        {"name": "France 24", "url": "https://www.france24.com/en/rss", "bias": "NEUTRAL"},
        {"name": "Mediapart", "url": "https://www.mediapart.fr/articles/feed", "bias": "PROGRESSIVE"},
    ],
    # 🇮🇹 이탈리아 (2개)
    "IT": [
        {"name": "La Repubblica", "url": "https://www.repubblica.it/rss/homepage/rss2.0.xml", "bias": "PROGRESSIVE"},
        {"name": "Corriere della Sera", "url": "https://www.corriere.it/rss/homepage.xml", "bias": "CONSERVATIVE"},
    ],
    # 🇯🇵 일본 (4개)
    "JP": [
        {"name": "Yomiuri Shimbun", "url": "https://japannews.yomiuri.co.jp/feed", "bias": "CONSERVATIVE"},
        {"name": "Nikkei Asia", "url": "https://asia.nikkei.com/rss/feed/nar", "bias": "NEUTRAL"},
        {"name": "NHK", "url": "https://www3.nhk.or.jp/rss/news/cat0.xml", "bias": "NEUTRAL"},
        {"name": "Asahi Shimbun", "url": "https://www.asahi.com/rss/asahi/newsheadlines.rdf", "bias": "PROGRESSIVE"},
    ],
    # 🇰🇷 한국 (5개)
    "KR": [
        {"name": "Google News Korea", "url": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko", "bias": "NEUTRAL"},
        {"name": "SBS", "url": "https://news.sbs.co.kr/news/TopicRssFeed.do?plink=RSSREADER", "bias": "NEUTRAL"},
        {"name": "조선일보", "url": "https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml", "bias": "CONSERVATIVE"},
        {"name": "동아일보", "url": "https://rss.donga.com/total.xml", "bias": "CONSERVATIVE"},
        {"name": "경향신문", "url": "https://www.khan.co.kr/rss/rssdata/total_news.xml", "bias": "PROGRESSIVE"},
    ],
    # 🇨🇦 캐나다 (5개)
    "CA": [
        {"name": "National Post", "url": "https://nationalpost.com/feed", "bias": "CONSERVATIVE"},
        {"name": "CBC", "url": "https://www.cbc.ca/cmlink/rss-topstories", "bias": "NEUTRAL"},
        {"name": "Globe and Mail - Business", "url": "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/", "bias": "NEUTRAL"},
        {"name": "Globe and Mail - Canada", "url": "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/canada/", "bias": "NEUTRAL"},
        {"name": "Globe and Mail - Politics", "url": "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/politics/", "bias": "NEUTRAL"},
    ],
    # 🇦🇺 호주 (3개)
    "AU": [
        {"name": "ABC Australia", "url": "https://www.abc.net.au/news/feed/51120/rss.xml", "bias": "NEUTRAL"},
        {"name": "Sydney Morning Herald", "url": "https://www.smh.com.au/rss/feed.xml", "bias": "PROGRESSIVE"},
        {"name": "The Age", "url": "https://www.theage.com.au/rss/feed.xml", "bias": "PROGRESSIVE"},
    ],
    # 🇧🇪 벨기에 (3개)
    "BE": [
        {"name": "La Libre", "url": "https://www.lalibre.be/rss.xml", "bias": "NEUTRAL"},
        {"name": "RTBF", "url": "https://rss.rtbf.be/article/rss/highlight_rtbf_info.xml?source=internal", "bias": "NEUTRAL"},
        {"name": "Le Soir", "url": "https://www.lesoir.be/rss2/2/cible_principale", "bias": "PROGRESSIVE"},
    ],
    # 🇳🇱 네덜란드 (4개)
    "NL": [
        {"name": "NRC", "url": "https://www.nrc.nl/rss/", "bias": "PROGRESSIVE"},
        {"name": "De Telegraaf", "url": "https://www.telegraaf.nl/rss", "bias": "CONSERVATIVE"},
        {"name": "NOS", "url": "https://feeds.nos.nl/nosnieuwsalgemeen", "bias": "NEUTRAL"},
        {"name": "De Volkskrant", "url": "https://www.volkskrant.nl/voorpagina/rss.xml", "bias": "PROGRESSIVE"},
    ],
    # 🇷🇺 러시아 (4개)
    "RU": [
        {"name": "RT (Russia Today)", "url": "https://www.rt.com/rss/news/", "bias": "CONSERVATIVE"},
        {"name": "TASS", "url": "https://tass.com/rss/v2.xml", "bias": "CONSERVATIVE"},
        {"name": "Kommersant", "url": "https://www.kommersant.ru/RSS/news.xml", "bias": "NEUTRAL"},
        {"name": "Novaya Gazeta", "url": "https://novayagazeta.eu/feed/rss/en", "bias": "PROGRESSIVE"},
    ],
    # 🇨🇳 중국 (2개)
    "CN": [
        {"name": "Xinhua", "url": "http://www.xinhuanet.com/english/rss/chinarss.xml", "bias": "CONSERVATIVE"},
        {"name": "South China Morning Post", "url": "https://www.scmp.com/rss/91/feed", "bias": "NEUTRAL"},
    ],
}


def parse_rss_feed(url, timeout=30):
    """feedparser를 사용하여 RSS 피드 파싱 (30초 타임아웃)"""
    try:
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Feed parsing timeout after {timeout} seconds")
        
        # 타임아웃 설정
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            feed = feedparser.parse(url)
            signal.alarm(0)  # 타임아웃 해제
        except TimeoutError as e:
            return {
                "success": False,
                "error": str(e)
            }
        
        if feed.bozo and not feed.entries:
            return {
                "success": False,
                "error": f"Parsing error: {feed.bozo_exception}"
            }
        
        if not feed.entries:
            return {
                "success": False,
                "error": "No entries found in feed"
            }
        
        # 피드 정보
        feed_title = feed.feed.get('title', 'Unknown Source')
        
        # 첫 번째 엔트리 파싱
        first_entry = feed.entries[0]
        
        # 제목
        title = first_entry.get('title', 'No Title')
        
        # 링크
        link = first_entry.get('link', '')
        
        # 발행일
        published = None
        if hasattr(first_entry, 'published'):
            published = first_entry.published
        elif hasattr(first_entry, 'updated'):
            published = first_entry.updated
        
        # Summary/Description
        summary = None
        summary_length = 0
        has_summary = False
        
        if hasattr(first_entry, 'summary'):
            summary = first_entry.summary
            summary_length = len(summary)
            has_summary = True
        elif hasattr(first_entry, 'description'):
            summary = first_entry.description
            summary_length = len(summary)
            has_summary = True
        elif hasattr(first_entry, 'content'):
            if first_entry.content:
                summary = first_entry.content[0].get('value', '')
                summary_length = len(summary)
                has_summary = True
        
        return {
            "success": True,
            "source_title": feed_title,
            "total_items": len(feed.entries),
            "has_summary": has_summary,
            "summary_length": summary_length,
            "sample_item": {
                "title": title[:100] + "..." if len(title) > 100 else title,
                "link": link[:100] + "..." if len(link) > 100 else link,
                "published_at": published,
                "summary_preview": summary[:100] + "..." if summary and len(summary) > 100 else summary,
                "summary_full_length": summary_length,
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}"
        }


def test_all_feeds():
    """전체 52개 언론사 RSS 피드 테스트"""
    print("=" * 80)
    print("🔍 RSS Feed Validation Test - ALL 52 SOURCES")
    print("=" * 80)
    print()
    
    all_results = {}
    total_feeds = 0
    success_count = 0
    fail_count = 0
    feeds_with_summary = []
    feeds_without_summary = []
    failed_feeds = []
    
    for country_code, feeds in ALL_RSS_FEEDS.items():
        print(f"\n{'='*80}")
        print(f"🌍 {country_code} - Testing {len(feeds)} sources")
        print(f"{'='*80}\n")
        
        country_results = []
        
        for feed_info in feeds:
            total_feeds += 1
            print(f"📰 {feed_info['name']} ({feed_info['bias']})")
            print(f"   URL: {feed_info['url']}")
            
            result = parse_rss_feed(feed_info['url'])
            
            feed_result = {
                "name": feed_info['name'],
                "bias": feed_info['bias'],
                "url": feed_info['url'],
                **result
            }
            
            country_results.append(feed_result)
            
            if result['success']:
                success_count += 1
                print(f"   ✅ SUCCESS - {result['total_items']} items")
                print(f"   📄 Title: {result['sample_item']['title']}")
                
                if result['has_summary']:
                    print(f"   📝 Summary: ✅ YES ({result['summary_length']} chars)")
                    feeds_with_summary.append({
                        'country': country_code,
                        'name': feed_info['name'],
                        'summary_length': result['summary_length']
                    })
                else:
                    print(f"   📝 Summary: ❌ NO")
                    feeds_without_summary.append({
                        'country': country_code,
                        'name': feed_info['name']
                    })
            else:
                fail_count += 1
                print(f"   ❌ FAILED - {result['error']}")
                failed_feeds.append({
                    'country': country_code,
                    'name': feed_info['name'],
                    'error': result['error']
                })
            
            print()
            
            # 서버 부하 방지를 위한 짧은 대기
            time.sleep(0.5)
        
        all_results[country_code] = country_results
    
    # 최종 요약
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    print(f"Total Feeds Tested: {total_feeds}")
    print(f"✅ Success: {success_count}/{total_feeds} ({success_count/total_feeds*100:.1f}%)")
    print(f"❌ Failed: {fail_count}/{total_feeds} ({fail_count/total_feeds*100:.1f}%)")
    print()
    
    # Summary 분석
    print("=" * 80)
    print("📝 Summary Field Analysis")
    print("=" * 80)
    print(f"✅ Feeds WITH summary: {len(feeds_with_summary)}/{success_count} ({len(feeds_with_summary)/success_count*100:.1f}%)")
    print(f"❌ Feeds WITHOUT summary: {len(feeds_without_summary)}/{success_count} ({len(feeds_without_summary)/success_count*100:.1f}%)")
    print()
    
    # 국가별 통계
    print("=" * 80)
    print("🌍 By Country")
    print("=" * 80)
    for country_code, results in all_results.items():
        total = len(results)
        success = sum(1 for r in results if r['success'])
        with_summary = sum(1 for r in results if r.get('success') and r.get('has_summary'))
        print(f"{country_code}: {success}/{total} success, {with_summary}/{success} with summary" if success > 0 else f"{country_code}: {success}/{total} success")
    print()
    
    # 실패한 피드 상세
    if failed_feeds:
        print("=" * 80)
        print("⚠️  Failed Feeds Details")
        print("=" * 80)
        for feed in failed_feeds:
            print(f"❌ {feed['country']} - {feed['name']}")
            print(f"   Error: {feed['error']}")
        print()
    
    # Summary 없는 피드 상세
    if feeds_without_summary:
        print("=" * 80)
        print("📝 Feeds WITHOUT Summary")
        print("=" * 80)
        for feed in feeds_without_summary:
            print(f"- {feed['country']}: {feed['name']}")
        print()
    
    # JSON 저장
    output_file = "rss_feed_test_results_ALL.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_file}")
    print()
    
    return all_results


if __name__ == "__main__":
    test_all_feeds()
