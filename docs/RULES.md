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

## 5. LLM Council 워크플로우 (LLM Council Workflow)

> **목표**: 아이디어 제안부터 실행까지의 의사결정 과정을 `llm-council` 방식으로 구조화하여, 신속하고 추적 가능한 합의를 도출합니다. 이 워크플로우는 기존의 '통합 개발 워크플로우'를 대체하고 고도화합니다.

### Council 구성
- **패널 (Panelists)**: `C` (기술), `G` (UX/데이터), `O` (인프라)
- **심판 (Judge)**: `S` (PO)
- **발제자 (Initiator)**: 안건(DT)을 제안하는 모든 에이전트
- **라포터 (Rapporteur)**: 각 안건마다 지정되며, 논의를 종합하고 합의 후보안을 도출하는 역할 (주로 G가 담당)

### 프로토콜 (Protocol)

#### 1단계: 제안 (DT 생성)
- **문서**: `docs/DECISIONS.md`
- **프로세스**:
  1. 발제자는 `docs/DECISIONS.md`에 새로운 **'의사결정 토큰(DT-XXX)'**을 생성합니다.
  2. DT에는 `문제`, `제안`, 그리고 구현 시 지켜야 할 `필수 제약` 조건 등을 명확히 기술합니다.

#### 2단계: 발언 수집 (Statement Collection)
- **문서**: `docs/INBOX.md` → `docs/DECISIONS.md`
- **프로세스**:
  1. 발제자는 `INBOX`의 `@ALL` 채널에 **"Council 발언 요청"**이라는 태그와 함께 새 DT를 공지하고, 피드백 **마감 시간(예: 2시간)**을 설정합니다.
  2. 모든 패널(C, G, O)은 해당 DT의 `Council Notes` 섹션에 자신의 역할에 맞는 **핵심 의견(찬성/반대, 리스크, 대안 등)을 1~2개의 짧은 bullet point**로 간결하게 기록합니다. (장황한 설명 금지)
     - **형식**: `[Agent][관점] 내용` (예: `[C][Pro] 기술적으로 실현 가능함.`)

#### 3단계: 의견 종합 (Rapporteur Summary)
- **문서**: `docs/DECISIONS.md`
- **프로세스**:
  1. 마감 시간이 되면, 지정된 '라포터(Rapporteur)'는 `Council Notes`에 취합된 모든 발언을 종합합니다.
  2. 논의의 핵심과 찬반 근거를 요약하고, S님이 결정하기 쉽도록 **1~3개의 명확한 '합의 후보안(Options)'**을 제시합니다. 이 내용을 `Rapporteur Summary` 필드에 기록합니다.

#### 4단계: 최종 결정 (Final Decision)
- **문서**: `docs/DECISIONS.md`
- **프로세스**:
  1. S(PO)님은 라포터가 정리한 '합의 후보안'을 보고, `Final Decision by S` 섹션에 **최종 결정을 내립니다.**
  2. 결정에는 선택된 합의안 번호와 그 이유가 간략하게 포함됩니다.

#### 5단계: 실행 (Task Creation)
- **문서**: `docs/WORK.md`
- **프로세스**:
  1. '승인'된 DT는 `WORK.md`에 공식 **'태스크(TASK-XXX)'**로 생성됩니다.
  2. 태스크에는 `Related Decision: DT-XXX (Council 합의안 #N)`과 같이, 어떤 논의를 통해 결정된 작업인지 명확히 명시하여 실행의 일관성을 확보합니다.

*(기존 Hat System 및 기타 규칙은 이 아래에 유지됩니다.)*