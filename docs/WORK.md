# Work In Progress

> 이 문서는 모든 작업의 역사를 기록하는 단일 소스입니다.
> `PRIORITY.md`(우선순위)와 `STATUS.md`(실시간 현황)와 연동됩니다.
> 장기적인 비전과 계획은 `docs/ROADMAP.md`를 참고하세요.
> `docs/TEMPLATES.md`의 형식을 준수하여 작성합니다.

---

## 템플릿 (Template)
> 새 Task 추가 시 아래 템플릿을 복사하여 '대기중 (Todo)' 섹션에 추가하세요.

```markdown
---
### TASK-XXX: [작업 제목]

- **ID**: `TASK-XXX`
- **Owner**: `C` | `G` | `O`
- **Status**: `Todo` | `Doing` | `Review` | `Done`
- **Priority**: `P0` | `P1` | `P2` | `P3`
- **Related Decision**: `DT-XXX`
- **Sync**: [ ] PRIORITY/STATUS 반영 완료

#### 완료의 정의 (Definition of Done - DoD)
- [ ] [완료 조건 1]
- [ ] [완료 조건 2]

#### 작업 기록 (Work Log)
- YYYY-MM-DD `[Agent][TASK#][Hat][Status] 로그 내용`

#### 검토 기록 (Review Log)
- YYYY-MM-DD `[Agent][TASK#][Hat][Status] 검토 의견`
---
```

---
---
> **아래부터 실제 작업 내용을 기록합니다.**

## 진행중 (In Progress)

---
### TASK-001: 레거시 자산 선별 마이그레이션
- **ID**: `TASK-001`
- **Owner**: `G`
- **Status**: `Done`
- **Priority**: `P1`
- **Related Decision**: `(없음)`
- **Sync**: [x] PRIORITY/STATUS 반영 완료

#### 완료의 정의 (Definition of Done - DoD)
- [x] `_legacy_MVP1`에서 재사용할 자산 목록 정의 완료
- [x] 정의된 파이썬 스크립트를 `MVP2` 구조에 맞게 1차 이전 완료
- [x] 이전된 스크립트 리팩토링 및 검증 완료 (S의 지시에 따라 Supabase 기존 데이터 활용으로 검증 대체)
- [ ] 마이그레이션 완료 후 `_legacy_MVP1`의 최종 처리 방안 결정

#### 작업 기록 (Work Log)
- 2025-11-29 `[G][TASK-001][Data Analyst][Progress] _legacy_MVP1의 모든 핵심 파이썬 스크립트를 MVP2/data/pipelines/로 이동 완료.`
- 2025-11-29 `[G][TASK-001][Data Analyst][Progress] MVP2/data/pipelines/requirements.txt 파일 생성 완료.`
- 2025-11-29 `[G][TASK-001][Default][Review] 1차 스크립트 마이그레이션 완료. 리팩토링 계획 검토 요청.`
- 2025-11-28 `[G][TASK-001][Data Engineer][Done] 'rss_collector.py' 리팩토링 완료 및 검증 (S의 지시에 따라 Supabase 기존 데이터 활용).`

#### 검토 기록 (Review Log)
- <!-- YYYY-MM-DD `[Agent][TASK#][Hat][Status] 검토 의견` -->
---
---
### TASK-008: Supabase 연동 및 최신 배치 데이터 노출

- **ID**: `TASK-008`
- **Owner**: `O`
- **Status**: `Todo`
- **Priority**: `P1`
- **Related Decision**: `(없음)`
- **Sync**: [ ] PRIORITY/STATUS 반영 완료

#### 완료의 정의 (Definition of Done - DoD)
- [ ] `/api/global/insights`에서 최근 24시간 `mvp2_megatopics` 실데이터가 UI(Global/VS)로 노출됨
- [ ] `/api/local/trends`에서 최근 24시간 `MVP2_local_topics` 실데이터가 UI(Local)로 노출됨
- [ ] `/api/local/topics/[id]`로 상세 데이터 조회 가능, 로컬 상세 페이지에 연결됨
- [ ] 실데이터 미존재 시 목업 폴백으로 UI 깨짐 없음

#### 작업 기록 (Work Log)
- 2025-11-29 `[O][TASK-008][Default][Plan] API를 mvp2_megatopics/mvp2_topics 최신 24h 조회로 수정. 실데이터 확인 필요.`
- 2025-11-29 `[G][TASK-008][Default][Comment] **주의:** 이 태스크는 C에게 할당된 TASK-007, TASK-009와 중복될 수 있습니다. API 구현은 C의 역할이므로, 역할 조정을 제안합니다.

#### 검토 기록 (Review Log)
- <!-- YYYY-MM-DD `[Agent][TASK#][Hat][Status] 검토 의견` -->
---

## 대기중 (Todo)

---
### TASK-010: 데이터 확장 - Global 탭 국가 확장 리서치
- **ID**: `TASK-010`
- **Owner**: `G`
- **Status**: `Todo`
- **Priority**: `P2`
- **Related Decision**: `FUTURE-TASK-02` (in PLANNING_SESSION.md)
- **Sync**: [ ] PRIORITY/STATUS 반영 완료

#### 완료의 정의 (Definition of Done - DoD)
- [ ] 확장 대상 국가 (예: 인도, 브라질, 스페인 등) 선정
- [ ] 각 국가별 주요 언론사 3-5곳의 RSS 피드 URL 리서치 및 유효성 검증
- [ ] 리서치 결과를 `packages/config/rss_feeds.json`에 추가 (is_active: false 상태로)

#### 작업 기록 (Work Log)
- 2025-11-29 `[G][TASK-010][Data Analyst][Assign] 'Global 탭 국가 확장' 기능을 위한 데이터 리서치 태스크 생성.`

#### 검토 기록 (Review Log)
- <!-- YYYY-MM-DD `[Agent][TASK#][Hat][Status] 검토 의견` -->
---
---
### TASK-009: 글로벌 토픽 세부 페이지 구현
- **ID**: `TASK-009`
- **Owner**: `C`
- **Status**: `Todo`
- **Priority**: `P1`
- **Related Decision**: `(없음)`
- **Sync**: [ ] PRIORITY/STATUS 반영 완료

#### 완료의 정의 (Definition of Done - DoD)
- [ ] `app/frontend/app/global/[id]/page.tsx` 경로에 페이지 컴포넌트 생성
- [ ] 기존 `VsCardSection` 컴포넌트를 활용하여 'VS 카드' UI 구현
- [ ] API(`GET /api/global/insights/[id]`)를 통해 실제 데이터를 받아와 페이지에 렌더링

#### 작업 기록 (Work Log)
- 2025-11-29 `[G][TASK-009][Default][Assign] S님의 요청에 따라 C에게 태스크 할당.`

#### 검토 기록 (Review Log)
- <!-- YYYY-MM-DD `[Agent][TASK#][Hat][Status] 검토 의견` -->
---
---
### TASK-007: 로컬 토픽 세부 페이지 구현
- **ID**: `TASK-007`
- **Owner**: `C`
- **Status**: `Doing`
- **Priority**: `P1`
- **Related Decision**: `(없음)`
- **Sync**: [x] PRIORITY/STATUS 반영 완료

#### 완료의 정의 (Definition of Done - DoD)
- [x] G가 설계한 API 명세(`GET /api/local/topics/[id]`) 백엔드 구현
- [x] G가 설계한 목업(`outputs/local_detail_mockup.html`) 기반 프론트엔드 UI 구현
- [x] Gravity Issue Bowl의 버블 클릭 시 해당 상세 페이지로 이동 기능 구현
- [ ] **[NEW]** 실제 기사 리스트 연결 (현재 Mock Data 사용 중)

#### 작업 기록 (Work Log)
- 2025-11-29 `[G][TASK-007][UX Designer][Done] 로컬 토픽 세부 페이지에 대한 UI 목업 및 API 명세서 설계 완료.`
- 2025-11-29 `[G][TASK-007][Default][Assign] C에게 구현 태스크 할당.`
- 2025-11-29 `[C][TASK-007][Frontend][Doing] UI 기본 구현 완료. 현재 기사 리스트는 Mock Data 사용 중.`

#### 검토 기록 (Review Log)
- 2025-11-29 `[G][TASK-007][Default][Review] 상세 페이지 진입 확인. 기사 리스트가 하드코딩되어 있어 실제 DB 연결 필요.`
- 2025-11-29 `[G][TASK-010][Data][Done] Global API 및 VS Card를 위한 DB 스키마 업데이트 완료 (title_ko, stances, article_count 등 추가).`
---
---
### TASK-006: 데이터 파이프라인 - 토픽 카테고리 분류 로직 구현
- **ID**: `TASK-006`
- **Owner**: `C`
- **Status**: `Todo`
- **Priority**: `P1`
- **Related Decision**: `DT-XXX` (Local Tab UI 변경에 따름)
- **Sync**: [ ] PRIORITY/STATUS 반영 완료

#### 완료의 정의 (Definition of Done - DoD)
- [ ] LLM을 사용하여 토픽(`title_ko`, `summary_ko`)을 "정치", "경제", "사회" 등 7개 카테고리로 분류하는 스크립트 작성
- [ ] 분류된 카테고리를 `LocalTopic` 테이블에 업데이트하는 로직 구현
- [ ] 스크립트 실행 및 검증

#### 작업 기록 (Work Log)
- 2025-11-28 `[G][TASK-006][Data Engineer][Blocked] TASK-003의 Supabase 연결 문제로 인해 작업 시작 불가.`
- 2025-11-28 `[S][TASK-006][PO][Assign] S의 지시에 따라 담당자를 G에서 C로 변경.`

#### 검토 기록 (Review Log)
- <!-- YYYY-MM-DD `[Agent][TASK#][Hat][Status] 검토 의견` -->
---
---
### TASK-003: 데이터 파이프라인 - LLM 번역 스크립트 구현
- **ID**: `TASK-003`
- **Owner**: `C`
- **Status**: `Todo`
- **Priority**: `P0`
- **Related Decision**: `(없음)`
- **Sync**: [ ] PRIORITY/STATUS 반영 완료

#### 완료의 정의 (Definition of Done - DoD)
- [ ] `llm_translator.py` 스크립트 작성 완료
- [ ] Supabase에서 번역 필요한 기사 조회, LLM 번역, DB 업데이트 로직 구현
- [ ] 스크립트 실행 및 검증 완료

#### 작업 기록 (Work Log)
- 2025-11-28 `[G][TASK-003][Data Engineer][Blocked] Supabase Python 클라이언트의 'SyntaxError'로 인해 작업 중단. O에게 기술 지원 요청.`
- 2025-11-28 `[S][TASK-003][PO][Assign] S의 지시에 따라 담당자를 G에서 C로 변경.`

#### 검토 기록 (Review Log)
- <!-- YYYY-MM-DD `[Agent][TASK#][Hat][Status] 검토 의견` -->
---
### TASK-004: 데이터 파이프라인 - LLM 스탠스 분석 스크립트 구현
- **ID**: `TASK-004`
- **Owner**: `C`
- **Status**: `Todo`
- **Priority**: `P0`
- **Related Decision**: `(없음)`
- **Sync**: [ ] PRIORITY/STATUS 반영 완료

#### 완료의 정의 (Definition of Done - DoD)
- [ ] `llm_stance_analyzer.py` 스크립트 작성
- [ ] 스크립트 실행 및 검증

#### 작업 기록 (Work Log)
- 2025-11-28 `[G][TASK-004][Data Engineer][Blocked] TASK-003의 Supabase 연결 문제로 인해 작업 시작 불가.`
- 2025-11-28 `[S][TASK-004][PO][Assign] S의 지시에 따라 담당자를 G에서 C로 변경.`

#### 검토 기록 (Review Log)
- <!-- YYYY-MM-DD `[Agent][TASK#][Hat][Status] 검토 의견` -->
---
### TASK-005: 데이터 파이프라인 - 임베딩 생성 스크립트 구현
- **ID**: `TASK-005`
- **Owner**: `C`
- **Status**: `Todo`
- **Priority**: `P0`
- **Related Decision**: `(없음)`
- **Sync**: [ ] PRIORITY/STATUS 반영 완료

#### 완료의 정의 (Definition of Done - DoD)
- [ ] `embedding_generator.py` 스크립트 작성
- [ ] 스크립트 실행 및 검증

#### 작업 기록 (Work Log)
- 2025-11-28 `[G][TASK-005][Data Engineer][Blocked] TASK-003의 Supabase 연결 문제로 인해 작업 시작 불가.`
- 2025-11-28 `[S][TASK-005][PO][Assign] S의 지시에 따라 담당자를 G에서 C로 변경.`

#### 검토 기록 (Review Log)
- <!-- YYYY-MM-DD `[Agent][TASK#][Hat][Status] 검토 의견` -->
---

<!--

## 완료 (Done)
<!-- 
---
### TASK-XXX: [작업 제목]
...
---
-->
