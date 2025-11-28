# Work In Progress

> 이 문서는 모든 작업의 역사를 기록하는 단일 소스입니다.
> `PRIORITY.md`(우선순위)와 `STATUS.md`(실시간 현황)와 연동됩니다.
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

## 대기중 (Todo)

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
