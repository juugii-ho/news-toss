"""
RSS 테스트 데이터를 Supabase에 업로드하는 스크립트
기존 테스트 결과를 mvp2_articles 테이블에 삽입
"""
import json
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Supabase 클라이언트 초기화
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

def load_test_data():
    """테스트 데이터 로드"""
    with open('rss_feed_test_results_ALL.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_source_id(source_name: str, country_code: str) -> str:
    """언론사 이름으로 source_id 조회"""
    response = supabase.table("mvp2_news_sources").select("id").eq(
        "name", source_name
    ).eq("country_code", country_code).execute()
    
    if response.data:
        return response.data[0]["id"]
    return None

def upload_articles():
    """기사 데이터 업로드"""
    data = load_test_data()
    
    total_uploaded = 0
    total_skipped = 0
    
    for country_code, sources in data.items():
        print(f"\n{'='*60}")
        print(f"Processing {country_code}...")
        print(f"{'='*60}")
        
        for source in sources:
            if not source.get("success"):
                print(f"❌ Skipping {source['name']} (failed)")
                continue
            
            # source_id 조회
            source_id = get_source_id(source["name"], country_code)
            if not source_id:
                print(f"⚠️  Source not found: {source['name']} ({country_code})")
                continue
            
            # 샘플 아이템만 업로드 (전체 RSS 수집은 나중에)
            sample = source.get("sample_item")
            if not sample:
                continue
            
            # 기사 데이터 준비
            article = {
                "url": sample["link"],
                "title_original": sample["title"],
                "summary_original": sample.get("summary_preview", ""),
                "country_code": country_code,
                "source_id": source_id,
                "source_name": source["name"],
                "published_at": sample.get("published_at", datetime.now().isoformat()),
            }
            
            try:
                # 중복 체크 (URL 기준)
                existing = supabase.table("mvp2_articles").select("id").eq(
                    "url", article["url"]
                ).execute()
                
                if existing.data:
                    print(f"⏭️  Already exists: {source['name']}")
                    total_skipped += 1
                    continue
                
                # 삽입
                supabase.table("mvp2_articles").insert(article).execute()
                print(f"✅ Uploaded: {source['name']} - {sample['title'][:50]}...")
                total_uploaded += 1
                
            except Exception as e:
                print(f"❌ Error uploading {source['name']}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Upload Summary")
    print(f"{'='*60}")
    print(f"✅ Uploaded: {total_uploaded}")
    print(f"⏭️  Skipped: {total_skipped}")
    print(f"📊 Total: {total_uploaded + total_skipped}")

if __name__ == "__main__":
    print("🚀 Starting RSS test data upload to Supabase...")
    upload_articles()
    print("\n✅ Upload complete!")
