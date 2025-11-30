# Team Task Breakdown & Collaboration Log

> 이 문서는 C(Frontend), G(Data/UX), O(Ops/Backend)의 역할별 작업과 협업 논의를 기록합니다.
> 각 에이전트는 자신의 전문 영역에서 제안(Proposal)을 하고, 다른 에이전트는 이에 대해 답변(Response)하거나 추가 제안을 합니다.

---

## 🌌 Project: News Constellation (뉴스 별자리)
**Goal**: 뉴스 토픽들의 의미적 유사도를 시각화하여 "별자리"처럼 탐색하게 한다.

### 1. Initial Proposals (Round 1)

#### 🧑‍💻 **G (Data/UX)**: "좌표 데이터 생성 및 시각화 컨셉 제안"
- **제안**:
    - 제가 `llm_topic_clustering_embedding.py`를 수정해서, 각 토픽의 768차원 임베딩을 **t-SNE** 알고리즘으로 2차원(x, y)으로 축소하겠습니다.
    - 이 좌표를 DB에 저장해야 합니다.
    - **To O**: `mvp2_topics` 테이블에 `coordinate_x`, `coordinate_y` 컬럼을 추가해줄 수 있나요? (Float 타입)
    - **To C**: 프론트엔드에서는 이 좌표를 받아서 `Canvas`나 `D3.js`로 뿌려주면 됩니다. 줌/팬 기능이 필요할 것 같습니다.

#### 🛠️ **O (Ops/Backend)**: "DB 스키마 및 성능 고려"
- **답변 (To G)**:
    - 네, `mvp2_topics`에 `coordinate_x`, `coordinate_y` 컬럼 추가는 간단합니다. 바로 마이그레이션 SQL을 준비하겠습니다.
    - **제안**: 다만, 매번 전체 토픽을 다 불러오면 느릴 수 있습니다. 최근 24시간 데이터만 불러오거나, 줌 레벨에 따라 필터링하는 API가 필요할까요?
    - 일단 MVP 단계에서는 **최근 24시간 데이터 전체(약 50~100개)**를 한 번에 내려주는 방식이 가장 효율적일 것 같습니다.

#### 🎨 **C (Frontend)**: "UI 라이브러리 및 인터랙션"
- **답변 (To G/O)**:
    - 50~100개 정도라면 `Canvas`보다는 `SVG`나 일반 `div`로도 충분히 성능이 나옵니다. 구현 편의성을 위해 **React Flow**나 **D3.js**를 고려해보겠습니다.
    - **질문 (To G)**: 별자리처럼 선을 잇는 기능도 필요한가요? 아니면 점만 찍으면 되나요?
    - **제안**: 모바일 환경을 고려해서, 터치 드래그로 탐색하는 인터랙션이 중요합니다.

---

## 🆚 Project: VS Card (Perspective Card)
**Goal**: 하나의 이슈에 대한 상반된 시각을 대조하여 보여준다.

### 1. Initial Proposals (Round 1)

#### 🧑‍💻 **G (Data/UX)**: "스탠스 분석 파이프라인 제안"
- **제안**:
    - `llm_stance_analyzer.py`를 새로 만들겠습니다.
    - 각 토픽의 대표 기사들을 읽고, LLM에게 "이 이슈의 주요 쟁점은 무엇이며, 어떤 대립되는 시각이 있는가?"를 묻겠습니다.
    - 결과물: `stance_A` (예: 찬성/기대), `stance_B` (예: 반대/우려), `summary_A`, `summary_B`.
    - **To O**: 이 구조화된 데이터를 저장할 공간이 필요합니다. `mvp2_topics`에 JSONB 컬럼을 추가할까요, 아니면 별도 테이블로 뺄까요?

#### 🛠️ **O (Ops/Backend)**: "데이터 구조 설계"
- **답변 (To G)**:
    - 토픽당 하나의 VS 카드만 존재한다면, `mvp2_topics` 테이블에 `stances`라는 **JSONB** 컬럼을 추가하는 게 조회 성능상 유리합니다. (JOIN 불필요)
    - **제안**: 스키마는 `{ "A": { "label": "...", "summary": "..." }, "B": { ... } }` 형태로 갑시다.

#### 🎨 **C (Frontend)**: "카드 UI 구현"
- **답변 (To G)**:
    - 디자인은 "토스"의 VS 투표 UI를 참고하면 좋을 것 같습니다.
    - **질문**: 만약 중립적인 뉴스라 대립 구도가 없으면 어떻게 하나요? 아예 카드를 숨기나요?
    - **제안**: 데이터가 없으면 섹션 자체를 렌더링하지 않도록 처리하겠습니다.

---

## ✅ Action Items (Next Steps)

1.  **[O]** DB 마이그레이션: `coordinate_x`, `coordinate_y`, `stances` (JSONB) 컬럼 추가.
2.  **[G]** 파이프라인 구현: `llm_topic_clustering_embedding.py` 수정 (좌표 계산), `llm_stance_analyzer.py` 생성.
3.  **[C]** 프론트엔드 구현: `Constellation.tsx`, `VsCard.tsx` 컴포넌트 개발.

## 3. Detail Page Sprint (상세 페이지 완성)

**목표**: 글로벌/로컬 상세 페이지의 데이터 연결 및 기능 완성 (기한: 즉시)

### [C] Frontend & API (Lead)
- **Local Page**: `/api/local/topics/[id]`에서 `mvp2_articles`를 조인하여 기사 리스트 반환하도록 수정. 프론트엔드에 실제 기사 렌더링.
- **Global Page**: `/api/global/insights/[id]`에서 `stances` 및 `related_articles` 반환 확인. VS Card UI 연결.

### [G] Data Pipeline (Support)
- **Global Page**: `llm_stance_analyzer.py` 실행하여 `mvp2_megatopics`의 `stances` 컬럼 데이터 생성. (현재 비어있음)
- **Local Page**: 필요 시 기사 요약 데이터 제공.

### [O] Ops & DB (Support)
- **DB**: `mvp2_articles` 테이블의 `topic_id` 인덱싱 확인 (성능 최적화).
