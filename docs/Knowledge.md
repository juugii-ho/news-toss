2025-11-28 [O][TASK-ZZZ][docs/STATUS.md] Synced context for session and reviewed RULES/PRIORITY/STATUS/WORK/INBOX for meeting prep.
2025-11-28 [O][TASK-ZZZ][docs/MEETING_NOTES.md] Reviewed kick-off decisions: Supabase 새 구축, MVP2_ prefix, UI-first with mock data, Admin 대시보드 필요, Vercel/Next.js SSR.
2025-11-28 [O][TASK-ZZZ][Conversation] S clarified: Vercel 배포/Actions는 로컬 검증 후 나중 세팅, Supabase 무료 티어 하나 공용 사용 예정(분리 필요시 제안 요청), 초기엔 Next.js API Routes 사용, 별도 API 필요하면 제안 가능. 요청: PWA 개념/필요 범위 설명 및 캐시 관련 안내.
2025-11-28 [O][TASK-ZZZ][Conversation] S confirmed product name "뉴스토스" (News Spectrum), Supabase 단일 인스턴스(클로즈 베타 기간 공용) 사용, 베타 종료 즈음 Prod 분리 예정.
2025-11-28 [O][TASK-ZZZ][Conversation] Theme reference: Apple/Toss style; Supabase env-column 생략; cache 정책은 ISR(revalidate: 3600) 적용 방향.
2025-11-28 [O][TASK-ZZZ][app/frontend] Added Next.js app scaffold with PWA basics (manifest, icons, theme-color #fff), ISR revalidate=3600 default, light theme globals placeholder.
2025-11-28 [O][TASK-ZZZ][app/frontend] Resolved Next metadata warning by moving themeColor to viewport only; noted npm install deps warnings (deprecated packages, 4 vuln) from local run by S.
2025-11-28 [O][TASK-ZZZ][docs/STATUS.md] Updated status: PWA 셋업 완료, UI 구현 준비.
2025-11-28 [O][TASK-ZZZ][G-request] 요청 제안: (1) Global/VS/Local 목업 데이터 JSON 샘플 제공, (2) 한글 카피 톤/레이블 가이드, (3) 스탠스 파스텔 컬러 값, (4) 인피니트 스크롤/뒤로가기 UX 가이드.
2025-11-28 [O][TASK-ZZZ][app/frontend] Implemented mock-backed UI: Global Hero/List, VS 카드, Local 모자이크 with infinite scroll; added mock API routes reading outputs/mock_data, stance color tokens, and UX styles per guides.
2025-11-28 [O][TASK-ZZZ][docs review] Read G’s updates: outputs/mock_data/*.json, outputs/guides/copy_design_guide.md (카피/색상), outputs/guides/ux_guide.md (인피니트 스크롤/스크롤 복원), data/pipelines/README.md, docs/VISION.md, docs/ARCHITECTURE.md.
2025-11-28 [O][TASK-ZZZ][app/frontend] Applied guide details: Framer Motion entry animations for Global hero/list, infinite-scroll trigger at last-3 item per UX guide, added stance color tokens in CSS.
2025-11-28 [O][TASK-ZZZ][INBOX] Added requests: to C—API Routes 타입/매핑, 라우팅/스크롤복원 방식, Supabase env 명칭/주입 시기; to G—추가 mock page(2+) for Local, 타이포/아이콘 가이드 여부.
2025-11-28 [O][TASK-ZZZ][app/frontend] Added ScrollRestoration client utility (sessionStorage) and wired in layout to restore scroll when navigating back, per UX guide.
2025-11-28 [O][TASK-ZZZ][app/frontend] Added React Query provider (app/providers) and migrated Local mosaic to useInfiniteQuery with initialData; added @tanstack/react-query dependency.
2025-11-28 [O][TASK-ZZZ][app/frontend] Added API fetch helpers (lib/api.ts) per C’s spec endpoints with graceful fallback to mocks; page.tsx now uses getGlobalList/getVsCard/getLocalList (ISR 1h preserved).
2025-11-28 [O][TASK-ZZZ][app/frontend] Implemented API routes per C spec with Supabase client + mock fallback: /api/global/insights, /api/global/insights/[id], /api/local/trends (display_level fallback calc). Added packages/lib/supabase-client.ts; dependency @supabase/supabase-js added (npm install pending).
2025-11-28 [O][TASK-ZZZ][app/frontend] Fixed framer-motion usage in RSC by marking GlobalSection as client component.
2025-11-28 [O][TASK-ZZZ][app/frontend] Fixed mock path resolution for Next dev root by resolving outputs/ from repo root (process.cwd mismatch).
2025-11-28 [O][TASK-ZZZ][app/frontend] Fixed fetch URL construction for server env (adds NEXT_PUBLIC_BASE_URL default http://localhost:3000); added .env.local.example with BASE_URL/Supabase vars.
2025-11-28 [O][TASK-ZZZ][app/frontend] Moved supabase client import to app/frontend/lib/supabase-client to fix path issues; adjusted mock path to repo root (two-level up).
2025-11-28 [O][TASK-ZZZ][app/frontend] Fixed API route imports to app/frontend/lib/supabase-client (correct depth), refined mock path when cwd is /app, added next.config images remotePatterns for images.unsplash.com, cleared .next cache. (Updated API imports again to ../../../../lib paths.)
2025-11-28 [O][TASK-ZZZ][docs/INBOX] Processed new messages: C shared API spec/requests done; G→C note on rss_collector progress; G→O Supabase Python client SyntaxError in Python 3.14 (supabase-py) blocking pipeline P0.
2025-11-28 [O][TASK-ZZZ][INBOX] Responded to G: Python 3.11/3.10 환경 권장 for supabase-py (3.14 호환 이슈), pyenv/venv 세팅 가능 안내.
2025-11-29 [O][TASK-ZZZ][INBOX] Added follow-up response to G: no existing venv found, advise creating new 3.11/3.10 venv under data/pipelines/venv with supabase installed; offered pyenv/venv help; awaiting environment path/confirmation.
2025-11-29 [O][TASK-ZZZ][app/frontend] Swapped Gravity Issue Bowl proto to Framer Motion (no Matter.js) per UX v1.1: initial drop animation only, tap pop placeholder. Removed matter-js dependency.
2025-11-29 [O][TASK-ZZZ][app/frontend] Matter toggle mode: added optional Matter.js sim with higher bounce (restitution 0.72) and longer 3.6s run under NEXT_PUBLIC_USE_MATTER flag.
2025-11-29 [O][TASK-ZZZ][app/api] Updated API routes to new Supabase tables: mvp2_megatopics (global) and mvp2_topics (local) pulling latest created_at batch; perspectives now read from stances JSON; keeps mock fallback.
