# Global Rules for All Projects

> 이 규칙은 모든 프로젝트에 공통으로 적용되는 S의 글로벌 설정입니다.

---

## 0. Critical Editing Behavior

### 0.1 No Destructive Edits
- **NEVER** delete, summarize, or aggressively rewrite content in:
  - `docs/VISION.md`
  - `docs/RULES.md`
  - `docs/DECISIONS.md`
  - `docs/WORK.md`
  - `docs/CHANGELOG.md`
  - Any file marked as "source of truth"
- If a shorter version is needed, create a **new file** (e.g., `*.summary.generated.md`)

### 0.2 Additive Edits Only
- Prefer **appending** new content over modifying existing content
- When updating status: change status field only, preserve all other text
- When deprecating: mark as `Status: DEPRECATED (reason)`, keep original text

### 0.3 No Aggressive Summarization
- LLMs tend to shorten and delete. **Resist this urge.**
- If user asks for summary, write it in a **separate file**
- Never "make it shorter" unless explicitly asked

---

## 1. AI Collaboration Velocity Context

> This is NOT a traditional human team. Adjust expectations accordingly.

### 1.1 Time Estimates
- Simple CRUD API: 1-2 hours
- Page UI implementation: 2-4 hours
- New feature pipeline: half-day to one day
- Full MVP: 1-2 weeks

### 1.2 Processes That Don't Apply
- Sprint planning meetings → replaced by document sharing
- Code review waiting → ask another LLM immediately
- Design handoff → implement and adjust directly
- Documentation phase → code is documentation

### 1.3 Forbidden Suggestions
- "This will take 3 months" → use AI-adjusted estimates
- "You need to hire a developer" → solo founder + AI team
- "Consult with legal/design team" → handle post-launch if needed
- "Schedule a meeting" → async document communication

---

## 2. Constraints Awareness

> Always check project's `docs/VISION.md` for specific constraints.

**Common constraints across S's projects:**
- Single developer (S) + AI assistants
- Cost sensitivity: optimize LLM API usage
- Free tier infrastructure preferred (Supabase, Vercel, GitHub Actions)
- No external contractors unless explicitly approved

---

## 3. Logging Format

When writing to `docs/CHANGELOG.md`:
```
YYYY-MM-DD [Agent][Category] Short description
```

**Examples:**
- `2025-11-28 [C][FEAT] Implemented hero layout`
- `2025-11-28 [G][FIX] Fixed null filter in topics pipeline`

**Categories**: `FEAT`, `FIX`, `DOCS`, `REFACTOR`, `INFRA`, `DATA`, `UX`

---

## 4. Directory Ownership (Default Pattern)

> Check project's `docs/RULES.md` for project-specific assignments.

**General pattern:**
- `app/frontend/`, `app/backend/` → C (Claude Code)
- `data/`, `analytics/`, `notebooks/` → G (Gemini CLI)
- `infra/`, `.github/` → O (Codex CLI)

**Non-owner directories**: Read-only, propose changes only

---

## 5. Session Protocol

### Session Resume (After Interruption)
**If session was interrupted (token limit, crash, etc.), immediately:**
1. `cat docs/PRIORITY.md` - What should I do now?
2. `cat docs/STATUS.md` - What was I doing? What are others doing?
3. `cat docs/CHANGELOG.md | head -50` - What changed while I was away?

**Then announce:**
```
[Agent] Session resumed.
- PRIORITY: Currently P0 is [...]
- STATUS: I was working on [...]
- CHANGELOG: [Other Agent] changed [...]
- Continuing from [next step]
```

### Before Starting Work
1. Read `docs/STATUS.md` - Check who's working on what
2. Read `docs/PRIORITY.md` - Check task priorities
3. Read `docs/WATCHLIST.md` - Check for critical file changes

### While Working
1. Update `docs/STATUS.md` with current progress
2. Avoid files in "In Progress" by other agents

### After Completing Work
1. Move task from "In Progress" to "Recently Completed" in STATUS.md
2. Add summary to `docs/CHANGELOG.md`
3. If modified WATCHLIST files, mention in CHANGELOG

---

## 6. Decision Making

- All major decisions → `docs/DECISIONS.md` with `DT-XXX` format
- Final decisions by S only
- Agents can propose, S approves

---

## 7. Safety

- Never auto-edit canonical docs without explicit request
- Never override other agents' ownership
- If unsure, propose in text instead of direct edit
