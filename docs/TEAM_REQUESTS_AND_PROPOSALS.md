# 팀원 간 요청사항 및 개선 제안

**작성일**: 2025-11-28 23:50  
**작성자**: C (Claude Code)

---

## 📬 G (Gemini CLI)에게 요청

### 즉시 필요한 사항

#### 1. RSS 수집 스크립트 개발
**파일**: `data/pipelines/rss_collector.py`

**요청사항**:
```python
# 다음 기능 포함 필요
1. MVP2_news_sources에서 is_active=true인 피드만 조회
2. feedparser 라이브러리 사용 (test_all_rss_feeds.py 참고)
3. 중복 방지: MVP2_articles.url UNIQUE 제약 활용
4. 에러 처리: 개별 피드 실패 시 다른 피드 계속 수집
5. 로깅: 수집 성공/실패 통계
```

**참고 파일**:
- `data/pipelines/test_all_rss_feeds.py` - feedparser 사용 예시
- `docs/RSS_FEED_AND_DATABASE_REPORT.md` - 49개 피드 목록

**출력**:
- MVP2_articles 테이블에 저장
- summary_original 필드에 RSS summary 저장 (있으면)

---

#### 2. LLM 번역/생성 스크립트
**파일**: `data/pipelines/llm_translator.py`

**요청사항**:
```python
# 처리 로직
1. MVP2_articles에서 title_ko IS NULL인 기사 조회
2. 원본 언어 감지 (language 필드 활용)
3. LLM 번역:
   - title_original → title_ko, title_en
   - summary_original → summary_ko, summary_en
4. summary_original이 없으면:
   - title_original 기반으로 summary 생성 (KO/EN)
5. 배치 처리 (20개씩) - 토큰 제한 고려
```

**LLM 모델**: `gemini-2.5-flash` (RULES.md 참고)

**프롬프트 예시 필요**:
- 번역 프롬프트
- Summary 생성 프롬프트

---

#### 3. 스탠스 분석 스크립트
**파일**: `data/pipelines/llm_stance_analyzer.py`

**요청사항**:
```python
# 분석 로직
1. MVP2_articles에서 summary_en이 있는 기사 조회
2. LLM으로 스탠스 분석:
   - SUPPORTIVE / NEUTRAL / CRITICAL
   - confidence_score (0.0-1.0)
   - reasoning (한 줄 설명)
3. MVP2_article_stance 테이블에 저장
```

**프롬프트 설계 시 고려사항**:
- 뉴스 기사의 객관성 vs 주관성 구분
- 정치 성향과 스탠스의 차이 명확화
- Few-shot 예시 포함 권장

---

#### 4. 임베딩 생성 스크립트
**파일**: `data/pipelines/embedding_generator.py`

**요청사항**:
```python
# 임베딩 생성
1. MVP2_articles에서 summary_en이 있는 기사 조회
2. text-embedding-004 모델 사용
3. MVP2_embeddings 테이블에 저장:
   - entity_type: 'article'
   - entity_id: article.id
   - embedding_vector: 768차원 벡터
   - source_text_en: summary_en
```

**성능 고려**:
- 배치 처리 (100개씩 권장)
- API 호출 제한 확인
- 진행 상황 로깅

---

### 의문사항 및 제안

#### 💡 제안 1: 파이프라인 오케스트레이션
**현재**: 각 스크립트를 수동 실행?

**제안**:
```python
# data/pipelines/run_pipeline.py
def run_full_pipeline():
    """전체 파이프라인 실행"""
    1. rss_collector.py
    2. llm_translator.py
    3. llm_stance_analyzer.py
    4. embedding_generator.py
    5. topic_extractor.py (기존 레거시 활용?)
    6. topic_merger.py
```

**장점**:
- 일관된 실행 순서
- 에러 처리 통합
- 로깅 통합

**질문**: Airflow/Prefect 같은 도구 사용 고려하셨나요?

---

#### 💡 제안 2: Summary 생성 전략
**현재 계획**: CNN, Nikkei Asia만 LLM 생성

**의문**:
- 조선일보, Asahi Shimbun도 summary가 비어있음 (0자)
- 이들도 LLM 생성 대상에 포함해야 하지 않나요?

**제안**:
```python
# 조건 수정
if not summary_original or len(summary_original.strip()) == 0:
    # LLM으로 summary 생성
```

---

#### 💡 제안 3: 토픽 추출 로직
**질문**: 레거시 `llm_topic_extractor.py` 재사용 계획인가요?

**확인 필요**:
- MVP1의 토픽 추출 로직이 MVP2 요구사항과 맞는지?
- 5개국 이상 → Global megatopic 기준 유지?

**제안**: 
- 토픽 추출 전에 임베딩 클러스터링 고려
- 유사한 기사들을 먼저 그룹화 후 토픽 추출

---

#### ❓ 질문 1: 데이터 파이프라인 실행 주기
**옵션**:
- A. 1시간마다 (실시간성 높음, API 비용 높음)
- B. 6시간마다 (균형)
- C. 12시간마다 (비용 절감)

**추천**: 초기에는 6시간, 안정화 후 1시간으로 단축

---

#### ❓ 질문 2: 에러 처리 전략
**시나리오**: 특정 언론사 RSS가 일시적으로 다운

**옵션**:
- A. 해당 피드 스킵, 다음 실행 때 재시도
- B. 3회 재시도 후 is_active=false로 변경
- C. 알림 발송 (Slack/Email)

**추천**: A + C (스킵 + 알림)

---

## 📬 O (Codex CLI)에게 요청

### 즉시 필요한 사항

#### 1. API 클라이언트 설정
**파일**: `packages/lib/supabase-client.ts`

**요청사항**:
```typescript
// Supabase 클라이언트 초기화
import { createClient } from '@supabase/supabase-js'
import type { Database } from './database-types'

export const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

**환경변수 필요**:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

---

#### 2. API 라우트 구조
**파일 구조**:
```
app/api/
├── global/
│   ├── insights/
│   │   ├── route.ts          # GET /api/global/insights
│   │   └── [id]/
│   │       └── route.ts      # GET /api/global/insights/{id}
└── local/
    └── trends/
        └── route.ts          # GET /api/local/trends
```

**요청사항**:
- TypeScript 타입 사용 (`database-types.ts` 참고)
- 에러 처리 통일
- 페이지네이션 지원 (local/trends)

---

#### 3. Global Insights API
**파일**: `app/api/global/insights/route.ts`

**요청사항**:
```typescript
// GET /api/global/insights
// 응답: GlobalInsightDetail[] (상위 10개)

// 쿼리:
// 1. MVP2_global_topics (is_pinned=true 우선, rank 순)
// 2. JOIN MVP2_perspectives (국가별 관점)
// 3. JOIN MVP2_countries (국가 정보)

// 정렬: rank ASC, article_count DESC
// 제한: 10개
```

**응답 예시**:
```json
[
  {
    "id": "uuid",
    "title_ko": "트럼프 관세 정책",
    "title_en": "Trump Tariff Policy",
    "intro_ko": "...",
    "intro_en": "...",
    "article_count": 150,
    "country_count": 8,
    "perspectives": [
      {
        "country_code": "US",
        "country_name_ko": "미국",
        "flag_emoji": "🇺🇸",
        "stance": "POSITIVE",
        "one_liner_ko": "경제 회복의 필수 조치",
        "one_liner_en": "Essential for economic recovery"
      }
    ]
  }
]
```

---

#### 4. Local Trends API
**파일**: `app/api/local/trends/route.ts`

**요청사항**:
```typescript
// GET /api/local/trends?country=KR&page=1&limit=20
// 응답: LocalTrendsResponse

// 쿼리:
// 1. MVP2_local_topics (country_code 필터)
// 2. 정렬: article_count DESC, created_at DESC
// 3. 페이지네이션

// display_level 로직:
// - Lv 1: 상위 20% (큰 카드)
// - Lv 2: 중간 30% (중간 카드)
// - Lv 3: 하위 50% (작은 카드)
```

---

### 의문사항 및 제안

#### 💡 제안 1: API 캐싱 전략
**현재**: 매 요청마다 DB 조회?

**제안**:
```typescript
// Next.js App Router의 fetch 캐싱 활용
export const revalidate = 3600 // 1시간

// 또는 Redis 캐싱
import { redis } from '@/lib/redis'

const cached = await redis.get(`global:insights`)
if (cached) return JSON.parse(cached)
```

**장점**:
- API 응답 속도 향상
- DB 부하 감소
- Vercel Edge 활용 가능

---

#### 💡 제안 2: ISR (Incremental Static Regeneration)
**현재 계획**: ISR 1시간 (MEETING_NOTES.md)

**제안**:
```typescript
// app/page.tsx (Global 탭)
export const revalidate = 3600 // 1시간

// app/local/page.tsx (Local 탭)
export const revalidate = 1800 // 30분 (더 자주 업데이트)
```

**이유**: Local 트렌드가 더 빠르게 변화

---

#### 💡 제안 3: 에러 바운더리
**제안**:
```typescript
// app/error.tsx
export default function Error({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div>
      <h2>문제가 발생했습니다</h2>
      <button onClick={reset}>다시 시도</button>
    </div>
  )
}
```

**장점**: 사용자 경험 개선

---

#### ❓ 질문 1: VS 카드 상세 페이지 라우팅
**옵션**:
- A. `/global/[id]` - 단순, SEO 좋음
- B. `/insights/[id]` - 명확
- C. `/vs/[id]` - 브랜딩

**추천**: A (`/global/[id]`)

---

#### ❓ 질문 2: Infinite Scroll vs Pagination
**Local 탭 요구사항**: Infinite Scroll

**질문**: 
- 초기 로드 개수는? (20개? 30개?)
- 스크롤 트리거 위치는? (하단 200px?)
- 로딩 인디케이터 디자인은?

---

## 📬 S (사용자)에게 질문

### 제품 기획 관련

#### ❓ 질문 1: Admin 대시보드 우선순위
**현재 상태**: 설계 단계

**질문**:
- Admin 대시보드가 MVP 출시 전에 필요한가요?
- 아니면 MVP 출시 후 개발해도 되나요?

**Admin 기능 예상**:
- 언론사 관리 (is_active 토글)
- 토픽 수동 편집
- 스탠스 수정
- 통계 대시보드

---

#### ❓ 질문 2: 다국어 지원 범위
**현재**: KO/EN 번역

**질문**:
- UI 언어는 한국어만? 아니면 영어도?
- 기사 원문 언어 표시 필요한가요?
- 번역 품질 표시 (신뢰도) 필요한가요?

---

#### ❓ 질문 3: 미디어 에셋 생성 시점
**현재 스키마**: MVP2_media_assets 테이블 존재

**질문**:
- AI 이미지/비디오 생성은 언제 하나요?
  - A. 토픽 생성 시 자동
  - B. Admin이 수동 트리거
  - C. MVP에서는 제외

**비용 고려**: 이미지 생성 비용이 높을 수 있음

---

#### ❓ 질문 4: 정치 성향 표시
**현재**: 언론사별 정치 성향 분류 완료

**질문**:
- 사용자에게 언론사 정치 성향을 표시하나요?
- 아니면 내부 데이터로만 사용?
- 표시한다면 어떤 형태? (아이콘? 색상? 텍스트?)

---

### 기술적 결정 필요

#### ❓ 질문 5: 배포 환경
**옵션**:
- A. Vercel (Next.js 최적화, 간편)
- B. AWS (유연성, 비용 최적화)
- C. 기타

**현재 가정**: Vercel

---

#### ❓ 질문 6: 모니터링 도구
**필요 항목**:
- 에러 추적 (Sentry?)
- 성능 모니터링 (Vercel Analytics?)
- 사용자 분석 (Google Analytics?)

**질문**: 어떤 도구 사용할까요?

---

## 🔧 개선 제안

### 1. 데이터베이스 스키마 개선

#### 💡 제안: MVP2_articles에 필드 추가
**현재**: `summary_original` 필드만

**제안**:
```sql
ALTER TABLE MVP2_articles ADD COLUMN IF NOT EXISTS
  llm_processing_status VARCHAR(20) CHECK (
    llm_processing_status IN ('pending', 'translating', 'completed', 'failed')
  ) DEFAULT 'pending';

ALTER TABLE MVP2_articles ADD COLUMN IF NOT EXISTS
  llm_processed_at TIMESTAMPTZ;
```

**이유**: 
- 파이프라인 진행 상황 추적
- 실패한 기사 재처리 용이

---

#### 💡 제안: MVP2_news_sources에 통계 필드
**제안**:
```sql
ALTER TABLE MVP2_news_sources ADD COLUMN IF NOT EXISTS
  last_collected_at TIMESTAMPTZ;

ALTER TABLE MVP2_news_sources ADD COLUMN IF NOT EXISTS
  total_articles_collected INTEGER DEFAULT 0;

ALTER TABLE MVP2_news_sources ADD COLUMN IF NOT EXISTS
  last_error TEXT;
```

**이유**:
- 언론사별 수집 현황 파악
- 문제 있는 피드 빠른 식별

---

### 2. 성능 최적화

#### 💡 제안: 복합 인덱스 추가
**현재**: 단일 컬럼 인덱스만

**제안**:
```sql
-- 자주 사용되는 쿼리 패턴
CREATE INDEX IF NOT EXISTS idx_articles_country_published 
  ON MVP2_articles(country_code, published_at DESC);

CREATE INDEX IF NOT EXISTS idx_articles_topic_published 
  ON MVP2_articles(global_topic_id, published_at DESC) 
  WHERE global_topic_id IS NOT NULL;
```

**이유**: 국가별/토픽별 최신 기사 조회 속도 향상

---

### 3. 데이터 품질

#### 💡 제안: 데이터 검증 함수
**파일**: `data/pipelines/data_validator.py`

**기능**:
```python
def validate_article(article):
    """기사 데이터 품질 검증"""
    checks = {
        'has_title': bool(article.title_original),
        'has_url': bool(article.url),
        'url_valid': is_valid_url(article.url),
        'published_date_reasonable': is_recent(article.published_at),
        'summary_length_ok': 10 <= len(article.summary_original or '') <= 5000,
    }
    return all(checks.values()), checks
```

**이유**: 저품질 데이터 사전 차단

---

### 4. 모니터링

#### 💡 제안: 파이프라인 메트릭 수집
**파일**: `data/pipelines/metrics.py`

**수집 항목**:
```python
metrics = {
    'rss_collection': {
        'total_feeds': 49,
        'successful_feeds': 47,
        'failed_feeds': 2,
        'total_articles': 1234,
        'duration_seconds': 45.2,
    },
    'llm_translation': {
        'total_articles': 1234,
        'translated': 1200,
        'failed': 34,
        'avg_time_per_article': 0.5,
    },
    # ...
}
```

**저장**: Supabase 별도 테이블 또는 로그 파일

---

## 📝 우선순위 제안

### P0 (즉시)
1. G: RSS 수집 스크립트
2. G: LLM 번역 스크립트
3. O: API 라우트 기본 구조

### P1 (이번 주)
4. G: 스탠스 분석 스크립트
5. G: 임베딩 생성 스크립트
6. O: Global Insights API 완성
7. O: Local Trends API 완성

### P2 (다음 주)
8. G: 토픽 추출/병합 로직
9. O: 프론트엔드 UI 구현
10. C: API 문서화

---

**작성 완료**: 2025-11-28 23:50  
**다음 액션**: 팀원 피드백 대기
