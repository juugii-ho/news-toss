# Changelog

> 모든 중요한 변경사항을 시간순으로 기록합니다.
> STATUS.md의 24시간 지난 항목이 여기로 아카이브됩니다.

---

## Format

```
### YYYY-MM-DD

- **[Agent][Category]** Brief description
  - Details if needed
  - Related files: path/to/file
```

**Categories**: `FEAT`, `FIX`, `DOCS`, `REFACTOR`, `INFRA`, `DATA`, `UX`

---

## 2025-11-28

### Added
- **[G][INFRA]** Created MVP2 project boilerplate
  - Directory structure: app/, packages/, data/, infra/, docs/
  - Core documentation: VISION, RULES, WORK, DECISIONS, ARCHITECTURE, DEPLOYMENT
  - CI/CD workflows: ci, deploy, security, cleanup
  - Development setup: Makefile, .env.example, .gitignore

- **[C][DOCS]** Added sync documentation system
  - README.md: Project overview
  - STATUS.md: Real-time work status
  - PRIORITY.md: Priority queue
  - CHANGELOG.md: Change history (this file)
  - WATCHLIST.md: Critical files monitoring

---

## 2025-11-27

*Start of project*

---

## Archive Policy

- Keep last 30 days in this file
- Older entries → Move to `docs/archive/CHANGELOG-YYYY-MM.md`
