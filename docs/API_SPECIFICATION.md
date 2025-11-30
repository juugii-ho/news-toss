# API 명세서 - News Spectrum MVP2

**작성일**: 2025-11-28  
**작성자**: C (Claude Code)  
**버전**: 1.0

---

## 📋 개요

### Base URL
- **Development**: `http://localhost:3000`
- **Production**: `https://newsspectrum.vercel.app` (예시)

### 인증
- 현재 MVP에서는 인증 불필요
- Supabase Anon Key 사용 (Row Level Security 미적용)

---

## 🌍 1. Global Insights API

### GET /api/global/insights

**설명**: 글로벌 인사이트 Top 10 목록 조회

**응답 타입**: `GlobalInsightDetail[]`

#### Request
```
GET /api/global/insights
```

**Query Parameters**: 없음

#### Response (200 OK)
```typescript
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title_ko": "트럼프 관세 정책",
    "title_en": "Trump Tariff Policy",
    "intro_ko": "미국 트럼프 대통령의 새로운 관세 정책이 전 세계 경제에 미치는 영향",
    "intro_en": "Impact of President Trump's new tariff policy on global economy",
    "article_count": 150,
    "country_count": 8,
    "perspectives": [
      {
        "country_code": "US",
        "country_name_ko": "미국",
        "country_name_en": "United States",
        "flag_emoji": "🇺🇸",
        "stance": "POSITIVE",
        "one_liner_ko": "경제 회복의 필수 조치",
        "one_liner_en": "Essential for economic recovery",
        "source_link": "https://example.com/article"
      },
      {
        "country_code": "CN",
        "country_name_ko": "중국",
        "country_name_en": "China",
        "flag_emoji": "🇨🇳",
        "stance": "NEGATIVE",
        "one_liner_ko": "무역 전쟁의 시작",
        "one_liner_en": "Beginning of trade war",
        "source_link": "https://example.com/article"
      }
    ]
  }
]
```

#### Supabase Query
```typescript
const { data, error } = await supabase
  .from('MVP2_global_topics')
  .select(`
    id,
    title_ko,
    title_en,
    intro_ko,
    intro_en,
    article_count,
    country_count,
    perspectives:MVP2_perspectives(
      country_code,
      stance,
      one_liner_ko,
      one_liner_en,
      source_link,
      country:MVP2_countries(
        name_ko,
        name_en,
        flag_emoji
      )
    )
  `)
  .order('rank', { ascending: true, nullsLast: true })
  .order('article_count', { ascending: false })
  .limit(10);
```

#### 에러 응답
```json
{
  "error": "Internal Server Error",
  "message": "Failed to fetch global insights"
}
```

---

### GET /api/global/insights/[id]

**설명**: 특정 글로벌 인사이트 상세 조회 (VS 카드)

**응답 타입**: `GlobalInsightDetail`

#### Request
```
GET /api/global/insights/550e8400-e29b-41d4-a716-446655440000
```

**Path Parameters**:
- `id` (UUID): Global topic ID

#### Response (200 OK)
```typescript
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title_ko": "트럼프 관세 정책",
  "title_en": "Trump Tariff Policy",
  "intro_ko": "미국 트럼프 대통령의 새로운 관세 정책이 전 세계 경제에 미치는 영향",
  "intro_en": "Impact of President Trump's new tariff policy on global economy",
  "article_count": 150,
  "country_count": 8,
  "perspectives": [
    // ... 국가별 관점 배열
  ]
}
```

#### Supabase Query
```typescript
const { data, error } = await supabase
  .from('MVP2_global_topics')
  .select(`
    id,
    title_ko,
    title_en,
    intro_ko,
    intro_en,
    article_count,
    country_count,
    perspectives:MVP2_perspectives(
      country_code,
      stance,
      one_liner_ko,
      one_liner_en,
      source_link,
      country:MVP2_countries(
        name_ko,
        name_en,
        flag_emoji
      )
    )
  `)
  .eq('id', id)
  .single();
```

#### 에러 응답 (404)
```json
{
  "error": "Not Found",
  "message": "Global insight not found"
}
```

---

## 🏠 2. Local Trends API

### GET /api/local/trends

**설명**: 국가별 트렌드 토픽 목록 조회 (Mosaic 레이아웃)

**응답 타입**: `LocalTrendsResponse`

#### Request
```
GET /api/local/trends?country=KR&page=1&limit=20
```

**Query Parameters**:
- `country` (required, string): 국가 코드 (예: KR, US, GB)
- `page` (optional, number): 페이지 번호 (기본값: 1)
- `limit` (optional, number): 페이지당 항목 수 (기본값: 20, 최대: 50)

#### Response (200 OK)
```typescript
{
  "country_code": "KR",
  "country_name_ko": "한국",
  "country_name_en": "South Korea",
  "topics": [
    {
      "topic_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "윤석열 대통령 계엄령 선포",
      "keyword": "계엄령",
      "article_count": 45,
      "display_level": 1,
      "media_type": "image",
      "media_url": "https://example.com/image.jpg"
    },
    {
      "topic_id": "660e8400-e29b-41d4-a716-446655440002",
      "title": "삼성전자 신제품 발표",
      "keyword": "삼성",
      "article_count": 32,
      "display_level": 2,
      "media_type": null,
      "media_url": null
    }
  ],
  "page": 1,
  "total_count": 156
}
```

#### Display Level 로직
```typescript
// article_count 기준 분위수 계산
const topics = await supabase
  .from('MVP2_local_topics')
  .select('*')
  .eq('country_code', country)
  .order('article_count', { ascending: false });

// 상위 20%: Lv 1 (큰 카드)
// 중간 30%: Lv 2 (중간 카드)
// 하위 50%: Lv 3 (작은 카드)

const total = topics.length;
const lv1Threshold = Math.floor(total * 0.2);
const lv2Threshold = Math.floor(total * 0.5);

topics.forEach((topic, index) => {
  if (index < lv1Threshold) topic.display_level = 1;
  else if (index < lv2Threshold) topic.display_level = 2;
  else topic.display_level = 3;
});
```

#### Supabase Query
```typescript
const { data: topics, error, count } = await supabase
  .from('MVP2_local_topics')
  .select('*', { count: 'exact' })
  .eq('country_code', country)
  .order('article_count', { ascending: false })
  .order('created_at', { ascending: false })
  .range((page - 1) * limit, page * limit - 1);

const { data: countryData } = await supabase
  .from('MVP2_countries')
  .select('name_ko, name_en')
  .eq('code', country)
  .single();
```

#### 에러 응답 (400)
```json
{
  "error": "Bad Request",
  "message": "Invalid country code"
}
```

---

## 🗺️ 3. Supabase 테이블 ↔ API 필드 매핑

### Global Insights 매핑

| API 필드 | Supabase 테이블 | 컬럼 | 비고 |
|----------|-----------------|------|------|
| `id` | MVP2_global_topics | id | UUID |
| `title_ko` | MVP2_global_topics | title_ko | |
| `title_en` | MVP2_global_topics | title_en | |
| `intro_ko` | MVP2_global_topics | intro_ko | |
| `intro_en` | MVP2_global_topics | intro_en | |
| `article_count` | MVP2_global_topics | article_count | |
| `country_count` | MVP2_global_topics | country_count | |
| `perspectives[]` | MVP2_perspectives | - | JOIN |
| `perspectives[].country_code` | MVP2_perspectives | country_code | |
| `perspectives[].stance` | MVP2_perspectives | stance | POSITIVE/NEGATIVE/NEUTRAL |
| `perspectives[].one_liner_ko` | MVP2_perspectives | one_liner_ko | |
| `perspectives[].one_liner_en` | MVP2_perspectives | one_liner_en | |
| `perspectives[].source_link` | MVP2_perspectives | source_link | nullable |
| `perspectives[].country_name_ko` | MVP2_countries | name_ko | JOIN |
| `perspectives[].country_name_en` | MVP2_countries | name_en | JOIN |
| `perspectives[].flag_emoji` | MVP2_countries | flag_emoji | JOIN |

### Local Trends 매핑

| API 필드 | Supabase 테이블 | 컬럼 | 비고 |
|----------|-----------------|------|------|
| `country_code` | MVP2_countries | code | |
| `country_name_ko` | MVP2_countries | name_ko | |
| `country_name_en` | MVP2_countries | name_en | |
| `topics[]` | MVP2_local_topics | - | |
| `topics[].topic_id` | MVP2_local_topics | id | |
| `topics[].title` | MVP2_local_topics | title | |
| `topics[].keyword` | MVP2_local_topics | keyword | nullable |
| `topics[].article_count` | MVP2_local_topics | article_count | |
| `topics[].display_level` | MVP2_local_topics | display_level | 1/2/3 (계산됨) |
| `topics[].media_type` | MVP2_local_topics | media_type | nullable |
| `topics[].media_url` | MVP2_local_topics | media_url | nullable |
| `page` | - | - | Query param |
| `total_count` | - | - | COUNT(*) |

---

## 🔧 4. 구현 가이드

### 4.1 Supabase 클라이언트 설정

**파일**: `packages/lib/supabase-client.ts`

```typescript
import { createClient } from '@supabase/supabase-js'
import type { Database } from './database-types'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey)
```

**환경변수** (`.env.local`):
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

---

### 4.2 API Route 예시

**파일**: `app/api/global/insights/route.ts`

```typescript
import { NextResponse } from 'next/server'
import { supabase } from '@/packages/lib/supabase-client'
import type { GlobalInsightDetail } from '@/packages/lib/database-types'

export const revalidate = 3600 // 1시간 ISR

export async function GET() {
  try {
    const { data, error } = await supabase
      .from('MVP2_global_topics')
      .select(`
        id,
        title_ko,
        title_en,
        intro_ko,
        intro_en,
        article_count,
        country_count,
        perspectives:MVP2_perspectives(
          country_code,
          stance,
          one_liner_ko,
          one_liner_en,
          source_link,
          country:MVP2_countries(
            name_ko,
            name_en,
            flag_emoji
          )
        )
      `)
      .order('rank', { ascending: true, nullsLast: true })
      .order('article_count', { ascending: false })
      .limit(10)

    if (error) throw error

    // 데이터 변환
    const insights: GlobalInsightDetail[] = data.map(topic => ({
      id: topic.id,
      title_ko: topic.title_ko,
      title_en: topic.title_en,
      intro_ko: topic.intro_ko || '',
      intro_en: topic.intro_en || '',
      article_count: topic.article_count,
      country_count: topic.country_count,
      perspectives: topic.perspectives.map(p => ({
        country_code: p.country_code,
        country_name_ko: p.country.name_ko,
        country_name_en: p.country.name_en,
        flag_emoji: p.country.flag_emoji,
        stance: p.stance,
        one_liner_ko: p.one_liner_ko,
        one_liner_en: p.one_liner_en,
        source_link: p.source_link,
      })),
    }))

    return NextResponse.json(insights)
  } catch (error) {
    console.error('Error fetching global insights:', error)
    return NextResponse.json(
      { error: 'Internal Server Error', message: 'Failed to fetch global insights' },
      { status: 500 }
    )
  }
}
```

---

### 4.3 캐싱 전략

#### Next.js Fetch 캐싱
```typescript
// 자동 캐싱 (App Router)
export const revalidate = 3600 // 1시간
```

#### React Query (선택사항)
```typescript
// app/providers.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 60, // 1시간
      cacheTime: 1000 * 60 * 60 * 2, // 2시간
    },
  },
})
```

---

### 4.4 라우팅 구조

```
app/
├── page.tsx                    # Global 탭 (/)
├── global/
│   └── [id]/
│       └── page.tsx           # VS 카드 상세 (/global/:id)
├── local/
│   └── page.tsx               # Local 탭 (/local)
└── api/
    ├── global/
    │   └── insights/
    │       ├── route.ts       # GET /api/global/insights
    │       └── [id]/
    │           └── route.ts   # GET /api/global/insights/:id
    └── local/
        └── trends/
            └── route.ts       # GET /api/local/trends
```

---

### 4.5 스크롤 복원

**문제**: 목록 → 상세 → 뒤로가기 시 스크롤 위치 복원

**해결책**:
```typescript
// app/global/[id]/page.tsx
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function GlobalDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()

  useEffect(() => {
    // 뒤로가기 시 스크롤 위치 복원
    const scrollPos = sessionStorage.getItem('global-scroll-pos')
    if (scrollPos) {
      window.scrollTo(0, parseInt(scrollPos))
      sessionStorage.removeItem('global-scroll-pos')
    }
  }, [])

  const handleBack = () => {
    // 현재 스크롤 위치 저장
    sessionStorage.setItem('global-scroll-pos', window.scrollY.toString())
    router.back()
  }

  return (
    <div>
      <button onClick={handleBack}>뒤로가기</button>
      {/* ... */}
    </div>
  )
}
```

---

## 📊 5. 성능 최적화

### 5.1 데이터베이스 인덱스
이미 생성됨:
- `idx_global_topics_rank`
- `idx_perspectives_topic`
- `idx_local_topics_country`
- `idx_local_topics_count`

### 5.2 API 응답 시간 목표
- Global Insights: < 500ms
- Global Detail: < 300ms
- Local Trends: < 400ms

### 5.3 페이지네이션 최적화
```typescript
// Cursor-based pagination (선택사항)
const { data } = await supabase
  .from('MVP2_local_topics')
  .select('*')
  .eq('country_code', country)
  .gt('id', cursor) // cursor 이후 데이터만
  .limit(20)
```

---

## 🧪 6. 테스트

### 6.1 API 테스트
```bash
# Global Insights
curl http://localhost:3000/api/global/insights

# Global Detail
curl http://localhost:3000/api/global/insights/550e8400-e29b-41d4-a716-446655440000

# Local Trends
curl "http://localhost:3000/api/local/trends?country=KR&page=1&limit=20"
```

### 6.2 타입 검증
```typescript
import type { GlobalInsightDetail, LocalTrendsResponse } from '@/packages/lib/database-types'

// 컴파일 시 타입 체크
const insights: GlobalInsightDetail[] = await fetchGlobalInsights()
```

---

**작성 완료**: 2025-11-28 23:52  
**다음 단계**: O가 API 구현 시작

---

### GET /api/local/topics/[id]

**설명**: 특정 로컬 토픽의 상세 정보 및 관련 기사 목록을 페이지네이션으로 조회

**응답 타입**: `LocalTopicDetail` (신규 타입 정의 필요)

#### Request
```
GET /api/local/topics/660e8400-e29b-41d4-a716-446655440001?page=1&limit=10
```

**Path Parameters**:
- `id` (UUID): Local topic ID

**Query Parameters**:
- `page` (optional, number): 기사 목록의 페이지 번호 (기본값: 1)
- `limit` (optional, number): 페이지당 기사 수 (기본값: 10, 최대: 30)

#### Response (200 OK)
```typescript
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "손흥민, 시즌 마지막 경기서 득점왕 도전",
  "category": "스포츠",
  "article_count": 2105,
  "trend_score": 850,
  "articles_in_last_24h": 312,
  "keywords": ["#손흥민", "#프리미어리그", "#득점왕", "#토트넘"],
  "articles": {
    "page": 1,
    "total_articles": 2105,
    "items": [
      {
        "id": "article-uuid-1",
        "title": "'시즌 23호골' 손흥민, 살라와 공동 득점왕...아시아 선수 최초",
        "source_name": "조선일보",
        "published_at": "2025-11-28T10:00:00Z",
        "url": "https://example.com/article1"
      },
      {
        "id": "article-uuid-2",
        "title": "\"SON IS GOLDEN\" 현지 매체 극찬, 평점 9점...득점왕 등극",
        "source_name": "YTN",
        "published_at": "2025-11-28T09:00:00Z",
        "url": "https://example.com/article2"
      }
    ]
  }
}
```

#### Supabase Query (Conceptual)
```typescript
// 1. Fetch topic details
const { data: topicData, error: topicError } = await supabase
  .from('MVP2_local_topics')
  .select('*')
  .eq('id', id)
  .single();

// 2. Fetch related articles with pagination
const { data: articlesData, error: articlesError, count: articlesCount } = await supabase
  .from('MVP2_articles')
  .select('id, title_original, source_name, published_at, url', { count: 'exact' })
  .eq('local_topic_id', id)
  .order('published_at', { ascending: false })
  .range((page - 1) * limit, page * limit - 1);
```

---

