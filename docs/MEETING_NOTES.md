# Meeting Notes

## 2025-11-28 22:44 - 뉴스토스 MVP2 킥오프 미팅

**참석자**: S (Product Owner), C (Claude Code - Tech Lead)

### 📋 회의 안건
뉴스토스(News Spectrum) MVP2 기획서 리뷰 및 개발 방향 논의

---

### 🎯 주요 결정사항

#### 1. 데이터 파이프라인 전략
**결정**: 기존 Supabase 데이터를 사용하지 않고 **처음부터 새롭게 구축**
- **이유**: 기존 데이터 구조가 새로운 기획 요구사항과 맞지 않음
- **테이블 네이밍**: 모든 테이블에 `MVP2_` 접두사 사용
- **요구사항**: 촘촘한 테이블 구성 필요

#### 2. 콘텐츠 생성 전략
**LLM 활용 범위**:
- ✅ **기사 단위**: 단순 번역 (LLM)
- ✅ **토픽/인사이트**: LLM 생성 (S가 세세한 프롬프트 제공 예정)
- ✅ **이미지**: AI API를 통해 S가 별도 제작

**프롬프트 관리**:
- S가 모든 LLM 프롬프트를 직접 작성 및 제공
- C는 프롬프트 실행 인프라만 구축

#### 3. 개발 우선순위
**S의 요청**: 옵션 A(UI 먼저)와 옵션 C(Admin 대시보드) **동시 진행**
- **Phase 1**: 프론트엔드 UI를 목업 데이터로 먼저 구현 (디자인 검증)
- **Phase 1**: Admin 대시보드 (에디터 기능) 병행 개발
  - `is_pinned` 플래그 수동 설정 기능
  - 토픽 관리 인터페이스

#### 4. 에디터 기능 (is_pinned)
**선택된 옵션**: **옵션 C - Admin 대시보드**
- S 또는 운영자가 Admin UI에서 중요 토픽을 수동으로 핀 설정
- Supabase에서 직접 수정하는 것보다 안전하고 편리

---

### ❓ C의 질문 및 S의 답변

#### Q1: 데이터 파이프라인 연동
**Q**: 기존 파이프라인 활용 여부?  
**A**: 새롭게 처음부터 제작. 기존 데이터 구조와 호환 불필요.

#### Q2: 다국어 데이터 정책
**Q**: LLM 번역 및 `one_liner_ko` 생성 주체?  
**A**: 
- 기사 번역: LLM 단순 번역
- `one_liner_ko`, `intro_ko` 등: LLM 생성 (S가 프롬프트 제공)

#### Q3: 미디어 자산
**Q**: 이미지/비디오 소스?  
**A**: S가 AI API를 통해 별도 제작 예정

#### Q4: 에디터 기능
**Q**: `is_pinned` 설정 방식?  
**A**: Admin 대시보드 제작 (옵션 C)

---

### 📝 C의 이해 확인 (Confirmed)

✅ **플랫폼**: Mobile Web (PWA), Next.js SSR, Vercel  
✅ **탭 구조**: Global(인사이트) + Local(트렌드)  
✅ **핵심 UX**:
- Global: Top 3 Hero + 4~10위 List + VS Card 상세
- Local: Masonry Layout (Lv 1/2/3)  
✅ **Stance 색상**: Blue/Red/Gray 파스텔톤  
✅ **성능**: Next/Image, Infinite Scroll, 스크롤 위치 유지

---

### 🚀 Next Actions

#### C (Claude Code)의 다음 작업:
1. **Supabase 스키마 설계** (`MVP2_` 접두사)
   - 테이블: topics, articles, perspectives, countries 등
   - 필드: stance, display_level, is_pinned, media_url 등
2. **API 명세서 작성** (`DECISIONS.md`에 DT 추가)
3. **Admin 대시보드 기획** (에디터 기능 요구사항 정리)
4. **프론트엔드 컴포넌트 구조 설계**

#### S의 다음 작업:
1. LLM 프롬프트 초안 작성 (토픽 생성, 한 줄 요약 등)
2. 디자인 가이드 제공 (있다면)

---

### 📌 중요 메모

- **테이블 네이밍 규칙**: `MVP2_` 접두사 필수
- **프롬프트 소유권**: S가 모든 프롬프트 작성 및 관리
- **개발 순서**: UI 먼저 → 데이터 나중 (목업으로 검증)
- **Admin 필수**: 에디터가 핀/관리할 수 있는 대시보드 필요

---

**작성자**: C (Claude Code)  
**작성일**: 2025-11-28 22:48
