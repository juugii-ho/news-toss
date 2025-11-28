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

*(기존 Hat System 및 기타 규칙은 이 아래에 유지됩니다.)*