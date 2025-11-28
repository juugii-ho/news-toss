# Data Pipeline Architecture for News Spectrum

> 이 문서는 News Spectrum MVP의 데이터 처리 파이프라인 아키텍처를 정의합니다.
> 담당자: **G (Data/UX)**

---

## 1. 개요 (Overview)

본 파이프라인의 목표는 전 세계의 뉴스 데이터를 수집, 분석, 가공하여 'Global Insight'와 'Local Trend' 탭에서 요구하는 데이터 모델에 맞는 최종 JSON을 생성하는 것입니다. 전체 프로세스는 4단계(수집 → 클러스터링 → 분석/가공 → 전달)로 구성됩니다.

## 2. 파이프라인 상세 단계 (Pipeline Stages)

### Phase 1: 데이터 수집 (Ingestion)

-   **Source**: 지정된 RSS 피드, 뉴스 API 등 (MVP 단계에서는 약 10~15개 미디어 소스로 제한)
-   **Process**:
    1.  주기적으로(예: 15분마다) 각 소스에서 새로운 기사 원문(제목, 본문, 발행일, 이미지/영상 URL 등)을 수집합니다.
    2.  수집된 데이터는 정규화된 포맷으로 `Raw_Articles` 데이터베이스에 저장됩니다.

### Phase 2: 토픽 클러스터링 (Topic Clustering)

-   **Goal**: 유사한 내용을 다루는 기사들을 하나의 '주제(Topic)'로 묶습니다.
-   **Process**:
    1.  **초기 클러스터링**: TF-IDF 또는 Doc2Vec과 같은 알고리즘을 사용하여 `Raw_Articles`에서 유사한 기사 그룹을 형성합니다.
    2.  **LLM을 통한 제목 생성 (Title Refinement)**:
        - 각 클러스터의 핵심 내용을 요약하여, 명료하고 대표성 있는 토픽 제목(예: "엔비디아, 거품일까요?")을 LLM으로 생성합니다. (S님과 논의된 `DT-002` 결정사항 반영)
    3.  **임베딩 및 최종 클러스터링**:
        - 생성된 토픽 제목을 다시 임베딩(Embedding)합니다.
        - 이 임베딩 값을 기준으로 초기 클러스터를 재조정하여 더 정확한 최종 토픽 그룹을 확정합니다.
    4.  결과는 `Topics` 테이블에 저장됩니다 (예: `topic_id`, `llm_generated_title`, `related_article_ids`).

### Phase 3: 데이터 분석 및 가공 (Analysis & Enrichment)

-   **Goal**: 클러스터링된 토픽을 API 명세에 맞게 구체적인 데이터로 가공합니다.
-   **Process (두 탭에 대해 병렬 처리)**:

    #### A) For Global Insight
    1.  **국가별 데이터 분류**: 각 토픽에 속한 기사들을 국가별로 분류합니다.
    2.  **입장(Stance) 분석**: 특정 국가의 기사 그룹 전체의 논조를 분석하여 `POSITIVE`, `NEGATIVE`, `NEUTRAL` 중 하나의 `stance` 값을 할당합니다.
    3.  **한 줄 요약(One-Liner) 생성**: LLM을 사용하여 해당 국가의 입장을 잘 나타내는 구어체 요약문(one_liner_ko)을 생성합니다. (페르소나: "똑똑하지만 위트있는 분석가")
    4.  결과는 `Global_Insights` 테이블에 저장됩니다.

    #### B) For Local Trend
    1.  **통계 계산**: 각 토픽의 `article_count`를 집계합니다.
    2.  **대표 미디어 선정**: 토픽 내 기사들 중 가장 많이 사용되거나 가장 고화질인 이미지/영상 URL을 `media_url`로 선정합니다.
    3.  **모자이크 레벨(Display Level) 할당**:
        - `article_count`를 기준으로 내림차순 정렬합니다.
        - 백분위 순위에 따라 `display_level` (1, 2, 3)을 할당합니다. (`DT-002` 결정사항)
    4.  결과는 `Local_Trends` 테이블에 저장됩니다.

### Phase 4: API 전달 (API Delivery)

-   **Process**:
    1.  프론트엔드(C)의 요청 시, `Global_Insights`와 `Local_Trends` 테이블에서 데이터를 조회합니다.
    2.  `GET /api/global/insights/{id}`와 `GET /api/local/trends` API 명세에 맞는 최종 JSON 형태로 가공하여 응답합니다.

## 3. 주요 기술 스택 (예상)

-   **Data Processing**: Python (Pandas, Scikit-learn)
-   **LLM Integration**: OpenAI API 또는 Google Gemini API
-   **Workflow Orchestration**: Airflow 또는 간단한 Cron-based scripts
-   **Database**: Supabase (PostgreSQL)

---

이 설계안에 대해 S, C, O 님의 피드백을 요청합니다.
