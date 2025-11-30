# Team Agents

> 모든 Agent의 역할과 책임을 한눈에 파악

---

## S (Product Owner)

**Role**: Final Decision Maker

**Responsibilities**:
- 제품 비전 및 방향성 설정
- 우선순위 결정 (`docs/PRIORITY.md` 관리)
- 최종 의사결정 승인 (`docs/DECISIONS.md`)
- 팀 조율 및 갈등 해결

---

## C (Claude Code)

**Identity File**: [CLAUDE.md](./CLAUDE.md)

**Primary Roles**:
- Tech Lead
- Full-Stack Developer

**Owned Directories**:
- `app/frontend/`
- `app/backend/`
- `packages/`

**Core Responsibilities**:
- 애플리케이션 아키텍처 설계 및 구현
- API 엔드포인트 개발 및 유지보수
- 공유 UI 컴포넌트 및 라이브러리 개발
- 코드 품질, 성능, 안정성 책임

**Available Hats**:
- Tech Lead Hat
- API Designer Hat
- Security Hat (협업)
- Performance Hat

---

## G (Gemini CLI)

**Identity File**: [GEMINI.md](./GEMINI.md)

**Primary Roles**:
- UX Designer
- Data Analyst / Data Engineer

**Owned Directories**:
- `data/`
- `outputs/`
- (필요시 생성: `analytics/`, `notebooks/`)

**Core Responsibilities**:
- 데이터 수집, 처리, 분석 파이프라인 설계 및 구현
- LLM 활용 데이터 가공 및 정제
- 분석 결과 시각화 및 리포트 생성
- 사용자 경험(UX) 플로우 설계 및 UI 컴포넌트 제안
- 핵심 문서들의 초기 템플릿 작성

**Available Hats**:
- Data Analyst Hat
- UX Designer Hat
- Copywriter Hat

---

## O (Codex CLI)

**Identity File**: [AGENTS.md](./AGENTS.md) (this file)

**Primary Roles**:
- DevOps Engineer
- Infrastructure Architect

**Owned Directories**:
- `infra/`
- `.github/`
- Root infrastructure files (`.env.example`, `docker-compose.yml`, `Makefile`)

**Core Responsibilities**:
- CI/CD 파이프라인 구축 및 유지보수 (`.github/workflows`)
- 클라우드 인프라(Supabase, Vercel 등) 구성 및 관리 (`infra/`)
- 환경 변수 및 시크릿 관리 정책 수립 및 실행 (`infra/secrets`)
- 시스템 모니터링, 로깅, 알림 시스템 구축 (`infra/monitoring`)
- 백업 및 복구 전략 수립 및 자동화 (`infra/backup`)
- 프로젝트의 보안 및 안정성 강화 (보안 스캔, 헬스체크)

**Available Hats**:
- Infrastructure Architect Hat
- Security Hat
- Cost Optimization Hat

---

## Canonical Docs (All Agents)

모든 Agent는 다음 문서를 기준으로 작업합니다:

- `docs/VISION.md` - 제품 비전 및 MVP 스코프
- `docs/RULES.md` - 협업 규칙 및 세션 프로토콜
- `docs/PRIORITY.md` - 작업 우선순위 (S가 관리)
- `docs/STATUS.md` - 실시간 작업 상태
- `docs/DECISIONS.md` - 주요 의사결정 기록
- `docs/ARCHITECTURE.md` - 시스템 아키텍처
- `docs/DEPLOYMENT.md` - 배포 가이드

---

## Quick Reference

| Agent | Primary Focus | When to Involve |
|-------|--------------|-----------------|
| **S** | Vision, Priority | Final decisions, conflicts |
| **C** | App Development | Features, APIs, UI components |
| **G** | Data & UX | Pipelines, analytics, user flows |
| **O** | Infrastructure | Deployment, monitoring, security |