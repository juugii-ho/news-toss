# 🌍 뉴스토스 (News Toss) - News Spectrum

> **"헤드라인 너머, 세상을 보다."**
>
> 뉴스토스는 전 세계 13개국 이상의 다양한 시각을 모아 균형 잡힌 "뉴스 스펙트럼"을 제공하는 AI 기반 글로벌 뉴스 애그리게이터입니다.

https://news-toss-ecru.vercel.app/

<img src="app/frontend/public/assets/news_toss_hero.jpg" alt="News Toss Hero" width="600">

## 🚀 프로젝트 소개

양극화된 세상에서 뉴스토스는 사용자가 글로벌 이슈를 다각도로 이해할 수 있도록 돕습니다. 단순히 기사 목록을 나열하는 대신, 국가별 보도의 **스탠스(지지/비판/중립)** 를 AI로 분석하고 의견의 "스펙트럼"을 시각화하여 보여줍니다.

이 프로젝트는 매일 수천 건의 기사를 수집, 번역하고 "메가토픽"으로 합성하는 **완전 자동화된 AI 뉴스 파이프라인**으로 운영됩니다.

### ✨ 핵심 기능

*   **🌐 글로벌 메가토픽**: 미국, 한국, 일본, 중국, 영국, 프랑스, 독일 등 13개국의 관련 뉴스를 자동으로 클러스터링하여 하나의 글로벌 서사로 묶습니다.
*   **⚖️ 스탠스 스펙트럼**: AI가 각 기사의 어조를 분석하여 관점의 분포(지지 vs 비판 vs 사실 전달)를 시각적으로 보여줍니다.
*   **🥣 토픽 볼 (Topic Bowl)**: 로컬 트렌드 토픽을 통통 튀는 공 모양으로 시각화한 인터랙티브 UI (Matter.js 물리 엔진 활용)를 제공합니다.
*   **🤖 완전 자동화**: **Gemini 2.5**와 **GitHub Actions**를 기반으로 한 9단계 데이터 파이프라인이 매일 오후 3시(KST)에 사람의 개입 없이 뉴스를 수집, 분석, 발행합니다.
*   **⚡ 무중단 배포**: Atomic Publishing 방식을 적용하여 업데이트 중에도 사용자는 항상 일관된 데이터를 볼 수 있습니다.

---

## 🛠️ 기술 스택 (Tech Stack)

### 프론트엔드 (Frontend)
*   **Framework**: Next.js 14 (App Router)
*   **Styling**: Vanilla CSS (모바일 우선, 애플/토스 스타일의 미니멀한 디자인)
*   **Animation**: Framer Motion
*   **Physics**: Matter.js (Topic Bowl 구현)

### 백엔드 & 데이터 (Backend & Data)
*   **Database**: Supabase (PostgreSQL + pgvector 의미 기반 검색)
*   **AI/LLM**: Google Gemini 2.5 Pro & Flash (번역, 요약, 스탠스 분석, 썸네일 생성)
*   **Language**: Python 3.10 (데이터 파이프라인)

### 인프라 (Infrastructure)
*   **CI/CD**: GitHub Actions (Daily Cron Jobs)
*   **Hosting**: Vercel (Frontend)

---

## 🔄 9단계 AI 파이프라인

뉴스토스의 핵심 엔진은 RSS 피드를 구조화된 인사이트로 변환하는 정교한 Python 파이프라인입니다:

1.  **RSS 수집 (RSS Collection)**: 주요 글로벌 언론사에서 매일 5,000건 이상의 기사를 수집합니다.
2.  **번역 (Translation)**: 비영어권 헤드라인을 Gemini를 통해 한국어/영어로 번역합니다.
3.  **클러스터링 (Clustering)**: **HDBSCAN**과 임베딩 벡터를 사용하여 유사한 기사들을 "토픽"으로 그룹화합니다.
4.  **데이터 보강 (Enrichment)**: AI가 각 토픽의 키워드, 카테고리, 스탠스를 추출합니다.
5.  **메가토픽 분석 (Megatopic Analysis)**: 국경을 넘어 연결되는 로컬 토픽들을 "글로벌 메가토픽"으로 병합합니다.
6.  **요약 (Summarization)**: 각 토픽에 대해 3줄 요약을 생성합니다.
7.  **에디터 코멘트 (Editor Comments)**: AI "에디터"가 글로벌 이슈에 대한 맥락과 통찰을 제공합니다.
8.  **썸네일 생성 (Thumbnail Generation)**: 대표 이미지를 선택하거나 생성합니다.
9.  **일괄 발행 (Atomic Publishing)**: 업데이트를 배치 단위로 처리하여 다운타임 없이 즉시 발행합니다.

---

## 🏃‍♂️ 시작하기 (Getting Started)

### 필수 요구사항
*   Node.js 18+
*   Python 3.10+
*   Supabase 계정
*   Google Gemini API Key

### 설치 방법

1.  **저장소 복제**
    ```bash
    git clone https://github.com/juugii-ho/news-toss.git
    cd news-toss
    ```

2.  **환경 변수 설정**
    ```bash
    cp .env.example .env
    # .env 파일에 SUPABASE_URL, SUPABASE_KEY, GOOGLE_API_KEY 등을 입력하세요.
    ```

3.  **의존성 설치**
    ```bash
    # 프론트엔드
    cd app/frontend
    npm install

    # 데이터 파이프라인
    cd ../../
    python -m venv venv
    source venv/bin/activate
    pip install -r data/pipelines/requirements.txt
    ```

4.  **로컬 실행**
    ```bash
    # 프론트엔드 개발 서버
    cd app/frontend
    npm run dev
    ```

---

## 🤝 기여하기

이 프로젝트는 AI 에이전트를 활용한 뉴스 큐레이션의 가능성을 보여주기 위한 MVP(Minimum Viable Product)입니다. 제안이나 풀 리퀘스트(PR)는 언제나 환영합니다!

## 📝 라이선스

MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.
