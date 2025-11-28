# Product Vision

> **뉴스 스펙트럼(News Spectrum)**은 글로벌 뉴스에 관심은 많지만 시간이 부족한 사용자를 위해, 전 세계의 다양한 관점을 한눈에 보여주는 **'시각적 뉴스 내러티브 분석 서비스'**입니다. 기존의 뉴스 포털과 달리, 저희는 인공지능을 통해 동일한 사건에 대한 국가별/매체별 미묘한 입장 차이(스탠스)를 분석하고, 이를 직관적인 시각화로 제공하여 사용자가 스스로 균형 잡힌 시각을 형성하도록 돕습니다.

---

## Core Values (핵심 가치)

-   **Global Insight**: 복잡한 국제 정세를 AI 에디터가 요약하여, 핵심만 빠르게 파악할 수 있는 '인사이트'를 제공합니다.
-   **Local Volume**: 특정 국가가 현재 무엇에 집중하고 있는지, 텍스트가 아닌 '규모감'으로 보여줍니다.

---

# MVP Scope

## In Scope (포함)

-   **플랫폼**: 모바일 웹 (PWA)
    -   **Tech Stack**: Next.js (SSR), Vercel 배포
    -   **Target Device**: 모바일 세로 모드 최적화

-   **핵심 기능 및 데이터**
    -   **Global Tab (Insight)**
        -   Top 3 Hero Cards & Rank 4~10 List
        -   상세 페이지: 국가별 입장을 비교하는 **VS 카드 (The Bubble Battle)**
    -   **Local Tab (Volume)**
        -   기사 수 기반의 **모자이크 레이아웃 (Mosaic Logic)**
        -   Infinite Scroll 페이지네이션
    -   **데이터 처리**:
        -   주요국 뉴스 자동 수집
        -   AI 기반 토픽 추출 및 병합
        -   AI 기반 입장(Stance) 분석

## Out of Scope (제외)

-   사용자 회원가입 및 개인화 기능
-   기사 본문 전체 번역 또는 스크랩
-   소셜 미디어 공유 또는 댓글 기능
-   유료 구독 및 결제 시스템
-   데스크탑 전용 UI (모바일 뷰 중앙 정렬로 대응)
-   네이티브 앱 개발

---

# Success Metrics

-   **Metric 1: 데이터 신뢰성 (Data Reliability)**
    -   **Target**: 매일 10개 이상의 유의미한 글로벌 토픽을 안정적으로 생성하며, 토픽 분류 및 입장 분석의 정확도 85% 이상 달성.
-   **Metric 2: 사용자 인게이지먼트 (User Engagement)**
    -   **Target**: DAU(일일 활성 사용자) 1000명 달성, 평균 세션 시간 3분 이상.
-   **Metric 3: 핵심 UX 검증 (Core UX Validation)**
    -   **Target**: 사용성 테스트에서 'VS 카드'와 '모자이크 레이아웃'이 의도대로(입장차이/규모감) 인지되는지 80% 이상 확인.