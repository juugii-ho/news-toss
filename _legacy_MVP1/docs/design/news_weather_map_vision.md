# 뉴스 기상도 (News Weather Map) 비전

## 📅 제안일: 2025-11-27
## 💡 핵심 컨셉

> **"뉴스를 태풍처럼 본다"**
> 토픽이 생성되고, 이동하고, 분화하고, 병합하고, 소멸하는 과정을
> 위성 태풍 추적 이미지처럼 시각화

---

## 🎯 목표

### 사용자 경험
- 뉴스 흐름을 **직관적**으로 이해
- 복잡한 토픽 진화를 **한눈에** 파악
- 정보의 생명주기를 **시간의 흐름**으로 체험

### 차별화 포인트
- **AllSides**: 정적 막대 그래프
- **Ground News**: 단순 리스트
- **우리**: 살아 숨쉬는 뉴스 생태계 🌀

---

## 🌪️ 비주얼 메타포

### 태풍 속성 → 토픽 속성 매핑

| 태풍 | 토픽 | 시각화 |
|------|------|--------|
| 형성 (Forming) | 신규 토픽 출현 | 작은 점 → 커지는 원 |
| 강화 (Strengthening) | 기사/국가 증가 | 색상 진해짐, 크기 증가 |
| 최대 강도 (Mature) | 메가토픽 확립 | 강렬한 색, 소용돌이 효과 |
| 이동 (Moving) | 임베딩 공간 이동 | 경로 추적선 |
| 분화 (Splitting) | 하위 토픽 분리 | 하나에서 여러 개로 갈라짐 |
| 병합 (Merging) | 여러 토픽 통합 | 여러 개가 하나로 합쳐짐 |
| 약화 (Weakening) | 관심 감소 | 색상 옅어짐, 크기 감소 |
| 소멸 (Dissipating) | 토픽 종료 | 페이드 아웃 |

### 태풍 등급 시스템

```
Category 1 🌱: 소규모 (article_count × country_count < 20)
Category 2 🌿: 중규모 (20-50)
Category 3 🌀: 대형 (50-100)
Category 4 🌪️: 강력 (100-150)
Category 5 ⚡️: 슈퍼 토픽 (150+)
```

### 컬러 팔레트 (기상 레이더 스타일)

- **Category 1**: `rgba(34, 197, 94, 0.8)` - 연한 초록
- **Category 2**: `rgba(234, 179, 8, 0.9)` - 노랑
- **Category 3**: `rgba(249, 115, 22, 0.95)` - 주황
- **Category 4**: `rgba(239, 68, 68, 1)` - 빨강
- **Category 5**: `rgba(139, 92, 246, 1)` - 보라 (펄스 효과)

---

## 🔧 기술 아키텍처

### 1. 데이터 구조

```sql
-- 토픽 히스토리
CREATE TABLE mvp_topic_history (
  id UUID PRIMARY KEY,
  topic_id UUID,
  date DATE,
  centroid_embedding VECTOR(768),
  viz_x FLOAT,  -- 2D 투영 좌표
  viz_y FLOAT,
  article_count INT,
  country_count INT,
  avg_stance_score FLOAT,
  intensity INT,  -- article_count × country_count
  category INT,   -- 1-5
  status VARCHAR(20), -- forming, strengthening, mature, weakening, dissipating
  age_days INT
);

-- 토픽 관계 (진화 그래프)
CREATE TABLE mvp_topic_relationships (
  id UUID PRIMARY KEY,
  parent_topic_id UUID,
  child_topic_id UUID,
  parent_date DATE,
  child_date DATE,
  similarity_score FLOAT,
  relationship_type VARCHAR(20), -- NEW, CONTINUATION, SPLIT, MERGE, END
  is_primary_parent BOOLEAN,
  split_rank INT
);
```

### 2. 진화 탐지 알고리즘

```python
# data/pipelines/detect_topic_evolution.py

def detect_all_evolution_paths():
    """
    토픽 진화 패턴 탐지:
    - 1→1 (Continuation)
    - 1→N (Split)
    - N→1 (Merge)
    - New (출현)
    - End (소멸)
    """

    # Step 1: 유사도 매트릭스 계산 (today × yesterday)
    similarity_matrix = calculate_similarity_matrix(
        today_topics,
        yesterday_topics
    )

    # Step 2: 관계 분류
    for today_topic in today_topics:
        parents = find_parents(today_topic, similarity_matrix)

        if len(parents) == 0:
            type = 'NEW'
        elif len(parents) == 1:
            type = 'CONTINUATION'
        else:
            type = 'MERGE'

    # Step 3: 분화 탐지 (역방향)
    for yesterday_topic in yesterday_topics:
        children = find_children(yesterday_topic)

        if len(children) > 1:
            # 첫 번째: CONTINUATION
            # 나머지: SPLIT
            mark_as_split(children)

    return relationships
```

### 3. 시각화 레이어

**Canvas 기반 렌더링:**
- **파티클 시스템**: 소용돌이 효과
- **열지도**: 뉴스 밀도 표현
- **경로 추적**: 과거 이동 경로 (실선) + 예측 (점선)
- **애니메이션**: 시간에 따른 변화

**프레임워크:**
- Canvas API (고성능)
- D3.js (데이터 바인딩)
- React Three Fiber (3D 옵션)

---

## 🎨 UI/UX 설계

### 메인 화면 구성

```
┌─────────────────────────────────────────────────────┐
│ 🌍 뉴스 기상도                    2025-11-27 23:30  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [활성 토픽 목록]      [메인 맵 영역]      [범례]  │
│   좌측 패널            중앙 캔버스         우측패널  │
│                                                     │
│   ● Ukraine War       🌀 태풍 애니메이션    등급:  │
│     5개국 23건                              🌱 1   │
│     Category 4                              🌿 2   │
│                                             🌀 3   │
│   ● Energy Crisis                           🌪️ 4   │
│     3개국 15건                              ⚡️ 5   │
│     Category 2                                     │
│                                                     │
├─────────────────────────────────────────────────────┤
│ [⏮][⏪][▶️][⏩][⏭]  [━━━●━━━━]  속도: 2x  [옵션]  │
│  처음 느림 재생 빠름 최근   타임라인                │
└─────────────────────────────────────────────────────┘
```

### 인터랙션

1. **재생 컨트롤**
   - 타임라인 슬라이더: 30일 전 ↔ 오늘
   - 재생 속도: 0.5x, 1x, 2x, 4x
   - 특정 날짜로 점프

2. **토픽 상세**
   - 태풍 클릭 → 상세 패널
   - 경로 히스토리 표시
   - 관련 기사 목록
   - 진화 그래프

3. **뷰 옵션**
   - 열지도 모드 ON/OFF
   - 경로 표시 ON/OFF
   - 예측 경로 ON/OFF
   - 필터: 국가, 카테고리

---

## 📊 구현 단계

### Phase 1: 데이터 인프라 (1주)

**목표**: 토픽 진화 추적 시스템 구축

- [ ] `mvp_topic_history` 테이블 생성
- [ ] `mvp_topic_relationships` 테이블 생성
- [ ] `detect_topic_evolution.py` 구현
- [ ] `aggregate_megatopics.py`에 통합
- [ ] 매일 파이프라인에서 자동 실행

**산출물**:
- 30일간 토픽 히스토리 데이터
- 진화 관계 그래프 데이터

### Phase 2: 기본 시각화 (1-2주)

**목표**: 타임라인 뷰 프로토타입

- [ ] `/api/topics/evolution` 엔드포인트
- [ ] 간단한 타임라인 페이지
- [ ] 토픽별 drift 그래프
- [ ] 관계 표시 (분화/병합)

**산출물**:
- `/topics/timeline` 페이지
- 기본 애니메이션 (fade in/out)

### Phase 3: 날씨 맵 프로토타입 (2-3주)

**목표**: Canvas 기반 "뉴스 기상도" 첫 버전

- [ ] Canvas 렌더링 엔진
- [ ] 파티클 시스템 (소용돌이)
- [ ] 태풍 등급 시스템
- [ ] 재생 컨트롤

**산출물**:
- `/weather-map` 페이지
- 기본 태풍 시각화

### Phase 4: 고급 효과 (2-3주)

**목표**: 완성도 높은 날씨 맵

- [ ] 이동 경로 추적 + 예측
- [ ] 열지도 모드
- [ ] 분화/병합 애니메이션
- [ ] 성능 최적화

**산출물**:
- 프로덕션 레벨 날씨 맵
- 모바일 최적화

### Phase 5: 폴리시 & 마케팅 (1주)

**목표**: 출시 준비

- [ ] 튜토리얼 추가
- [ ] 공유 기능 (스냅샷)
- [ ] 효과음 (선택)
- [ ] 데모 영상 제작

**산출물**:
- 마케팅 자료
- SNS 공유용 콘텐츠

---

## 🎬 즉시 실행 가능한 것

### 지금 바로 할 수 있는 것:

1. **데이터베이스 스키마 생성** (10분)
   - migration 파일 작성
   - Supabase에서 실행

2. **진화 탐지 스크립트 작성** (1-2시간)
   - `detect_topic_evolution.py`
   - 기본 알고리즘 구현

3. **파이프라인 통합** (30분)
   - `aggregate_megatopics.py`에 추가
   - 내일부터 데이터 쌓이기 시작

4. **간단한 API 엔드포인트** (1시간)
   - `/api/topics/evolution`
   - 관계 데이터 반환

5. **프로토타입 페이지** (2-3시간)
   - `/topics/timeline`
   - 리스트 뷰로 진화 표시
   - D3.js 간단한 그래프

### 다음 스프린트에서:

- Canvas 기반 날씨 맵
- 파티클 시스템
- 애니메이션 효과

---

## 💡 마케팅 메시지

### 랜딩 페이지 헤드라인

> **"뉴스도 태풍처럼 생겨나고 사라집니다"**
>
> 전 세계 이슈를 위성처럼 실시간 추적하세요
>
> [뉴스 기상도 보기 →]

### 소셜 미디어 피치

```
🌀 뉴스를 날씨처럼 본다면?

태풍이 생겨나고 이동하듯,
뉴스 토픽도 생성-진화-소멸합니다.

우리는 이 과정을 위성 이미지처럼 시각화했습니다.

👉 [링크]
```

### 프레스 릴리스 포인트

- **세계 최초**: 뉴스 토픽을 기상 시스템처럼 추적
- **AI 기반**: 임베딩 공간에서 토픽 이동 감지
- **직관적**: 복잡한 진화 과정을 한눈에
- **투명성**: 알고리즘 가시화로 신뢰도 증대

---

## 🔗 참고 자료

### 영감 소스
- [NOAA 태풍 추적](https://www.nhc.noaa.gov/)
- [Windy.com](https://www.windy.com/) - 바람 흐름 시각화
- [Ventusky](https://www.ventusky.com/) - 날씨 레이어

### 기술 참고
- [Canvas 파티클 시스템](https://github.com/VincentGarreau/particles.js/)
- [D3.js Force Simulation](https://d3js.org/d3-force)
- [Three.js 파티클](https://threejs.org/examples/#webgl_points_waves)

---

## 📝 노트

- 이 문서는 비전 문서입니다. 구체적인 구현 사양은 별도 문서로 작성 필요.
- Phase별 일정은 리소스 상황에 따라 조정 가능.
- MVP는 Phase 2까지, 날씨 맵은 Post-MVP 고려.

**Status**: 💡 Idea / Vision
**Priority**: High (차별화 포인트)
**Owner**: C (Claude Code - Frontend/Backend), G (Data Pipeline)
