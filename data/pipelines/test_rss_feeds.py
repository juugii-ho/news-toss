"""
RSS Feed Validation Script
각 국가별로 1개 언론사씩 RSS 피드를 테스트하여 정상 작동 여부 및 데이터 형태 확인
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json

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


def parse_rss_feed(url, timeout=30):
    """RSS 피드를 파싱하여 첫 번째 아이템의 구조를 반환"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        print(f"  📡 Fetching feed...")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # XML 파싱
        root = ET.fromstring(response.content)
        
        # channel 찾기 (RSS 2.0)
        channel = root.find('channel')
        if channel is None:
            # RSS 1.0 또는 Atom 형식일 수 있음
            channel = root
        
        # 소스 제목 추출
        source_title = "Unknown Source"
        if channel is not None:
            title_elem = channel.find('title')
            if title_elem is not None and title_elem.text:
                source_title = title_elem.text
            else:
                # RSS 1.0 네임스페이스
                ns_title = channel.find('.//{http://purl.org/rss/1.0/}title')
                if ns_title is not None and ns_title.text:
                    source_title = ns_title.text
        
        # 아이템 찾기
        items = channel.findall('item') if channel is not None else []
        if not items:
            items = root.findall('.//{http://purl.org/rss/1.0/}item')
        if not items:
            items = root.findall('.//item')
        
        if not items:
            return {
                "success": False,
                "error": "No items found in feed",
                "source_title": source_title,
                "total_items": 0
            }
        
        # 첫 번째 아이템 파싱
        first_item = items[0]
        
        # 제목
        title = (first_item.find('title') or first_item.find('.//{http://purl.org/rss/1.0/}title'))
        title = title.text if title is not None else "No Title"
        
        # 링크
        link = (first_item.find('link') or first_item.find('.//{http://purl.org/rss/1.0/}link'))
        link = link.text if link is not None else ""
        
        # 발행일
        pub_date = (first_item.find('pubDate') or first_item.find('.//{http://purl.org/dc/elements/1.1/}date'))
        pub_date = pub_date.text if pub_date is not None else None
        
        # 설명/요약
        description = (first_item.find('description') or first_item.find('.//{http://purl.org/rss/1.0/}description'))
        description = description.text if description is not None else ""
        
        # 카테고리
        categories = [cat.text for cat in first_item.findall('category') if cat.text]
        
        # 작성자
        author = first_item.find('author')
        author = author.text if author is not None else None
        
        return {
            "success": True,
            "source_title": source_title,
            "total_items": len(items),
            "sample_item": {
                "title": title[:100] + "..." if len(title) > 100 else title,
                "link": link,
                "published_at": pub_date,
                "description": description[:150] + "..." if description and len(description) > 150 else description,
                "categories": categories,
                "author": author
            }
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout (30s)"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request error: {type(e).__name__}: {str(e)}"
        }
    except ET.ParseError as e:
        return {
            "success": False,
            "error": f"XML parsing error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {type(e).__name__}: {str(e)}"
        }


def test_all_feeds():
    """모든 테스트 피드를 검증"""
    print("=" * 80)
    print("🔍 RSS Feed Validation Test")
    print("=" * 80)
    print()
    
    results = {}
    success_count = 0
    fail_count = 0
    
    for country_code, feed_info in TEST_FEEDS.items():
        print(f"🌍 {country_code} - {feed_info['name']} ({feed_info['bias']})")
        print(f"   URL: {feed_info['url']}")
        
        result = parse_rss_feed(feed_info['url'])
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
            print(f"   📄 Sample Title: {result['sample_item']['title']}")
            if result['sample_item']['published_at']:
                print(f"   📅 Published: {result['sample_item']['published_at']}")
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
    
    # 실패한 피드 목록
    if fail_count > 0:
        print("⚠️  Failed Feeds:")
        for country_code, result in results.items():
            if not result['success']:
                print(f"   - {country_code}: {result['name']}")
                print(f"     Error: {result['error']}")
        print()
    
    # JSON 파일로 저장
    output_file = "rss_feed_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_file}")
    print()
    
    return results


if __name__ == "__main__":
    test_all_feeds()
