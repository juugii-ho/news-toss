# Main Rules

> 이 문서는 MVP2 프로젝트의 모든 AI 에이전트가 따라야 할 핵심 규칙을 정의합니다.

---

## 1. 절대 규칙 (Absolute Rules)

**이 섹션의 규칙은 다른 모든 지침에 우선하는 최상위 명령입니다.**

### SYS-001: LLM 모델 사용 지정
-   **Rule**: 모든 AI 에이전트는 `gemini-1.5-flash` 모델을 사용해서는 안 됩니다.
-   **Directive**: 모든 텍스트 생성, 분석, 요약 작업에는 **`gemini-2.5-flash`** (또는 S가 지정하는 다른 모델)를 사용해야 합니다. 타임아웃은 **`300초`** 이며, 입력 토큰 한도는 **`1,048,576`** 출력 토큰 한도는 **`65,536`**입니다.

---

## 2. 세션 및 작업 프로토콜 (Session & Task Protocol)

### 세션 시작 (필수)
1.  **컨텍스트 동기화 (Context Sync)**: `docs/STATUS.md` 파일의 `Context Sync Marker` 섹션에 `Synced: [시간] by [본인]` 로그를 남겨, 모든 에이전트가 최신 상태에서 작업을 시작함을 보장합니다.
2.  **우선순위 및 상태 확인**: `docs/PRIORITY.md`와 `docs/STATUS.md`를 순서대로 확인하여, 가장 시급한 작업과 다른 에이전트의 현재 상태를 파악합니다.
3.  **받은편지함 확인 (Check Inbox)**: `docs/INBOX.md` 파일을 확인하여 자신에게 온 새 메시지(`Unread` 섹션)가 있는지 확인하고, 필요한 경우 먼저 대응합니다.

### 작업 흐름 (Task Flow)
-   모든 작업은 **`PRIORITY.md` → `WORK.md` → `STATUS.md`** 순서로 흐릅니다.
    1.  새로운 작업은 `PRIORITY.md`에 먼저 등록됩니다.
    2.  작업을 시작할 때, `WORK.md`에 상세 내용을 기록하고 `Doing` 상태로 변경합니다.
    3.  현재 진행 중인 작업의 실시간 현황은 `STATUS.md`에 상세히 기록합니다. (`지시 반영 여부` 필드 필수 작성)

### 세션 종료
-   세션을 종료하기 전, `STATUS.md`를 최종 상태로 업데이트하고, 하루 동안의 **핵심 변경사항, 주요 차단요인, 내일 진행할 첫 작업**에 대해 3줄 요약 로그를 `WORK.md`의 해당 Task에 남깁니다.

---

## 3. 소통 및 기록 규칙 (Communication & Logging)

### 표준 메시지 헤더 (Standard Message Header)
-   `INBOX.md`, `WORK.md` 등 모든 기록은 다음 표준 헤더 형식을 사용해야 합니다.
-   **Format**: `[Agent][TASK/DT#][Hat][Status] 요약`
-   **Example**: `[C][TASK-003][API Designer][Review] /api/topics 엔드포인트 구조 검토 요청`

### 양방향 링크 (Bidirectional Linking)
-   `DECISIONS.md`에서 새로운 DT를 작성할 때는, 관련된 `TASK#`를 반드시 명시해야 합니다.
-   `WORK.md`에서 Task를 진행할 때는, 해당 Task의 근거가 되는 `DT#`를 반드시 명시해야 합니다.

### Watchlist 알림
-   `WATCHLIST.md`(신설 필요)에 등록된 중요 파일을 수정할 경우, `STATUS.md`와 `WORK.md` 로그에 `"Watchlist: [파일명]"`을 포함하여 다른 에이전트들이 변경사항을 즉시 인지할 수 있도록 합니다.

---

## 4. 역할 및 소유권 (Roles & Ownership)

-   **C (Claude Code)**: `app/`, `packages/`
-   **G (Gemini CLI)**: `data/`, `docs/`, `outputs/`
-   **O (Codex CLI)**: `infra/`, `.github/`, Root infrastructure files

---

## 5. 통합 개발 워크플로우 (Unified Development Workflow)

> **목표**: 아이디어 제안부터 작업 완료까지의 과정을 표준화하여, 모든 팀원이 동일한 프로세스를 따르도록 합니다. 이 워크플로우는 `PLANNING_SESSION.md`와 같은 임시 문서를 대체하며, `DECISIONS.md`와 `WORK.md`를 중심으로 작업을 관리합니다.

### 1단계: 제안 (Proposal)
- **문서**: `docs/DECISIONS.md`
- **프로세스**:
  1. 새로운 기능, 아키텍처 변경, 주요 정책 제안 등 모든 아이디어는 `docs/DECISIONS.md`에 **신규 '의사결정 토큰(DT-XXX)'**으로 작성하여 제안합니다.
  2. 제안자는 '문제(Problem)'와 '제안(Proposal)' 섹션을 구체적으로 작성합니다.

### 2단계: 논의 (Discussion)
- **문서**: `docs/INBOX.md` → `docs/DECISIONS.md`
- **프로세스**:
  1. 제안자는 `docs/INBOX.md`의 `@ALL` 채널에 **새로운 DT가 등록되었음을 알리고, 팀의 검토를 요청**합니다. (`[G][DT-004][Proposal] 신규 기능 제안 검토 요청`)
  2. 모든 팀원(C, G, O)은 해당 DT를 읽고, 기술적 검토 의견이나 피드백을 DT의 `Reviews` 섹션에 직접 기록합니다.

### 3단계: 결정 (Decision)
- **문서**: `docs/DECISIONS.md` → `docs/WORK.md`
- **프로세스**:
  1. S(PO)는 제안 내용과 모든 팀원의 검토 의견을 바탕으로 `Final Decision by S` 섹션에 **최종 결정을 내립니다. (승인/보류/반려)**
  2. **승인된 경우**, 제안자 또는 S는 `docs/WORK.md`에 해당 DT를 이행하기 위한 **신규 '태스크(TASK-XXX)'를 생성**합니다.
  3. 생성된 태스크에는 근거가 되는 의사결정을 명시하기 위해 `Related Decision: DT-XXX` 필드를 반드시 포함합니다.

### 4단계: 실행 (Execution)
- **문서**: `docs/WORK.md` & `docs/INBOX.md`
- **프로세스**:
  1. 태스크 담당자는 `WORK.md`에서 자신의 태스크 상태를 `Todo` → `Doing`으로 변경하고, 모든 진행 상황을 `Work Log`에 상세히 기록합니다.
  2. 작업 중 다른 팀원의 도움이 필요할 경우, `TASK-ID`를 명시하여 `INBOX.md`를 통해 소통합니다.
  3. 작업이 완료되면, 상태를 `Review` 또는 `Done`으로 변경하고 `STATUS.md`를 업데이트합니다.

*(기존 Hat System 및 기타 규칙은 이 아래에 유지됩니다.)*