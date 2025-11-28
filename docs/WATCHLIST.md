# Critical Files Watchlist

> 이 파일들이 변경되면 관련 Agent들에게 알림 필요

---

## Core Rules & Documentation

**Files**:
- `docs/RULES.md`
- `docs/VISION.md`
- `docs/DECISIONS.md`

**Notify**: ALL (C, G, O)

**Why**: 협업 규칙과 제품 방향성 변경

---

## API Contracts

**Files**:
- `app/backend/api/**/*.ts`
- `app/backend/routes/**/*.ts`
- `packages/lib/types.ts`

**Notify**: C, G

**Why**: API 변경 시 프론트엔드와 데이터 파이프라인 영향

---

## Database Schema

**Files**:
- `infra/supabase/migrations/*.sql`
- `packages/lib/database-types.ts`

**Notify**: ALL

**Why**: 스키마 변경은 모든 레이어에 영향

---

## Shared Types & Constants

**Files**:
- `packages/lib/types.ts`
- `packages/lib/constants.ts`
- `packages/config/**/*.ts`

**Notify**: C, G

**Why**: 공유 타입 변경 시 의존 코드 업데이트 필요

---

## Infrastructure & Deployment

**Files**:
- `.github/workflows/*.yml`
- `infra/environments/**/*`
- `.env.example`
- `docker-compose.yml`

**Notify**: O, C

**Why**: 배포 환경 변경 시 앱 설정 조정 필요

---

## Data Pipeline Outputs

**Files**:
- `data/pipelines/schemas/*.json`
- `data/pipelines/output-spec.md`

**Notify**: C, G

**Why**: 파이프라인 출력 형식 변경 시 프론트엔드 어댑터 수정

---

## Usage

### When to Check
1. **세션 시작 시**: STATUS.md 확인 후 WATCHLIST 파일들 변경 여부 확인
2. **작업 완료 시**: 수정한 파일이 WATCHLIST에 있으면 CHANGELOG에 명시

### Example Check
```bash
# 최근 24시간 내 WATCHLIST 파일 변경 확인
git log --since="24 hours ago" --name-only --pretty=format: | \
grep -E "(docs/RULES|api/|migrations/|types\.ts)" | sort -u
```
