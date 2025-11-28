"""
France 24 단독 테스트 - XML 파싱 에러 확인
"""

import feedparser

url = "https://www.france24.com/en/rss"

print("Testing France 24 RSS feed...")
print(f"URL: {url}\n")

feed = feedparser.parse(url)

print(f"Feed parsed: {not feed.bozo}")
print(f"Bozo exception: {feed.bozo_exception if feed.bozo else 'None'}")
print(f"Total entries: {len(feed.entries)}")

if feed.entries:
    first = feed.entries[0]
    print(f"\nFirst entry:")
    print(f"  Title: {first.get('title', 'N/A')}")
    print(f"  Link: {first.get('link', 'N/A')}")
    print(f"  Published: {first.get('published', 'N/A')}")
    
    # Summary 확인
    summary = None
    if hasattr(first, 'summary'):
        summary = first.summary
    elif hasattr(first, 'description'):
        summary = first.description
    
    if summary:
        print(f"  Summary: {summary[:100]}...")
        print(f"  Summary length: {len(summary)}")
    else:
        print(f"  Summary: None")
