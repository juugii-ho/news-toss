# 회의 준비 자료 - News Spectrum MVP2

**일시**: 2025-11-28 23:48  
**참석자**: S, C (Claude Code)  
**목적**: RSS 피드 검증 및 데이터베이스 마이그레이션 완료 보고

---

## 📊 완료된 작업 요약

### 1. RSS 피드 검증 (13개국, 51개 언론사)
✅ **성공률**: 96.1% (49/51)
- **사용 가능**: 49개 언론사
- **제외**: 2개 (CBC - 타임아웃, Le Soir - 접근 차단)
- **Summary 제공률**: 95.9%

### 2. 데이터베이스 스키마 설계
✅ **10개 테이블** 설계 완료
- 기존 6개 (기획서 기반)
- 신규 4개 (파이프라인 요구사항)

### 3. Supabase 마이그레이션
✅ **마이그레이션 완료** (MVP1 병행 운영)
- 10개 테이블 생성
- 49개 언론사 데이터 삽입
- 27개 인덱스 생성
- 기존 MVP1 테이블 보존

---

## 📁 생성된 문서

### 핵심 문서 (5개)
1. **DATABASE_SCHEMA.md** - 상세 스키마 설계
2. **RSS_FEED_AND_DATABASE_REPORT.md** - 종합 보고서 (팀원 참고용)
3. **RSS_FEED_FINAL_DECISION.md** - 최종 RSS 피드 결정
4. **MIGRATION_LOG.md** - 마이그레이션 과정 기록
5. **database-types.ts** - TypeScript 타입 정의

### 테스트 결과
- **rss_feed_test_results_ALL.json** - 전체 테스트 결과 (JSON)
- **RSS_SUMMARY_ANALYSIS.md** - Summary 필드 분석

### 마이그레이션 파일
- **20251128_initial_schema.sql** - Supabase 마이그레이션 SQL

---

## 🎯 주요 결정 사항

### 1. RSS 피드 (49개 사용)
| 결정 | 내용 |
|------|------|
| 제외 피드 | CBC (CA), Le Soir (BE) |
| Summary 없는 피드 | CNN, Nikkei Asia → LLM 생성 |
| 정치 성향 분류 | 보수/중립/진보 균형 확보 |

### 2. 데이터베이스 구조
| 결정 | 내용 |
|------|------|
| 테이블 접두사 | MVP2_ (MVP1과 분리) |
| 병행 운영 | MVP1 테이블 보존, 동시 운영 |
| 임베딩 | pgvector 사용, 768차원 |
| 언론사 관리 | is_active 필드로 활성/비활성 관리 |

### 3. 마이그레이션 전략
| 결정 | 내용 |
|------|------|
| 안전성 | IF NOT EXISTS 사용 |
| 롤백 | MVP2만 삭제 가능 (MVP1 영향 없음) |
| 데이터 | 국가 13개, 언론사 51개 초기 삽입 |

---

## 📊 데이터베이스 구조

### 테이블 관계도
```
MVP2_countries (13개국)
    ↓
MVP2_news_sources (49개 언론사)
    ↓
MVP2_articles (원본 기사)
    ├→ MVP2_article_stance (LLM 스탠스)
    ├→ MVP2_embeddings (벡터)
    ├→ MVP2_local_topics (국가별 트렌드)
    │       ↓
    │   MVP2_topic_relations
    │       ↓
    └→ MVP2_global_topics (글로벌 인사이트)
            ↓
        MVP2_perspectives (VS 카드)
            ↓
        MVP2_media_assets (AI 미디어)
```

### 데이터 플로우
```
1. RSS 수집 (49개 언론사)
   ↓
2. MVP2_articles 저장
   ↓
3. LLM 처리
   - 번역 (KO/EN)
   - Summary 생성 (없는 경우)
   - 스탠스 분석 (SUPPORTIVE/NEUTRAL/CRITICAL)
   ↓
4. 임베딩 생성 (text-embedding-004)
   ↓
5. 토픽 추출
   - Local topics (국가별)
   - Global megatopics (5개국 이상)
   ↓
6. 관점 생성 (VS 카드)
```

---

## 🔄 현재 상태

### C (Claude Code)
- ✅ RSS 피드 검증 완료
- ✅ 데이터베이스 스키마 설계 완료
- ✅ Supabase 마이그레이션 완료
- ✅ TypeScript 타입 정의 완료

### G (Gemini CLI)
- 🔄 레거시 자산 마이그레이션 진행 중
- 📋 다음: 데이터 파이프라인 개발

### O (Codex CLI)
- 🔄 프론트엔드 스캐폴딩 진행 중
- 📋 다음: API 연결 및 UI 구현

---

## 🎯 다음 단계

### 즉시 조치 (우선순위 순)

#### 1. 데이터 파이프라인 개발 (G)
- [ ] RSS 수집 스크립트 (`data/pipelines/rss_collector.py`)
- [ ] LLM 번역/생성 스크립트
- [ ] 스탠스 분석 스크립트
- [ ] 임베딩 생성 스크립트
- [ ] 토픽 추출/병합 스크립트

#### 2. API 개발 (C)
- [ ] FastAPI 프로젝트 구조 설정
- [ ] GET /api/global/insights 엔드포인트
- [ ] GET /api/global/insights/{id} 엔드포인트
- [ ] GET /api/local/trends 엔드포인트

#### 3. 프론트엔드 개발 (O)
- [ ] Next.js API 연결
- [ ] Global 탭 UI (Hero + List)
- [ ] VS Card 상세 페이지
- [ ] Local 탭 Mosaic 레이아웃

---

## ⚠️ 주의사항

### 1. MVP1 병행 운영
- MVP1 테이블 절대 삭제 금지
- MVP2 안정화 전까지 유지
- 데이터 동기화 불필요 (별도 운영)

### 2. LLM 프롬프트 전략
- Summary 생성 프롬프트 필요 (CNN, Nikkei Asia)
- 스탠스 분석 프롬프트 필요
- 번역 프롬프트 필요

### 3. 성능 고려사항
- 임베딩 생성 시간 (49개 언론사 × 기사 수)
- HNSW 인덱스 빌드 시간
- API 응답 속도 최적화

---

## 📝 회의 안건

### 1. 확인 사항
- [ ] RSS 피드 49개 승인
- [ ] 제외된 2개 피드 (CBC, Le Soir) 승인
- [ ] 데이터베이스 스키마 승인
- [ ] MVP1 병행 운영 전략 승인

### 2. 결정 필요 사항
- [ ] LLM 모델 선택 (gemini-2.5-flash 확정?)
- [ ] 임베딩 모델 확정 (text-embedding-004?)
- [ ] 데이터 파이프라인 실행 주기 (1시간? 6시간?)
- [ ] Admin 대시보드 우선순위

### 3. 논의 사항
- [ ] G의 데이터 파이프라인 개발 일정
- [ ] C의 API 개발 일정
- [ ] O의 프론트엔드 개발 일정
- [ ] MVP 출시 목표일

---

## 📊 통계

### 작업 시간
- RSS 피드 검증: ~2시간
- 스키마 설계: ~3시간
- 마이그레이션: ~1시간
- 문서화: ~1시간
- **총**: ~7시간

### 생성된 코드/문서
- SQL: 370줄
- TypeScript: 250줄
- Markdown: 1,500줄
- Python (테스트): 300줄

### 테스트 커버리지
- RSS 피드: 51/51 (100%)
- 데이터베이스: 10/10 테이블 (100%)
- 인덱스: 27/27 (100%)

---

## ✅ 체크리스트

### 회의 전 확인
- [x] 모든 문서 최신화
- [x] STATUS.md 업데이트
- [x] 마이그레이션 완료 확인
- [x] 테스트 결과 정리
- [x] 다음 단계 명확화

### 회의 중 준비
- [ ] 질문 사항 메모
- [ ] 결정 사항 기록
- [ ] Action Item 정리

### 회의 후 조치
- [ ] DECISIONS.md 업데이트
- [ ] WORK.md에 새 Task 추가
- [ ] PRIORITY.md 업데이트
- [ ] 팀원들에게 공유

---

**준비 완료**: 2025-11-28 23:48  
**작성자**: C (Claude Code)
