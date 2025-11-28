# Deployment Guide

> 이 문서는 프로덕션 및 스테이징 환경으로의 배포 절차를 안내합니다.

---

## 1. 사전 확인 사항 (Pre-deployment Checklist)

-   [ ] `main` 브랜치가 최신 상태인지 확인
-   [ ] `ci.yml` 워크플로우 (Lint, Test, Build)가 성공적으로 통과했는지 확인
-   [ ] `docs/DECISIONS.md`에 배포와 관련된 새로운 의사결정이 있는지 확인
-   [ ] `infra/secrets/`에 새로운 환경 변수 추가가 필요한지 확인

## 2. 배포 절차 (Deployment Process)

### 스테이징 환경 (Staging)

1.  배포할 커밋을 기준으로 `release/staging-YYYY-MM-DD` 브랜치를 생성합니다.
2.  해당 브랜치를 GitHub에 푸시하면 `.github/workflows/deploy-staging.yml` 워크플로우가 자동으로 실행됩니다.
3.  배포된 스테이징 URL에서 기능이 정상 동작하는지 최종 확인합니다.

### 프로덕션 환경 (Production)

1.  스테이징 환경에서 검증이 완료된 `release/` 브랜치를 `main` 브랜치에 병합(Merge)합니다.
2.  `main` 브랜치에 새로운 태그(`vX.X.X`)를 생성하여 푸시합니다.
3.  `.github/workflows/deploy-prod.yml` 워크플로우가 자동으로 실행됩니다.

## 3. 롤백 절차 (Rollback Plan)

-   **상황**: 심각한 버그가 배포 후 발견되었을 경우
-   **절차**:
    1.  [Vercel/대상 플랫폼]에서 이전 배포 버전으로 즉시 롤백합니다.
    2.  `main` 브랜치를 이전 태그 시점으로 되돌리는 `revert` 커밋을 생성합니다.
    3.  문제의 원인을 파악하고 `fix/` 브랜치에서 수정 후 새로운 배포 절차를 따릅니다.

## 4. 트러블슈팅 (Troubleshooting)

-   **문제**: 배포 실패 시
    -   **해결**: GitHub Actions 로그를 확인하여 빌드 또는 배포 단계의 에러 메시지를 확인합니다.
-   **문제**: 환경 변수 누락
    -   **해결**: `infra/secrets/` 문서를 참고하여 [Vercel/대상 플랫폼]에 누락된 환경 변수를 추가하고 재배포합니다.
