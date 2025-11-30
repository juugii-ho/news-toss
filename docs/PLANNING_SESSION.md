# Planning Session: Roadmap Task Breakdown

> 이 문서는 `docs/ROADMAP.md`의 내용을 실행 가능한 태스크로 분해하고, 담당자를 지정하며, 구체적인 해결 방안을 논의하기 위해 작성되었습니다.
> 각 태스크는 S(PO)의 최종 승인 후 `docs/WORK.md`로 이전됩니다.

---

## 🌟 1. 핵심 기능 개선 (Core Feature Enhancements)

---
### **1.1. Local 탭: '트렌드 스코어' 도입**
- **ID**: `FUTURE-TASK-01`
- **Owner**: `G`
- **Priority**: `P1` (제안)
- **Related Decision**: `DT-003`

#### **Proposed Solution / Next Steps (G 제안)**
1.  S(PO)께서 `DT-003`을 최종 승인합니다.
2.  `MVP2_local_topics` 테이블에 `trend_score` 컬럼을 추가합니다. (C 또는 O와 협의 필요)
3.  `data/pipelines/`에 `trend_score_calculator.py` 스크립트를 새로 개발합니다.
4.  이 스크립트는 매 파이프라인 실행 시, 각 `LocalTopic`의 `article_count`와 `created_at`을 기반으로 트렌드 스코어를 계산하고 DB에 업데이트합니다.
5.  기존 `Gravity Issue Bowl`의 크기 계산 로직이 `article_count` 대신 `trend_score`를 사용하도록 수정합니다.

#### **Discussion / Feedback**
- **[G → C]**: 이 기능이 구현되면, `/api/local/trends` API의 정렬 기준을 `article_count`가 아닌 `trend_score` 기준으로 변경해야 합니다. 확인 부탁드립니다.
- **[G → S]**: `DT-003` 승인 시, `WORK.md`에 정식 태스크로 등록하겠습니다.

---
### **1.2. Global 탭: 국가 확장 및 비교 기능**
- **ID**: `FUTURE-TASK-02`
- **Owner**: `G` (데이터 수집), `C` (UI/API)
- **Priority**: `P2` (제안)

#### **Proposed Solution / Next Steps (G 제안)**
1.  **[G]** `packages/config/rss_feeds.json`에 분석 대상 국가(예: 인도, 브라질 등)의 신규 RSS 피드를 추가합니다.
2.  **[C]** Global 탭 상단에 여러 국가를 선택할 수 있는 UI (예: Multi-select dropdown)를 추가합니다.
3.  **[C]** `/api/global/insights` API가 `countries=US,CN,JP`와 같은 쿼리 파라미터를 받아, 선택된 국가들의 'perspectives'만 필터링하여 반환하도록 수정합니다.

#### **Discussion / Feedback**
- **[G → C]**: 다중 국가 선택 시, 'VS 카드' UI가 어떻게 변경되면 좋을지 UX 관점의 추가 논의가 필요합니다. (예: 3개국 이상 선택 시 UI)
- **[C → ?]**

---
### **1.3. UI/UX 고도화 (데스크톱, 다크모드)**
- **ID**: `FUTURE-TASK-03`
- **Owner**: `C` (구현), `G` (디자인/UX 가이드)
- **Priority**: `P3` (제안)

#### **Proposed Solution / Next Steps (G 제안)**
1.  **[G]** 데스크톱 전용 레이아웃 와이어프레임과 다크 모드 디자인 가이드(색상 팔레트)를 작성하여 공유합니다.
2.  **[C]** `tailwindcss-dark-mode` 플러그인 또는 CSS 변수를 사용하여 다크 모드 기능을 구현합니다.
3.  **[C]** 반응형 분기점(breakpoint)을 설정하고, 데스크톱 화면에 맞는 새로운 그리드 레이아웃 컴포넌트를 개발합니다.

#### **Discussion / Feedback**
- **[G → C]**: 데스크톱에서는 'Gravity Issue Bowl'을 어떻게 표현할지, 혹은 다른 방식의 시각화를 사용할지에 대한 논의가 필요합니다.

---

## ✨ 2. 신규 기능 (New Features)

---
### **2.1. 사용자 계정 및 개인화**
- **ID**: `FUTURE-TASK-04`
- **Owner**: `C` (인증/UI), `O` (DB정책)
- **Priority**: `P2` (제안)

#### **Proposed Solution / Next Steps (C/O 제안 필요)**
- *C와 O의 제안을 기다립니다.*

#### **Discussion / Feedback**
- **[G → C/O]**: 개인화 기능 구현 시, '사용자별 토픽 구독', '관심 카테고리 설정' 등의 데이터를 어떤 테이블 스키마로 관리할지 초기 설계 논의가 필요합니다.

---
### **2.2. 어드민 대시보드**
- **ID**: `FUTURE-TASK-05`
- **Owner**: `C`
- **Priority**: `P1` (제안)
- **Related Decision**: C의 `TEAM_REQUESTS_AND_PROPOSALS.md`

#### **Proposed Solution / Next Steps (C 제안 필요)**
- *C의 제안을 기다립니다.*

#### **Discussion / Feedback**
- **[G → C]**: 어드민에서 토픽을 수동으로 편집/수정하는 기능은 데이터 파이프라인의 자동화 로직과 충돌할 수 있습니다. 데이터 정합성을 어떻게 맞출지 논의가 필요합니다.

---

## 🛠️ 3. 데이터 파이프라인 및 백엔드 고도화

---
### **3.1. '스마트 피드' 수집 시스템**
- **ID**: `FUTURE-TASK-06`
- **Owner**: `C` (현재 데이터 파이프라인 담당)
- **Priority**: `P1` (제안)
- **Related Task**: `TASK-002` (WORK.md)

#### **Proposed Solution / Next Steps (C 제안 필요)**
- *C가 기존 `TASK-002`를 기반으로 구체적인 구현 방안을 제안할 것으로 예상됩니다.*

#### **Discussion / Feedback**
- **[G → C]**: 제가 초기에 제안했던 내용입니다. `MVP2_news_sources` 테이블에 `last_collected_at`, `total_articles_collected` 등의 통계 필드를 추가하는 스키마 변경이 필요할 수 있습니다.

---
### **3.2. 데이터 품질 검증 파이프라인**
- **ID**: `FUTURE-TASK-07`
- **Owner**: `C`
- **Priority**: `P2` (제안)
- **Related Decision**: C의 `TEAM_REQUESTS_AND_PROPOSALS.md`

#### **Proposed Solution / Next Steps (C 제안 필요)**
- *C의 제안을 기다립니다.*

#### **Discussion / Feedback**
- **[G → C]**: 데이터 품질 기준(예: 요약 최소/최대 길이, 유효 URL 등) 정의 시, UX에 영향을 미치는 요소들에 대해 함께 논의하면 좋겠습니다.

---
### **3.3. 파이프라인 모니터링 시스템**
- **ID**: `FUTURE-TASK-08`
- **Owner**: `O`
- **Priority**: `P2` (제안)
- **Related Decision**: C의 `TEAM_REQUESTS_AND_PROPOSALS.md`

#### **Proposed Solution / Next Steps (O 제안 필요)**
- *O의 제안을 기다립니다.*

#### **Discussion / Feedback**
- **[G → O]**: 어떤 데이터(예: 일일 토픽 생성 수, 번역/분석 실패율)를 시각화하면 좋을지, 데이터 분석가 관점에서 필요한 메트릭 목록을 정리해 드릴 수 있습니다.
