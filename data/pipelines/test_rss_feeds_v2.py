"""
RSS Feed Validation Script v2
- 각 국가별로 1개 언론사씩 RSS 피드를 테스트
- summary/description 필드가 있는 피드를 모두 기록
- feedparser 라이브러리 사용으로 파싱 개선
"""

import feedparser
import json
from datetime import datetime

# 각 국가별 1개 언론사만 테스트 (대표 언론사)
TEST_FEEDS = {
    "US": {
        "name": "CNN",
        "url": "http://rss.cnn.com/rss/edition.rss",
        "bias": "NEUTRAL"
    },
    "GB": {
        "name": "BBC",
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "bias": "NEUTRAL"
    },
    "DE": {
        "name": "Deutsche Welle",
        "url": "https://rss.dw.com/rdf/rss-en-all",
        "bias": "NEUTRAL"
    },
    "FR": {
        "name": "France 24",
        "url": "https://www.france24.com/en/rss",
        "bias": "NEUTRAL"
    },
    "IT": {
        "name": "La Repubblica",
        "url": "https://www.repubblica.it/rss/homepage/rss2.0.xml",
        "bias": "PROGRESSIVE"
    },
    "JP": {
        "name": "NHK",
        "url": "https://www3.nhk.or.jp/rss/news/cat0.xml",
        "bias": "NEUTRAL"
    },
    "KR": {
        "name": "조선일보",
        "url": "https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml",
        "bias": "CONSERVATIVE"
    },
    "CA": {
        "name": "CBC",
        "url": "https://www.cbc.ca/cmlink/rss-topstories",
        "bias": "NEUTRAL"
    },
    "AU": {
        "name": "ABC Australia",
        "url": "https://www.abc.net.au/news/feed/51120/rss.xml",
        "bias": "NEUTRAL"
    },
    "BE": {
        "name": "RTBF",
        "url": "https://rss.rtbf.be/article/rss/highlight_rtbf_info.xml?source=internal",
        "bias": "NEUTRAL"
    },
    "NL": {
        "name": "NOS",
        "url": "https://feeds.nos.nl/nosnieuwsalgemeen",
        "bias": "NEUTRAL"
    },
    "RU": {
        "name": "RT (Russia Today)",
        "url": "https://www.rt.com/rss/news/",
        "bias": "CONSERVATIVE"
    },
    "CN": {
        "name": "South China Morning Post",
        "url": "https://www.scmp.com/rss/91/feed",
        "bias": "NEUTRAL"
    }
}


def parse_rss_feed_v2(url, timeout=30):
    """feedparser를 사용하여 RSS 피드 파싱"""
    try:
        print(f"  📡 Fetching feed with feedparser...")
        
        # feedparser 사용 (모든 RSS/Atom 형식 자동 처리)
        feed = feedparser.parse(url)
        
        if feed.bozo:
            # 파싱 에러가 있지만 일부 데이터는 있을 수 있음
            print(f"  ⚠️  Warning: Feed has parsing issues - {feed.bozo_exception}")
        
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
        
        # 발행일 (여러 형식 시도)
        published = None
        if hasattr(first_entry, 'published'):
            published = first_entry.published
        elif hasattr(first_entry, 'updated'):
            published = first_entry.updated
        
        # Summary/Description (여러 필드 시도)
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
        
        # 카테고리
        categories = []
        if hasattr(first_entry, 'tags'):
            categories = [tag.get('term', '') for tag in first_entry.tags]
        
        # 작성자
        author = first_entry.get('author', None)
        
        # 미디어 (이미지/비디오)
        media = []
        if hasattr(first_entry, 'media_content'):
            for m in first_entry.media_content:
                media.append({
                    'url': m.get('url', ''),
                    'type': m.get('type', ''),
                    'medium': m.get('medium', '')
                })
        
        return {
            "success": True,
            "source_title": feed_title,
            "total_items": len(feed.entries),
            "has_summary": has_summary,
            "summary_length": summary_length,
            "sample_item": {
                "title": title[:100] + "..." if len(title) > 100 else title,
                "link": link,
                "published_at": published,
                "summary": summary[:200] + "..." if summary and len(summary) > 200 else summary,
                "summary_full_length": summary_length,
                "categories": categories,
                "author": author,
                "media": media[:2] if media else []  # 처음 2개만
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {type(e).__name__}: {str(e)}"
        }


def test_all_feeds_v2():
    """모든 테스트 피드를 검증 (v2)"""
    print("=" * 80)
    print("🔍 RSS Feed Validation Test v2 (with feedparser)")
    print("=" * 80)
    print()
    
    results = {}
    success_count = 0
    fail_count = 0
    feeds_with_summary = []
    feeds_without_summary = []
    
    for country_code, feed_info in TEST_FEEDS.items():
        print(f"🌍 {country_code} - {feed_info['name']} ({feed_info['bias']})")
        print(f"   URL: {feed_info['url']}")
        
        result = parse_rss_feed_v2(feed_info['url'])
        results[country_code] = {
            "name": feed_info['name'],
            "bias": feed_info['bias'],
            "url": feed_info['url'],
            **result
        }
        
        if result['success']:
            success_count += 1
            print(f"   ✅ SUCCESS - {result['total_items']} items found")
            print(f"   📰 Source: {result['source_title']}")
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
            
            if result['sample_item']['published_at']:
                print(f"   📅 Published: {result['sample_item']['published_at']}")
            
            if result['sample_item']['media']:
                print(f"   🖼️  Media: {len(result['sample_item']['media'])} items")
        else:
            fail_count += 1
            print(f"   ❌ FAILED - {result['error']}")
        
        print()
    
    # 요약
    print("=" * 80)
    print("📊 Summary")
    print("=" * 80)
    print(f"✅ Success: {success_count}/{len(TEST_FEEDS)}")
    print(f"❌ Failed: {fail_count}/{len(TEST_FEEDS)}")
    print()
    
    # Summary 필드 분석
    print("=" * 80)
    print("📝 Summary Field Analysis")
    print("=" * 80)
    print(f"✅ Feeds WITH summary: {len(feeds_with_summary)}/{success_count}")
    for feed in feeds_with_summary:
        print(f"   - {feed['country']}: {feed['name']} ({feed['summary_length']} chars)")
    print()
    
    print(f"❌ Feeds WITHOUT summary: {len(feeds_without_summary)}/{success_count}")
    for feed in feeds_without_summary:
        print(f"   - {feed['country']}: {feed['name']}")
    print()
    
    # 실패한 피드 목록
    if fail_count > 0:
        print("⚠️  Failed Feeds:")
        for country_code, result in results.items():
            if not result['success']:
                print(f"   - {country_code}: {result['name']}")
                print(f"     Error: {result['error']}")
        print()
    
    # JSON 파일로 저장
    output_file = "rss_feed_test_results_v2.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_file}")
    print()
    
    return results


if __name__ == "__main__":
    test_all_feeds_v2()
