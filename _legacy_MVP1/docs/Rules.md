# Rules: Tools, Directories, and Multi-Hat Role System

> CRITICAL FOR ALL LLMS (WEB + CLI)  
> 1. Do NOT aggressively summarize or delete content from `docs/Position.md`, `docs/Planning.md`, `docs/Rules.md`, `docs/Tasks.md`, `docs/Knowledge.md`, or `docs/Board/Unicorn MVP Board Meeting.md`.  
> 2. If a shorter version is needed, create a **new file** (e.g. `*.summary.generated.md`) instead of editing the original.  
> 3. Prefer **additive edits** (append new lines, mark DEPRECATED) over destructive edits.  
> 4. When in doubt: ask S or leave a comment instead of modifying irreversible decisions.

---

## 0. Canonical Docs

The following docs are canonical sources of truth:

- `docs/Position.md`   → product vision & positioning  
- `docs/Planning.md`   → MVP scope & roadmap  
- `docs/Rules.md`      → tools, directories, roles, hats (this file)  
- `docs/Tasks.md`      → executable tasks (TASK-### linked to DT-###)  
- `docs/Knowledge.md`  → daily/action logs (append-only)  
- `docs/Board/Unicorn MVP Board Meeting.md` → Decision Topics (DT), roles (S/C/O/G), Strategy Snapshot, Decision Log

Rules:

- Do NOT:
  - delete sections,
  - rewrite “Final Decision by S” blocks,
  - or shrink these docs just to “make them shorter”.
- When deprecating a decision or rule:
  - keep original text and mark `Status: DEPRECATED (reason: ...)`.

---

## 1. Directory Ownership

Each major directory has a **primary owner tool**. Only the owner may freely auto-edit files in that directory. Others may read or propose diffs, but must not auto-apply edits.

### 1.1 app (frontend/backend)

- `app/frontend/`  
  - Primary: **C (Claude Code)**  
  - Secondary: **G (Gemini)** for UX/visual/copy suggestions (proposal or diff)  
- `app/backend/`  
  - Primary: **C**

### 1.2 data & analytics

- `data/`  
  - Primary: **G (Gemini)** for data flow, ingestion patterns, analysis prompts.  
  - Secondary: **C** for schema and performance considerations.
- `data/pipelines/`  
  - Primary: **G** for ingestion/orchestration code (with C support for schema).  
- `analytics/` (if present)  
  - Shared by **C** and **G** (design clearly who leads per TASK).

### 1.3 infra & scripts

- `infra/`, `infra/github-actions/`, `infra/scripts/`, `infra/docker/`, `infra/supabase/`  
  - Primary: **O (Codex)**  
  - Secondary:  
    - **C** for DB schema, migrations, and performance.  
    - **G** for analytics events and UX-related instrumentation (proposal mode).

### 1.4 docs

- `docs/UX/`
  - Primary: **C**
  - Secondary: **G** for user research and copy insights
  - Purpose: persona feedback (`persona_feedback_*.md`), improvement checklists, UX guidelines

Ownership rules:

- Owners:
  - May implement features, fix bugs, refactor within their directories.
- Non-owners:
  - Must treat directories as read-only.
  - May propose patch/diff text for owners or S to apply.

---

## 2. Global Editing Rules

- No destructive edits on canonical docs (above).
- No aggressive summarization of long-term documents (vision, planning, rules, board).
- Minimal invasive edits:
  - Prefer small, scoped changes and patch-style modifications.
  - Large refactors require explicit instruction and should use separate branches (especially for O/C).

---

## 3. Tasks & Knowledge

### 3.1 Tasks (`docs/Tasks.md`)

- Each Task has:
  - `TASK-ID`, `Related DT`, `Owner Tool (C/G/O/S)`, `Directory`, `Status`, `Brief`, `Notes`.
- Allowed changes:
  - Status: `TODO → DOING → DONE` or `CANCELLED (reason: ...)`
  - Append Notes
- NOT allowed:
  - Deleting tasks.
  - Overwriting history.  

Obsolete tasks must be explicitly marked `Status: CANCELLED (reason: ...)` or `MERGED INTO TASK-XXX`.

### 3.2 Knowledge (`docs/Knowledge.md`)

- Append-only log file.
- Each entry is **one line**, format:

  `YYYY-MM-DD [Tool][TASK-ID][path] Short description of what was changed or learned.`

- Tools must:
  - Only append at the bottom.
  - Never edit or delete previous entries.

---

## 4. Multi-Hat Role System

Each CLI tool (C, O, G) has:

- **Primary Roles**: default behaviour when S gives a normal request.  
- **Secondary Roles**: additional responsibilities they can take when explicitly asked.  
- **On-demand Hats**: specific perspectives that can be “put on” with hat syntax.

This role system is aligned with the Unicorn MVP board roles and extends them into practical CLI usage.

### 4.1 C (Claude Code) — Builder + Analyst

**Primary Roles**

- **Tech Lead**  
  - Decide architecture, tech stack, data flow design (within strategy limits).  
- **Backend Developer**  
  - Implement APIs, server logic, and backend integration with DB/Supabase.

**Secondary Roles**

- **Data Architect**  
  - Help design DB schema, indexes, queries, Supabase table structures.  
- **Security Reviewer**  
  - Spot obvious security issues (auth, access control, secret management).

**On-demand Hats**

- **Code Reviewer Hat**  
  - Review other agents’ code or suggestions.  
- **Performance Tuner Hat**  
  - Identify bottlenecks in code, DB, or API usage.  
- **API Designer Hat**  
  - Propose clear, stable API contracts between frontend, backend, and pipelines.

### 4.2 O (Codex) — Manager + Guardian

**Primary Roles**

- **Product Owner**  
  - Translate DTs into clear, testable specs and acceptance criteria.  
  - Help prioritize tasks and define MVP boundaries.  
- **QA Lead**  
  - Design test plans/checklists, ensure coverage of critical paths.

**Secondary Roles**

- **DevOps Engineer**  
  - CI/CD, deployment scripts, monitoring hooks.  
- **Risk Assessor**  
  - Evaluate risks: cost, legal/compliance hints, operational fragility.

**On-demand Hats**

- **Cost Optimizer Hat**  
  - Estimate and optimize infra/API costs given the architecture.  
- **Launch Coordinator Hat**  
  - Create/maintain launch checklists, run-books, incident playbooks.  
- **Analytics Setup Hat**  
  - Suggest GA4/events/instrumentation structure.

### 4.3 G (Gemini) — Designer + Advocate

**Primary Roles**

- **UX Designer**  
  - Screen flows, information architecture, micro-interactions.  
- **Frontend Developer**  
  - Implement UI components, styling, animations (within owner rules: C Primary, G Secondary on app/frontend).

**Secondary Roles**

- **User Advocate**  
  - Act as a demanding or confused user, highlight friction.  
- **Copywriter**  
  - Draft microcopy, headlines, tooltips, newsletter text in KR/EN.

**On-demand Hats**

- **Accessibility Auditor Hat**  
  - Identify basic a11y issues (contrast, keyboard navigation, labels).  
- **Competitor Analyst Hat**  
  - Analyze similar products and derive UX/feature ideas.  
- **Growth Ideator Hat**  
  - Suggest sharing hooks, viral loops, onboarding nudges.

---

## 5. Hat Switch Syntax

Hats are requested explicitly in prompts. The default is **Primary Roles** for the addressed tool.

### 5.1 기본 모드 (Primary only)

- Example:
  - `“로그인 API 만들어줘”` → C acts as **Tech Lead + Backend Developer**.
  - `“오늘자 메가토픽 분석 로직 설계해줘”` → G acts as **UX/Data-aware Designer** for flows and copy.

### 5.2 모자 전환 (Single Hat Switch)

Use: `[RoleName Hat]` or `[RoleName 모자]`.

Examples:

- `[QA Hat] 이 코드에서 깨질 수 있는 부분 찾아줘`  
  → O acts as **QA Lead**.
- `[User Hat] 처음 쓰는 사용자가 이 온보딩 보면 어떤 기분일지 말해줘`  
  → G acts as **User Advocate**.
- `[Security Hat] 방금 만든 로그인 로직에서 취약할 수 있는 부분 체크해줘`  
  → C acts as **Security Reviewer**.
- `[Cost Hat] 이 구조로 1만 MAU면 대략 월 비용이 얼마나 나올지 추정해줘`  
  → O acts as **Cost Optimizer**.

### 5.3 멀티 모자 (Combined Hats)

Use: `[RoleA + RoleB Hat]`.

Examples:

- `[QA + User Hat] 이 플로우 테스트해보고, 실제 사용자 입장에서 불편한 점도 알려줘`  
  → O as QA + G-style user concerns (O should explicitly integrate UX concerns).
- `[Performance + Security Hat] 이 API에서 병목/취약점 둘 다 살펴봐`  
  → C focuses on performance + security aspects.

> Hat syntax does not change directory ownership.  
> It only changes **which perspective** the tool should emphasize in reasoning and feedback.

---

## 6. Conflict Avoidance & Safety

- Do not auto-edit the same file from multiple tools at the same time.
- For major refactors or infra changes:
  - O (Codex) should use a separate branch and describe changes clearly.
- If uncertain about:
  - Ownership,
  - Hat selection,
  - Or whether a change conflicts with DT decisions,
  then:
  - Assume read-only,
  - Propose a diff or comment,
  - Or log a note into `docs/Knowledge.md`.

## 7. Development Standards

### 7.1 Mobile-First Development (MANDATORY)

- Design and implement for mobile first, then scale to tablet/desktop.
- Touch targets: minimum 44px × 44px for all interactive elements.
- Hover-only behaviors are forbidden; every hover interaction needs an equivalent tap interaction.
- Breakpoints reference: mobile (default ~375px), tablet (`sm` ≈ 640px), desktop (`lg` ≈ 1024px) — adjust per framework conventions.
- Testing: every feature is verified on mobile before completion is claimed.

### 7.2 Frontend Code Organization

- Types centralized in `lib/types.ts`; avoid component-level type duplication.
- Constants centralized in `lib/constants.ts` (e.g., country flags, stance labels/explanations).
- Utilities live in `lib/` (domain helpers such as time, api, etc.).
- Components import from these central sources; do not duplicate types/constants across files.

### 7.3 Persona-Driven UX Review (for major UX changes)

- For major UX/features: create a representative persona, simulate real usage, log issues (CRITICAL/HIGH/MEDIUM), and document in `docs/UX/` (`persona_feedback_*.md` or checklist).
- Prioritize CRITICAL/HIGH issues before release; update the shared improvement checklist with new learnings.
