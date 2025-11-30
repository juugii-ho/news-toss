# Standard Format Templates

> 이 문서는 모든 AI 에이전트가 일관된 형태로 소통하고 기록하기 위한 표준 템플릿을 정의합니다.

---

## 1. 표준 메시지 헤더 (Standard Message Header)

> `INBOX.md`, `WORK.md` 등 모든 로그 및 메시지에 사용합니다.

**Format**: `[Agent][TASK/DT#][Hat][Status] 요약`

-   **Agent**: `C`, `G`, `O`
-   **TASK/DT#**: 관련 작업(`TASK-001`) 또는 의사결정(`DT-001`). 관련 없을 시 생략.
-   **Hat**: 현재 쓰고 있는 Hat. (예: `API Designer`, `Data Analyst`). 없으면 생략.
-   **Status**: `Progress` (진행), `Review` (검토요청), `Question` (질문), `Block` (차단됨), `Info` (정보공유)
-   **요약**: 한 줄 요약

**Example**:
`[C][TASK-003][API Designer][Review] /api/topics 엔드포인트 구조 검토 요청`

---

## 2. INBOX.md 메시지 템플릿

```markdown
- **[보내는에이전트 → 받는에이전트]** YYYY-MM-DD HH:MM `#tag`
  > 메시지 본문.
  > 여러 줄에 걸쳐 작성 가능.
  >
  > Related: path/to/file.ts:123
```
**To Use**: `docs/INBOX.md`의 해당 에이전트 `Unread` 섹션에 이 템플릿을 사용하여 추가합니다.

---

## 3. WORK.md 작업 템플릿

```markdown
---
### TASK-XXX: [작업 제목]

- **ID**: `TASK-XXX`
- **Title**: [작업 제목]
- **Owner**: `C` | `G` | `O`
- **Requestor**: `S`
- **Status**: `Todo` | `Doing` | `Review` | `Done`
- **Priority**: `P0` | `P1` | `P2` | `P3` (from PRIORITY.md)
- **Related Decision**: `DT-XXX`

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

## 4. DECISIONS.md 제안(DT) 템플릿

```markdown
## DT-XXX: [제안 제목]

**제안자**: `C` | `G` | `O`
**날짜**: YYYY-MM-DD
**관련 TASK**: `TASK-XXX`, `TASK-YYY`

### 문제 (Problem)
- 

### 제안 (Proposal)
- 

### Reviews (다른 Agent 의견)
- **[G's Review]** YYYY-MM-DD:
  - ✅ **찬성/반대**: [의견]
  - ⚠️ **주의/우려**: [내용]
  - 📝 **추가 제안**: [내용]

### Final Decision by S
- 
```
