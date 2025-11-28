# 토픽 진화 추적 구현 계획

## 📅 작성일: 2025-11-27

---

## 🎯 즉시 실행 가능한 작업

### Step 1: 데이터베이스 스키마 (30분)

**Migration 파일 생성:**
- `infra/supabase/migrations/20251127000001_add_topic_evolution.sql`

**필요한 테이블:**
1. `mvp_topic_history` - 일별 토픽 스냅샷
2. `mvp_topic_relationships` - 토픽 간 관계 그래프

### Step 2: 진화 탐지 스크립트 (2-3시간)

**새 파일:**
- `data/pipelines/detect_topic_evolution.py`

**주요 기능:**
- 어제-오늘 토픽 유사도 계산
- 관계 분류 (NEW, CONTINUATION, SPLIT, MERGE, END)
- Supabase에 저장

### Step 3: 파이프라인 통합 (30분)

**수정 파일:**
- `data/pipelines/aggregate_megatopics.py`

**추가 내용:**
- `detect_topic_evolution()` 호출
- 히스토리 저장

### Step 4: API 엔드포인트 (1-2시간)

**새 파일:**
- `app/frontend/src/app/api/topics/evolution/route.ts`
- `app/frontend/src/app/api/topics/[id]/timeline/route.ts`

**응답 형식:**
```json
{
  "summary": {
    "new": 5,
    "continuation": 12,
    "split": 3,
    "merge": 2,
    "ended": 4
  },
  "relationships": [...]
}
```

### Step 5: 간단한 타임라인 페이지 (2-3시간)

**새 파일:**
- `app/frontend/src/app/topics/timeline/page.tsx`

**기능:**
- 토픽 목록 with 진화 배지
- 간단한 D3.js 그래프
- 날짜 필터

---

## 📦 구현 우선순위

### 🔴 Priority 1 (이번 주)
- [ ] DB 스키마 생성 및 마이그레이션
- [ ] `detect_topic_evolution.py` 기본 구현
- [ ] 파이프라인 통합
- [ ] 데이터 수집 시작 (내일부터 쌓임)

### 🟡 Priority 2 (다음 주)
- [ ] API 엔드포인트
- [ ] 간단한 타임라인 페이지
- [ ] 진화 배지 (메인 피드에 추가)

### 🟢 Priority 3 (2주 후)
- [ ] D3.js 그래프 개선
- [ ] 토픽 상세 페이지에 타임라인 추가
- [ ] 필터/검색 기능

### 🔵 Future (Post-MVP)
- [ ] Canvas 기반 "날씨 맵"
- [ ] 파티클 애니메이션
- [ ] 3D 시각화

---

## 🗄️ 데이터베이스 스키마 상세

### mvp_topic_history

```sql
CREATE TABLE mvp_topic_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- 토픽 정보
  topic_id UUID,  -- NULL이면 오늘 생성된 신규 토픽
  date DATE NOT NULL,
  title_en TEXT,
  title_kr TEXT,

  -- 임베딩 & 좌표
  centroid_embedding VECTOR(768),
  viz_x FLOAT,  -- 2D PCA 좌표 (나중에 계산)
  viz_y FLOAT,

  -- 메트릭
  article_count INT,
  country_count INT,
  avg_stance_score FLOAT,

  -- 진화 메타데이터
  intensity INT,  -- article_count × country_count
  category INT CHECK (category BETWEEN 1 AND 5),  -- 태풍 등급
  status VARCHAR(20),  -- forming, strengthening, mature, weakening, dissipating
  age_days INT DEFAULT 0,

  -- 부모/자식 수 (빠른 조회용)
  parent_count INT DEFAULT 0,
  child_count INT DEFAULT 0,

  created_at TIMESTAMP DEFAULT NOW(),

  UNIQUE(topic_id, date)  -- 하루에 하나만
);

-- 인덱스
CREATE INDEX idx_topic_history_date ON mvp_topic_history(date DESC);
CREATE INDEX idx_topic_history_topic ON mvp_topic_history(topic_id);
CREATE INDEX idx_topic_history_intensity ON mvp_topic_history(intensity DESC);
CREATE INDEX idx_topic_history_category ON mvp_topic_history(category);
```

### mvp_topic_relationships

```sql
CREATE TABLE mvp_topic_relationships (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- 관계 (parent → child)
  parent_topic_id UUID,  -- 어제 토픽 (NULL이면 child는 신규)
  child_topic_id UUID NOT NULL,  -- 오늘 토픽
  parent_date DATE,
  child_date DATE NOT NULL,

  -- 유사도
  similarity_score FLOAT,

  -- 관계 타입
  relationship_type VARCHAR(20) NOT NULL,
  -- NEW: 신규 출현
  -- CONTINUATION: 단순 지속 (1→1, 유사도 높음)
  -- SPLIT: 분화 (1→N 중 하나)
  -- MERGE: 병합 (N→1)
  -- END: 소멸 (부모만 있고 자식 없음, 별도 처리)

  -- 복합 관계용
  is_primary_parent BOOLEAN DEFAULT true,  -- 병합 시 주 부모
  split_rank INT,  -- 분화 시 순위 (1=주 지속, 2+=분화된 것)

  created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_relationships_parent ON mvp_topic_relationships(parent_topic_id, parent_date);
CREATE INDEX idx_relationships_child ON mvp_topic_relationships(child_topic_id, child_date);
CREATE INDEX idx_relationships_type ON mvp_topic_relationships(relationship_type);
CREATE INDEX idx_relationships_dates ON mvp_topic_relationships(parent_date, child_date);
```

---

## 🐍 detect_topic_evolution.py 구조

```python
"""
토픽 진화 탐지 스크립트

매일 파이프라인 끝에 실행:
1. 어제 토픽 로드
2. 오늘 토픽 로드
3. 유사도 매트릭스 계산
4. 관계 분류
5. Supabase에 저장
"""

from scipy.spatial.distance import cosine
import numpy as np
from datetime import datetime, timedelta
from supabase import create_client
import os

# Supabase 설정
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_topics_by_date(date_str):
    """특정 날짜의 토픽 조회"""
    pass


def calculate_similarity_matrix(today_topics, yesterday_topics):
    """유사도 매트릭스 계산"""
    pass


def classify_relationship(today_topic, parent_matches):
    """관계 타입 결정"""
    pass


def detect_splits(yesterday_topics, relationships):
    """분화 탐지 (역방향 분석)"""
    pass


def detect_ended_topics(yesterday_topics, relationships):
    """소멸 토픽 탐지"""
    pass


def save_to_history(topics, date, relationships):
    """히스토리 저장"""
    pass


def save_relationships(relationships):
    """관계 저장"""
    pass


def main():
    """메인 실행"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')

    print(f"Detecting topic evolution: {yesterday} → {today}")

    # 1. 토픽 로드
    yesterday_topics = get_topics_by_date(yesterday)
    today_topics = get_topics_by_date(today)

    # 2. 진화 탐지
    relationships = detect_all_evolution_paths(
        today_topics,
        yesterday_topics
    )

    # 3. 저장
    save_to_history(today_topics, today, relationships)
    save_relationships(relationships)

    # 4. 요약
    summary = summarize_evolution(relationships)
    print(f"  ✨ New: {summary['new']}")
    print(f"  ➡️ Continuation: {summary['continuation']}")
    print(f"  🌿 Split: {summary['split']}")
    print(f"  🔀 Merge: {summary['merge']}")
    print(f"  💀 Ended: {summary['ended']}")


if __name__ == "__main__":
    main()
```

---

## 📝 aggregate_megatopics.py 수정

**마지막에 추가:**

```python
if __name__ == "__main__":
    # 기존 로직
    print("Step 6: Aggregate megatopics...")
    megatopics = aggregate_megatopics()
    save_megatopics_to_supabase(megatopics)

    # 새로 추가: 토픽 진화 탐지
    print("\nStep 7: Detect topic evolution...")
    try:
        from detect_topic_evolution import main as detect_evolution
        detect_evolution()
    except Exception as e:
        print(f"  ⚠️ Evolution detection failed: {e}")
        print("  Continuing anyway...")

    print("\n✓ Pipeline complete!")
```

---

## 🎨 간단한 타임라인 페이지 와이어프레임

```
/topics/timeline

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 토픽 진화 타임라인

[필터: 최근 7일 ▼] [전체 관계 타입 ▼]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

오늘의 변화 (2025-11-27):
• ✨ 5개 신규 토픽
• ➡️ 12개 지속 중
• 🌿 3개 분화
• 🔀 2개 병합
• 💀 4개 소멸

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌────────────────────────────────┐
│ ✨ 새로 등장한 토픽            │
├────────────────────────────────┤
│ • Samsung AI Chip Breakthrough │
│   3개국 15건                   │
│   [상세보기 →]                 │
│                                │
│ • Mexico Election Crisis       │
│   2개국 8건                    │
│   [상세보기 →]                 │
└────────────────────────────────┘

┌────────────────────────────────┐
│ 🌿 분화된 토픽                 │
├────────────────────────────────┤
│ "우크라이나-러시아 갈등"에서:  │
│   ├─→ "우크라이나 전쟁"        │
│   ├─→ "유럽 에너지 위기"       │
│   └─→ "난민 위기"              │
│                                │
│ [그래프 보기 →]                │
└────────────────────────────────┘

┌────────────────────────────────┐
│ 🔀 통합된 토픽                 │
├────────────────────────────────┤
│ → "글로벌 금융 위기"           │
│   ← "연준 금리 인상"           │
│   ← "은행 파산"                │
│   ← "주가 폭락"                │
│                                │
│ [상세보기 →]                   │
└────────────────────────────────┘
```

---

## ✅ 성공 지표

### 데이터 수집 (1주 후)
- [ ] 7일간 토픽 히스토리 수집됨
- [ ] 평균 50+ 관계 레코드/일
- [ ] 모든 관계 타입 탐지 확인

### 시각화 (2주 후)
- [ ] 타임라인 페이지 작동
- [ ] 진화 배지 표시
- [ ] API 응답 < 500ms

### 사용자 피드백 (3주 후)
- [ ] "이해하기 쉽다" 반응
- [ ] 타임라인 페이지 체류 시간 > 2분
- [ ] 공유 발생

---

## 🚀 다음 단계

1. **Migration 파일 작성** → G와 협의
2. **detect_topic_evolution.py 구현** → C 작업
3. **로컬 테스트** → 과거 데이터로 시뮬레이션
4. **프로덕션 배포** → 내일부터 데이터 수집 시작

**예상 소요 시간**: 1일 (집중 작업 시)
**완료 후**: 7일 대기 → 충분한 히스토리 확보 → 타임라인 페이지 구현

---

**Status**: 🛠️ Ready to Implement
**Owner**: C (Claude Code)
**Dependencies**: None (지금 바로 시작 가능!)
