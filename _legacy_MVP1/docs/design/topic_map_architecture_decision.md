# Topic Map Architecture Decision

**Date**: 2025-11-27
**Status**: DECIDED
**Participants**: S, C

---

## Context

뉴스 지형도(News Weather Map) 시각화를 구현하면서 토픽과 기사를 어떻게 배치할지에 대한 근본적인 질문이 제기되었습니다.

### 초기 접근법 (잘못된 방식)

```
1. 토픽에 centroid_embedding 생성 (별도 임베딩)
2. 토픽 임베딩 → PCA/t-SNE → 토픽 위치
3. 기사들을 토픽 주변에 랜덤 산포
```

**문제점:**
- 토픽 자체를 임베딩하는 것은 의미론적으로 부자연스러움
- 토픽은 기사들의 집합일 뿐, 별도의 semantic entity가 아님
- 기사 임베딩이 이미 존재하는데 중복 작업
- 대부분의 토픽에 `centroid_embedding: null` (데이터 생성 실패)

---

## Decision

**토픽은 기사들의 중심점(centroid)으로 자동 배치한다.**

### 올바른 접근법

```
1. 기사 임베딩 수집 (mvp_articles.embedding - 이미 존재)
2. 기사 임베딩 → PCA/t-SNE → 기사 위치
3. 각 토픽의 위치 = 소속 기사들의 중심점 계산
```

**근거:**
- **의미적 정확성**: 토픽은 기사들의 집합이므로, 그 중심에 위치하는 것이 자연스러움
- **데이터 효율성**: 기사 임베딩만 있으면 되고, 토픽 임베딩 불필요
- **시각적 일관성**: 기사들이 의미적 유사도에 따라 배치되고, 토픽이 그 무리의 중심에 자동으로 위치
- **자동 업데이트**: 기사가 추가/제거되면 토픽 위치도 자동으로 조정

---

## Implementation Plan

### 1. API 수정

#### Before (현재)
```typescript
GET /api/topics
→ [{ id, title, country_count, centroid_embedding, ... }]
```

#### After (수정안)
```typescript
GET /api/topics
→ [{
  id, title, country_count, ...
  articles: [{
    id, title, country, embedding: [768D array], ...
  }]
}]
```

**또는 별도 엔드포인트:**
```typescript
GET /api/topics/with-articles
GET /api/topics/[id]/articles
```

### 2. 프론트엔드 수정

**파일**: `app/frontend/public/map.html`

```javascript
async function loadData() {
  // 1. 토픽 + 기사 데이터 가져오기
  const topicsData = await fetch('/api/topics?include_articles=true');

  // 2. 모든 기사 임베딩 수집
  const allArticles = [];
  const allEmbeddings = [];
  topicsData.forEach(topic => {
    topic.articles.forEach(article => {
      allArticles.push({ ...article, topicId: topic.id });
      allEmbeddings.push(article.embedding);
    });
  });

  // 3. 기사 위치 계산 (PCA/t-SNE)
  const articlePositions = reduceDimensions(allEmbeddings);

  // 4. 기사 객체 생성
  articles = allArticles.map((article, i) => ({
    ...article,
    absX: articlePositions[i].x * width,
    absY: articlePositions[i].y * height,
    size: 3,
    color: getCountryColor(article.country)
  }));

  // 5. 토픽 위치 = 소속 기사들의 centroid
  topics = topicsData.map(topic => {
    const topicArticles = articles.filter(a => a.topicId === topic.id);
    const centerX = topicArticles.reduce((sum, a) => sum + a.absX, 0) / topicArticles.length;
    const centerY = topicArticles.reduce((sum, a) => sum + a.absY, 0) / topicArticles.length;

    return {
      ...topic,
      absX: centerX,
      absY: centerY,
      size: calculateSize(topic),
      color: getStanceColor(topic.avg_stance_score)
    };
  });
}
```

### 3. 백엔드 수정 (필요시)

**Option A**: `/api/topics`에 `?include_articles=true` 파라미터 추가

**Option B**: 별도 엔드포인트 생성
```typescript
// app/frontend/src/app/api/topics/with-articles/route.ts
export async function GET(request: Request) {
  const topics = await supabase
    .from('mvp_topics')
    .select(`
      *,
      articles:mvp_topic_articles(
        article:mvp_articles(
          id, title, country, embedding, stance_score
        )
      )
    `);

  return Response.json(topics);
}
```

---

## Performance Considerations

### 데이터 크기
- 토픽당 평균 10-50개 기사
- 임베딩 크기: 768D × 4 bytes = 3KB per article
- 50개 토픽 × 20 기사 × 3KB = **~3MB** (acceptable for initial load)

### 최적화 옵션
1. **Limit articles per topic**: 최대 15-20개로 제한 (대표 기사만)
2. **Lazy loading**: 기사 임베딩은 필요시에만 로드
3. **Server-side dimension reduction**: 서버에서 t-SNE 미리 계산
4. **Caching**: 임베딩 위치 계산 결과를 캐시

---

## Migration Path

### Phase 1: Immediate (Today)
- [x] Knowledge.md에 결정사항 기록
- [ ] 이 문서 작성
- [ ] G와 협의 (토픽 임베딩 작업 중단 여부)

### Phase 2: API Implementation
- [ ] `/api/topics/with-articles` 엔드포인트 생성
- [ ] 기사 임베딩 포함 여부 확인
- [ ] 응답 데이터 크기 측정

### Phase 3: Frontend Update
- [ ] `map.html` loadData() 함수 수정
- [ ] 기사 위치 계산 로직 구현
- [ ] 토픽 centroid 계산 로직 구현
- [ ] 성능 테스트

### Phase 4: Optimization
- [ ] 기사 수 제한 (per topic)
- [ ] 서버 사이드 t-SNE 고려
- [ ] 캐싱 전략 수립

---

## ✅ G의 답변 (2025-11-27)

### Q1. 임베딩 상태: 현재 `mvp_articles.embedding` 필드 채워져 있나요?
**A**: ✅ **네, 100% 채워져 있습니다.**
- 현재 약 4,500개의 기사가 모두 임베딩 벡터를 가지고 있습니다.

### Q2. 토픽 임베딩: `centroid_embedding` 작업 중단해도 되나요?
**A**: ✅ **네, 가능합니다.**
- 현재 로직도 별도의 API 비용을 들여 토픽을 임베딩하는 것이 아니라, **기사들의 임베딩 평균(Mean)**을 계산하여 저장하는 방식입니다.
- **S님의 "기사 중심" 철학과 이미 일치합니다!**
- 캐싱 효과가 있으나, 프론트엔드에서 직접 계산한다면 DB 저장을 멈춰도 됩니다.

### Q3. API 지원: 토픽별 기사 임베딩 가져오는 API 추가 가능한가요?
**A**: ✅ **네, 가능합니다.**
- `/api/topics` 호출 시 `include_articles=true` 같은 옵션을 추가하여 기사 리스트와 임베딩을 함께 반환하도록 수정할 수 있습니다.

### Q4. 성능: 토픽당 기사 몇 개까지 괜찮을까요?
**A**: ⚠️ **데이터 전송량(Payload)이 문제입니다.**
- 원본 임베딩(1536차원)을 그대로 보내면 토픽당 기사 50개 기준 **약 150KB** 소모
- 모바일에서 무거울 수 있음

**💡 G의 제안**:
> **서버(API)에서 PCA로 2차원 좌표(x, y)만 계산해서 내려주면, 기사가 수천 개라도 가볍게 처리 가능합니다. 이 방식을 추천합니다.**

---

## Updated Decision: Server-Side Dimension Reduction

G의 제안에 따라 **서버 사이드 PCA**로 전략을 수정합니다.

### 최종 아키텍처

```
1. [Backend] 모든 기사 임베딩 수집 (mvp_articles.embedding - 1536D)
2. [Backend] PCA/t-SNE로 2D 좌표 계산
3. [Backend] API 응답: 기사별 (x, y) 좌표 + 메타데이터
4. [Frontend] 기사들을 받은 좌표에 배치
5. [Frontend] 토픽 = 소속 기사들의 중심점 계산
```

### 장점
✅ **경량 Payload**: 기사당 8 bytes (x: float32, y: float32) vs 6KB (1536D)
✅ **일관된 배치**: 서버에서 한 번만 계산, 클라이언트 간 동일
✅ **확장 가능**: 수천 개 기사도 처리 가능
✅ **모바일 최적화**: 네트워크/메모리 부담 최소화

---

## Final Implementation Plan

### Phase 1: Backend (G)

**파일**: `app/frontend/src/app/api/topics/map/route.ts` (신규)

```typescript
// GET /api/topics/map
export async function GET(request: Request) {
  // 1. 모든 토픽과 기사 가져오기
  const topics = await supabase
    .from('mvp_topics')
    .select(`
      *,
      articles:mvp_topic_articles(
        article:mvp_articles(
          id, title, country, stance_score, embedding
        )
      )
    `);

  // 2. 모든 기사 임베딩 수집
  const allArticles = [];
  const allEmbeddings = [];

  topics.forEach(topic => {
    topic.articles.forEach(({ article }) => {
      allArticles.push({ ...article, topic_id: topic.id });
      allEmbeddings.push(article.embedding);
    });
  });

  // 3. PCA로 2D 좌표 계산 (Python 스크립트 호출 또는 JS 라이브러리)
  const positions = await reduceDimensionsPCA(allEmbeddings);

  // 4. 기사 객체에 좌표 추가
  const articlesWithPositions = allArticles.map((article, i) => ({
    id: article.id,
    title: article.title,
    country: article.country,
    stance_score: article.stance_score,
    topic_id: article.topic_id,
    x: positions[i].x,
    y: positions[i].y
  }));

  // 5. 토픽별로 그룹화
  const topicsWithArticles = topics.map(topic => ({
    id: topic.id,
    title_kr: topic.title_kr,
    country_count: topic.country_count,
    avg_stance_score: topic.avg_stance_score,
    articles: articlesWithPositions.filter(a => a.topic_id === topic.id)
  }));

  return Response.json(topicsWithArticles);
}

// PCA 구현 (sklearn-like)
async function reduceDimensionsPCA(embeddings: number[][]): Promise<{x: number, y: number}[]> {
  // Option A: Python subprocess
  // Option B: ml.js 라이브러리
  // Option C: 간소화된 PCA (현재 map.html과 동일)
}
```

**예상 응답**:
```json
[
  {
    "id": 1,
    "title_kr": "토픽 제목",
    "country_count": 3,
    "avg_stance_score": 52,
    "articles": [
      {
        "id": 101,
        "title": "기사 제목",
        "country": "US",
        "stance_score": 45,
        "topic_id": 1,
        "x": 0.234,
        "y": 0.567
      }
    ]
  }
]
```

**Payload 크기**:
- 50 토픽 × 20 기사 × 80 bytes = **80KB** (vs 1.5MB with embeddings)

---

### Phase 2: Frontend (C)

**파일**: `app/frontend/public/map.html`

```javascript
async function loadData() {
  // 1. 새 API 호출
  const response = await fetch('/api/topics/map');
  const topicsData = await response.json();

  // 2. 기사들 그대로 사용 (이미 x, y 있음)
  articles = [];
  topicsData.forEach(topic => {
    topic.articles.forEach(article => {
      articles.push({
        id: article.id,
        title: article.title,
        country: article.country,
        stance: article.stance_score,
        absX: article.x * width,  // 서버에서 받은 좌표
        absY: article.y * height,
        size: 3,
        color: getCountryColor(article.country),
        parentTopic: topic.id
      });
    });
  });

  // 3. 토픽 = 기사들의 중심점
  megaTopics = [];
  nationalTopics = [];

  topicsData.forEach(topic => {
    const topicArticles = articles.filter(a => a.parentTopic === topic.id);
    const centerX = topicArticles.reduce((sum, a) => sum + a.absX, 0) / topicArticles.length;
    const centerY = topicArticles.reduce((sum, a) => sum + a.absY, 0) / topicArticles.length;

    const topicObj = {
      id: topic.id,
      title: topic.title_kr,
      article_count: topic.articles.length,
      country_count: topic.country_count,
      stance: topic.avg_stance_score,
      absX: centerX,
      absY: centerY,
      size: Math.sqrt(topic.articles.length * topic.country_count) * 4 + 30,
      color: getStanceColor(topic.avg_stance_score)
    };

    if (topic.country_count >= 3) {
      megaTopics.push({ ...topicObj, type: 'mega' });
    } else {
      nationalTopics.push({ ...topicObj, type: 'national' });
    }
  });
}
```

---

### Phase 3: PCA 구현 옵션

#### Option A: Python Subprocess (추천)
```python
# app/frontend/src/lib/pca_service.py
import numpy as np
from sklearn.decomposition import PCA
import sys
import json

def reduce_dimensions(embeddings):
    pca = PCA(n_components=2)
    positions = pca.fit_transform(embeddings)

    # Normalize to 0-1
    min_x, max_x = positions[:, 0].min(), positions[:, 0].max()
    min_y, max_y = positions[:, 1].min(), positions[:, 1].max()

    normalized = [
        {
            "x": 0.1 + (x - min_x) / (max_x - min_x) * 0.8,
            "y": 0.1 + (y - min_y) / (max_y - min_y) * 0.8
        }
        for x, y in positions
    ]

    return normalized

if __name__ == "__main__":
    embeddings = json.loads(sys.argv[1])
    result = reduce_dimensions(embeddings)
    print(json.dumps(result))
```

#### Option B: ml.js (순수 JS)
```typescript
import { PCA } from 'ml-pca';

function reduceDimensionsPCA(embeddings: number[][]): {x: number, y: number}[] {
  const pca = new PCA(embeddings);
  const reduced = pca.predict(embeddings, { nComponents: 2 });
  // normalize...
}
```

#### Option C: 간소화된 PCA (현재 방식)
- 현재 `map.html`의 `reduceDimensions()` 함수를 서버로 이동

---

### Phase 4: 캐싱 (선택)

**Redis 캐싱** (날짜별로 좌표 저장):
```typescript
const cacheKey = `topic_map:${date}`;
const cached = await redis.get(cacheKey);
if (cached) return JSON.parse(cached);

// ... PCA 계산 ...

await redis.set(cacheKey, JSON.stringify(result), 'EX', 86400); // 24h
```

---

## References

- `docs/design/news_weather_map_vision.md` - 전체 비전
- `app/frontend/public/map.html` - 현재 구현
- `SONAR_MAP_GUIDE.md` - 사용자 가이드
- `docs/Knowledge.md:312` - 결정 기록
