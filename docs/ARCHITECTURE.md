# System Architecture

> 이 문서는 News Spectrum MVP의 고수준 시스템 아키텍처를 설명합니다.

---

## 1. Architecture Diagram

```mermaid
graph TD
    subgraph "User Interaction (Vercel)"
        A[Next.js Frontend] --> B[Next.js API Routes (BFF)]
    end

    subgraph "Backend & Data (Supabase)"
        C[Supabase DB & Storage]
    end
    
    subgraph "Data Pipeline (Scheduled)"
        D[GitHub Actions Workflow (.github/workflows)]
    end

    subgraph "External Services"
        E[LLM APIs (OpenAI/Google)]
        F[News Sources (RSS/API)]
    end

    B --> C
    D --> F
    D --> E
    D --> C
```

## 2. Components

### Frontend & BFF (`app/`)

-   **Framework**: Next.js
-   **Hosting**: Vercel
-   **Description**:
    -   **Frontend**: 사용자가 직접 상호작용하는 PWA입니다. 서버 사이드 렌더링(SSR)을 통해 빠른 초기 로딩 속도를 보장합니다.
    -   **BFF (Backend-For-Frontend)**: Next.js의 API Routes 기능을 사용하여 프론트엔드에 최적화된 API를 제공합니다. 데이터베이스 접근, 외부 API 호출 등 민감한 로직을 서버 사이드에서 처리합니다.

### Database (`infra/supabase`)

-   **Service**: Supabase
-   **Description**: PostgreSQL 데이터베이스 및 기사 관련 미디어(이미지/영상)를 저장하기 위한 스토리지 기능을 제공하는 BaaS(Backend as a Service)입니다.

### Data Pipeline (`data/pipelines/` & `.github/workflows/`)

-   **Environment**: GitHub Actions (Scheduled Workflow)
-   **Description**:
    -   매일 정해진 시간에 `data/pipelines`에 정의된 스크립트를 실행합니다.
    -   외부 소스(RSS, News API)로부터 데이터를 수집하고, LLM API를 통해 분석/가공(토픽 생성, 입장 분석 등)합니다.
    -   최종적으로 처리된 데이터를 Supabase DB에 저장하는 자동화된 파이프라인입니다.

## 3. Data Flow

1.  **데이터 수집 및 처리 (G, O 담당)**:
    -   GitHub Actions 스케줄러가 `data/pipelines` 스크립트를 실행합니다.
    -   스크립트는 외부 뉴스 소스로부터 최신 기사를 수집하고, LLM API를 통해 토픽 클러스터링 및 입장 분석을 수행합니다.
    -   처리된 최종 데이터는 Supabase DB에 저장됩니다.

2.  **데이터 제공 (C 담당)**:
    -   사용자가 프론트엔드(Next.js Frontend)에 접속합니다.
    -   프론트엔드는 필요한 데이터를 Next.js API Routes(BFF)에 요청합니다.
    -   BFF는 Supabase DB에서 데이터를 조회하여, API 명세에 맞는 JSON 형태로 프론트엔드에 전달합니다.
