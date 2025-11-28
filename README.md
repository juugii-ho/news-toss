# MVP2 - AI-Powered Collaboration Template

> S + AI Agents (C, G, O) 협업을 위한 최적화된 프로젝트 보일러플레이트

## Quick Start

```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 실제 값 입력

# 2. 의존성 설치
make setup

# 3. 개발 서버 시작
make dev
```

## Team Structure

- **S**: Product Owner & Final Decision Maker
- **C** (Claude Code): Tech Lead, Full-Stack Developer
- **G** (Gemini CLI): Data Engineer, UX Designer
- **O** (Codex CLI): DevOps Engineer, Infrastructure Architect

## Core Documentation

- **[VISION.md](docs/VISION.md)**: 제품 비전, MVP 스코프, 성공 지표
- **[RULES.md](docs/RULES.md)**: 역할, 디렉토리 소유권, 협업 규칙
- **[WORK.md](docs/WORK.md)**: 작업 목록 및 이력
- **[PRIORITY.md](docs/PRIORITY.md)**: 우선순위 큐 (S가 관리)
- **[STATUS.md](docs/STATUS.md)**: 실시간 작업 상태
- **[DECISIONS.md](docs/DECISIONS.md)**: 주요 의사결정 기록
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: 시스템 아키텍처
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)**: 배포 가이드

## Project Structure

```
.
├── app/
│   ├── frontend/       # Next.js 프론트엔드 (C 소유)
│   └── backend/        # 백엔드 API (C 소유)
├── packages/           # 공유 라이브러리 (C 소유)
│   ├── ui/            # UI 컴포넌트
│   ├── config/        # 공통 설정
│   └── lib/           # 공통 로직
├── data/              # 데이터 파이프라인 (G 소유)
│   ├── pipelines/
│   ├── notebooks/
│   └── analysis/
├── infra/             # 인프라 코드 (O 소유)
│   ├── environments/
│   ├── supabase/
│   ├── monitoring/
│   └── backup/
├── docs/              # 프로젝트 문서
├── outputs/           # 로컬 산출물 (gitignore)
└── .github/workflows/ # CI/CD 파이프라인 (O 소유)
```

## Development Commands

```bash
make help        # 사용 가능한 명령어 확인
make setup       # 의존성 설치
make dev         # 프론트엔드 개발 서버
make dev-be      # 백엔드 개발 서버
make build       # 프로덕션 빌드
make test        # 테스트 실행
make lint        # 코드 린트
make pipeline    # 데이터 파이프라인 실행
make clean       # 생성 파일 제거
```

## Workflow

1. **작업 시작 전**: `docs/STATUS.md`와 `docs/PRIORITY.md` 확인
2. **작업 중**: `docs/STATUS.md`에 진행 상황 업데이트
3. **작업 완료 후**: `docs/CHANGELOG.md`에 요약 추가

## License

MIT
