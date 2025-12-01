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
2025-11-30 [G][TASK-020-2][data/pipelines/llm_topic_clustering_embedding.py] Refined HDBSCAN parameters (epsilon=0.0, min_samples=3 for small datasets) and added LLM outlier filtering to fix "garbage clusters".
2025-11-30 [G][TASK-020-3][data/pipelines/*.py] Fixed Gemini API timeout/hang issues by setting `os.environ["GRPC_DNS_RESOLVER"] = "native"`. This resolves conflicts between `grpcio` and local DNS settings on macOS.
2025-11-30 [G][TASK-020-4][data/pipelines/llm_topic_clustering_embedding.py] Solved "garbage clusters" in small datasets (JP, BE) by increasing HDBSCAN `epsilon` to 0.1 and strengthening LLM prompt to keep only the "SINGLE dominant topic" (aggressive outlier filtering).
2025-11-30 [G][TASK-020-5][data/pipelines/llm_megatopic_analysis.py] Optimized megatopic analysis speed by pre-filtering small clusters before LLM calls. Also applied "Dominant Topic" strategy to prevent merging unrelated events (e.g., Coupang Hack + Canada Shooting).; adjusted mock path to repo root (two-level up).
2025-11-28 [O][TASK-ZZZ][app/frontend] Fixed API route imports to app/frontend/lib/supabase-client (correct depth), refined mock path when cwd is /app, added next.config images remotePatterns for images.unsplash.com, cleared .next cache. (Updated API imports again to ../../../../lib paths.)
2025-11-28 [O][TASK-ZZZ][docs/INBOX] Processed new messages: C shared API spec/requests done; G→C note on rss_collector progress; G→O Supabase Python client SyntaxError in Python 3.14 (supabase-py) blocking pipeline P0.
2025-11-28 [O][TASK-ZZZ][INBOX] Responded to G: Python 3.11/3.10 환경 권장 for supabase-py (3.14 호환 이슈), pyenv/venv 세팅 가능 안내.
2025-11-29 [O][TASK-ZZZ][INBOX] Added follow-up response to G: no existing venv found, advise creating new 3.11/3.10 venv under data/pipelines/venv with supabase installed; offered pyenv/venv help; awaiting environment path/confirmation.
2025-11-29 [O][TASK-ZZZ][app/frontend] Swapped Gravity Issue Bowl proto to Framer Motion (no Matter.js) per UX v1.1: initial drop animation only, tap pop placeholder. Removed matter-js dependency.
2025-11-29 [O][TASK-ZZZ][app/frontend] Matter toggle mode: added optional Matter.js sim with higher bounce (restitution 0.72) and longer 3.6s run under NEXT_PUBLIC_USE_MATTER flag.
2025-11-29 [O][TASK-ZZZ][app/api] Updated API routes to new Supabase tables: mvp2_megatopics (global) and mvp2_topics (local) pulling latest created_at batch; perspectives now read from stances JSON; keeps mock fallback.
2025-11-29 [O][TASK-ZZZ][app/frontend] VS 카드 호출 시 글로벌 첫 번째 id로 상세 fetch하도록 page.tsx 수정(실데이터 우선, 없을 경우 목업).
2025-11-29 [O][TASK-ZZZ][app/frontend] Guarded local list/perspective fetch: only fetch VS if UUID; local data fallback to mock to avoid undefined items runtime.
2025-11-29 [O][TASK-ZZZ][app/frontend] Added nav tabs (Global/Local), new pages: /global, /local (country selector + Gravity Bowl + mosaic), /global/[id] VS detail, /local/[id] mock detail. Gravity Bowl now navigates to local detail; Matter/Framer toggle preserved.
2025-11-29 [O][TASK-ZZZ][app/api/app] Added /api/local/topics/[id] for latest mvp2_topics by id; Local detail page now fetches API with mock fallback; Local mosaic/bowl link to /local/[id].
2025-11-29 [O][TASK-ZZZ][app/frontend] Gravity Bowl (Matter mode) sleep time extended to 5s to reduce mid-air stopping.
2025-11-29 [O][TASK-ZZZ][app/frontend] VS detail shows placeholder when related_articles empty to clarify data absence.
2025-11-29 [O][TASK-ZZZ][Summary] Supabase 연결 시 최신 24h 데이터 사용: mvp2_megatopics(글로벌) + mvp2_topics(로컬, stances JSON 포함). VS 상세 id가 UUID 아니어도 최신 레코드로 폴백. Local /topics/[id] 상세 API 추가. 탭 네비(Global/Local), Gravity Bowl, Mosaic, 상세 라우트 연결 완료.
2025-11-29 [O][TASK-ZZZ][Execution status] 로컬 dev 서버는 EPERM로 포트 바인딩 실패(3000/3001/3100/3101). 시도: HOST/PORT 조합, 아직 실행 불가. Supabase 데이터 확인은 API curl 필요.
2025-11-29 [O][TASK-ZZZ][app/api] Tested curl /api/global/insights and /api/local/trends; output not visible (likely empty/blocked). Need to verify Supabase data and env.

2025-11-29 [O][TASK-ZZZ][app/frontend/app/local/[id]/page.tsx] 로컬 토픽 상세 페이지를 복원해 API(/api/local/topics/:id) 결과를 스탠스/키워드/기사와 함께 표시, 목업 폴백 포함.

2025-11-29 [O][TASK-ZZZ][app/api] Supabase 테이블명을 소문자(mvp2_global_topics, mvp2_articles)로 정정해 PostgREST 캐시 오류 해결 시도.

2025-11-29 [O][TASK-ZZZ][app/local/[id]/page.tsx] 로컬 상세 stances가 배열이 아닐 때 안전 처리(Array.isArray)로 런타임 오류 제거.

2025-11-29 [O][TASK-ZZZ][LocalGravityBowl] Matter 모드에서 버블 탭 시 즉시 상세로 이동하도록 딜레이 제거(짧은 0.6s 물리 효과만 유지).

2025-11-29 [O][TASK-ZZZ][app/api] Supabase 스키마에 맞춰 매핑 수정: global 테이블 mvp2_global_topics( article_count/country_count ), 상세 stances/related 제거; local topic headline/topic_name/keywords 반영.

2025-11-29 [O][TASK-ZZZ][app/frontend] 글로벌 데이터 소스 테이블을 mvp2_megatopics로 확정, 24h 비어있으면 최신 50건으로 폴백하도록 API/서비스 정비. 홈 글로벌 섹션 미노출 이슈 대응.

2025-11-29 [O][TASK-ZZZ][app/page.tsx] 홈 글로벌/로컬 데이터를 API(getGlobalList/getLocalList) 기반으로 통일해 빈 글로벌 섹션 문제 대응.

2025-11-29 [O][TASK-ZZZ][app/api] 글로벌 테이블명을 mvp2_global_topics로 교정(리스트/상세), 잘못된 mvp2_megatopics 참조로 목업 폴백되던 문제 수정.

2025-11-29 [O][TASK-ZZZ][app/api] 글로벌 API/클라이언트 모두 데이터 없을 경우 목업으로 폴백하도록 보강(빈 배열 방지).

2025-11-29 [O][TASK-ZZZ][app/api] 글로벌 리스트 API의 24h 필터 제거, 최신 50건 정렬만 사용해 목업 폴백을 줄임.
2025-11-29 [G][TASK-010][Mistake] Google Embedding API (text-embedding-004) caused persistent DNS/Timeout errors in local batch processing. Lesson: For high-volume batch jobs in unstable local network environments, prefer Local Embeddings (sentence-transformers) over API calls.
2025-11-29 [O][TASK-010][Architecture] Advised switching to Local Embeddings (Option A) or GitHub Actions (Option B) to resolve DNS bottleneck. Confirmed Local Embedding is viable for MVP stability.
2025-11-29 [G][TASK-010][Data] Recommended 'paraphrase-multilingual-MiniLM-L12-v2' for multi-language topic clustering.
2025-11-29 [C][TASK-010][Implementation] Refactored Step 2 & Step 3 pipelines to use Local Embeddings, added DB cleanup logic, and optimized batch sizes (100) based on O & G's advice.

2025-11-29 [O][TASK-ZZZ][app/frontend] 글로벌 섹션 UI 변경(KR 포함/제외 토글, 메가토픽/국가수 배지, 카드 전체 링크화, VS 섹션 제거).
2025-11-29 [O][TASK-ZZZ][local page] 국가 탭 개편: 병 아이콘 모달로 Gravity Bowl 호출, 국가 드롭다운(▼) 선택, 모자이크만 본문 노출; Gravity Bowl status 텍스트 옵션화.

2025-11-29 [O][TASK-ZZZ][NavTabs] React import 추가로 ReferenceError 해결.

2025-11-29 [O][TASK-ZZZ][app/frontend] 홈 리디렉션 -> /global, 글로벌 헤더/문구 제거, 플랫 탭(Global|Local|버튼) 정리. 글로벌 배지 N개국/메가토픽 #N, 로컬 상단 컨테이너 제거, 국가 선택 모달만 유지, Gravity Bowl 버튼만 섹션 헤더에 위치, 로컬 무한 스크롤 끝나면 다음 국가 자동 로드.

2025-11-29 [O][TASK-ZZZ][LocalMosaic] topic_id 없는 항목 필터링(safeItems)으로 렌더 오류 방지.

2025-11-29 [O][TASK-ZZZ][LocalMosaic] 자동 국가 전환 조건을 완화(pages>1+데이터 있을 때만)해 초기 페이지에서 다른 국가로 튀는 문제 완화.

2025-11-29 [O][TASK-ZZZ][app/api] 로컬 트렌드 API에 hasNextPage/limit 반환 추가로 무한스크롤 가능하게 수정.
2025-11-29 [O][TASK-ZZZ][LocalPageClient] 국가 선택 목록을 AU, BE, CA, CN, DE, FR, GB, IT, JP, KR, NL, RU, US 전체로 확장.
2025-11-29 [O][TASK-ZZZ][LocalMosaic] topic_id 없는 항목 필터 및 자동 국가 전환 완화, API hasNextPage 사용으로 무한스크롤 개선.

2025-11-29 [O][TASK-ZZZ][app/api] 로컬 트렌드 정렬을 article_count desc 우선으로 변경.
2025-11-29 [O][TASK-ZZZ][LocalMosaic] sentinel 계산을 안전 목록 기준으로 조정하고 빈 상태 메시지 추가.

2025-11-29 [O][TASK-ZZZ][app/api] 로컬 트렌드 24h 필터 제거(모든 누적 데이터 조회)로 다국가 빈 목록 이슈 대응.

2025-11-29 [O][TASK-ZZZ][app/api] 로컬 트렌드 topic_id/keyword/title 기본값 보강(id/ topic_name/created_at 조합)으로 빈 리스트/필터 문제 대응.

2025-11-29 [O][TASK-ZZZ][LocalGravityBowl] 버블 키워드에 pre-line 적용/패딩 추가로 상단 잔상 방지, 제목 길이 여유 확대(28자).

2025-11-29 [O][TASK-ZZZ][LocalGravityBowl] 최대 버블 크기 240px, 로그 스케일 재조정(log base 30)으로 기사 10개 이상시 2배 이상 커지도록 조정.

2025-11-29 [O][TASK-ZZZ][LocalGravityBowl] 버블 스케일 튜닝: 10개 이상은 240px, 소량 기사는 완만한 로그 스케일(log base 80, 0.6배)로 과도 팽창 방지.

2025-11-29 [O][TASK-ZZZ][LocalGravityBowl] Matter 렌더 afterRender에서 clearRect로 캔버스 잔상(글자 남음) 제거.

2025-11-29 [O][TASK-ZZZ][LocalGravityBowl] 오버레이 텍스트 위치가 화면 밖일 때는 스킵(y<0,y>height+10)하여 잔상/흔들림 완화.

2025-11-29 [O][TASK-ZZZ][UI] 헤더 3분할 버튼(글로벌/로컬/액션) 색상 토글, Global Insight 헤더 버튼 제거.
2025-11-29 [O][TASK-ZZZ][Global detail] 국가별 관점 섹션 제거, 설명 필드 추가, 관련 기사 링크 "제목 - 언론사"로 표기.
2025-11-29 [O][TASK-ZZZ][Local detail] 기사수/레벨 카드 제거, 입장 스펙트럼 바 추가, 관련 기사 링크 "제목 - 언론사"로 표기.
2025-11-29 [O][TASK-ZZZ][Local] 국가 모달 가나다 정렬, 뉴스 순위 제목에 국가명 반영, Gravity Bowl 정지 7s 상향 유지.

2025-11-29 [O][TASK-ZZZ][VsCardSection] 글로벌 상세 관련기사/설명 섹션을 카드 스타일로 분리, 링크를 “제목 - 언론사”로 표기.
2025-11-29 [O][TASK-ZZZ][Local detail] 관련기사 제목 margin 조정(아래 패딩 확보).
2025-11-29 [O][TASK-ZZZ][GlobalSection] KR 포함/제외 필터를 URL 파라미터 기반으로 동기화.
2025-11-29 [O][TASK-ZZZ][LocalGravityBowl] 텍스트 y범위 제한으로 잔상/떨림 완화.

2025-11-29 [O][TASK-ZZZ][VsCardSection] 글로벌 상세를 로컬 상세처럼 박스 분리(질문/설명/관련기사 각각 rounded-card)하여 관련 기사 컨테이너가 헤더 안으로 들어가는 문제 수정.

2025-11-29 [O][TASK-ZZZ][local trends API] 토픽에 topic_ids 존재 시 is_global 플래그 추가, Topic Bowl에서 GLOBAL 배지 표시 가능.

2025-11-30 [G][TASK-SPECTRUM][app/api/global/insights/route.ts] Fixed Global Stance Aggregation by traversing Global -> Articles -> Local Topic (since direct link doesn't exist).
2025-11-30 [G][TASK-SPECTRUM][app/frontend/components/LocalTile.tsx] Updated to handle raw stance object format and moved spectrum bar inline with article count.
2025-11-30 [G][TASK-SPECTRUM][app/frontend/components/GlobalSection.tsx] Updated to handle both array and object stance formats for robustness.
2025-11-30 [G][TASK-SPECTRUM][Detail Pages] Reverted Context Spectrum Bars from article cards on both Global and Local detail pages.

2025-11-30 [G][TASK-THUMBNAIL][data/pipelines/llm_global_thumbnail_generator.py] Created global thumbnail generator script using same prompt approach as local topics.
2025-11-30 [G][TASK-THUMBNAIL][Global Topics] Successfully generated AI thumbnails for 10 global topics and uploaded to Supabase Storage.
2025-11-30 [G][TASK-THUMBNAIL][Prompt] Updated thumbnail generation prompt to "글자 사용 금지" for cleaner images without text.
2025-12-02 [O][TASK-PIPELINE-HARDEN][data/pipelines] Hardened ingestion/publish: cut off stale RSS dates, GB country code alignment, no blanket unpublish (publish window env), merge topics instead of overwrite, restrict thumbnail reuse by country/recent window.
2025-12-02 [O][TASK-PIPELINE-HARDEN][infra/.github/workflows/data/pipelines] Set publish window default 12h, doubled schedule (06/18 UTC), thumbnails now published-only; GB country alignment already done.
2025-12-02 [O][TASK-THUMBNAIL-GLOBAL][data/pipelines/llm_global_thumbnail_generator.py] Restrict global thumbnail generation to published megatopics from last 7 days (align with local policy).
2025-12-02 [O][TASK-SCHEDULE][.github/workflows/daily_full_pipeline.yml] Updated cron to 07:00/19:00 KST (22:00/10:00 UTC) for twice-daily runs.
