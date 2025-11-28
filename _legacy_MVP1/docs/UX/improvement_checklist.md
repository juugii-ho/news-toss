# UX Improvement Checklist

> **목적:** C/G/O가 UX 개선 작업 시 참고할 체크리스트
> **최종 업데이트:** 2025-11-26

---

## 📱 모바일 우선 원칙

개발/디자인 시 **항상** 모바일을 먼저 고려하세요.

```
✅ DO:
- 모바일에서 먼저 테스트
- Touch target 최소 44x44px
- 한 손 조작 가능하도록
- 텍스트 최소 16px

❌ DON'T:
- Desktop 먼저 디자인
- Hover-only 인터랙션
- 작은 버튼/링크
- 가로 스크롤
```

---

## 🎯 작업 전 체크리스트

### 새 기능/컴포넌트 추가 시

- [ ] **모바일 responsive?** (375px 기준)
- [ ] **Touch target 충분?** (최소 44px)
- [ ] **Loading state 있나?** (Skeleton or Spinner)
- [ ] **Error state 있나?** (Retry 버튼)
- [ ] **Empty state 있나?** (친절한 안내)
- [ ] **Accessibility?** (ARIA labels, keyboard nav)
- [ ] **Dark mode 지원?** (색상 contrast 확인)

### 텍스트 추가 시

- [ ] **한/영 모두 고려?**
- [ ] **모바일에서 읽기 편한가?** (font-size, line-height)
- [ ] **너무 길지 않나?** (3-5초 내 이해 가능)
- [ ] **맥락 충분한가?** (사용자가 이해할 수 있나)

### API/데이터 연동 시

- [ ] **Retry logic 있나?** (네트워크 오류 대응)
- [ ] **Fallback 있나?** (데이터 없을 때)
- [ ] **Loading 처리?** (Skeleton)
- [ ] **Error 처리?** (친절한 메시지)
- [ ] **캐싱 고려?** (불필요한 재요청 방지)

---

## 🚨 절대 규칙 (NEVER)

### UI/UX
- ❌ Hover-only 기능 (모바일 작동 안 함)
- ❌ 44px 미만 터치 타겟
- ❌ 설명 없는 아이콘만 버튼
- ❌ 에러 메시지 없는 실패 처리
- ❌ 무한 로딩 (timeout 필수)

### 컨텐츠
- ❌ 자동 생성 텍스트 그대로 노출
- ❌ 맥락 없는 숫자/데이터
- ❌ "Coming Soon" 없이 빈 섹션
- ❌ 날짜/시간 정보 누락

### 성능
- ❌ Lazy loading 없는 긴 리스트
- ❌ 최적화 없는 큰 이미지
- ❌ Skeleton 없는 긴 로딩

---

## 📋 컴포넌트별 체크리스트

### MegatopicCard
- [ ] 날짜 표시 (relative time)
- [ ] 모바일: 1-column Country Breakdown
- [ ] Touch target 44px 이상
- [ ] Spectrum 설명 (모바일: tap-to-show)
- [ ] "View Full Analysis" 버튼 위치/텍스트

### Topic Detail Page
- [ ] Summary 실제 내용 (자동 생성 X)
- [ ] Country Summary 표시
- [ ] Back 버튼 크기 (모바일 44px)
- [ ] Skeleton loading
- [ ] "다음 토픽" 버튼

### Hero Section
- [ ] Last Updated 표시
- [ ] 스크롤 인디케이터
- [ ] 가치 제안 명확
- [ ] CTA 버튼 명확

### Header/Footer
- [ ] Navigation 명확
- [ ] Last Updated (header)
- [ ] Data Sources (footer)
- [ ] Contact/About 링크

---

## 🎨 디자인 가이드라인

### 색상
```
Primary: Zinc (neutral)
Supportive: Emerald-500 (긍정)
Factual: Zinc-400 (중립)
Critical: Amber-500 (비판)

Dark mode: Contrast ratio 최소 4.5:1
```

### 타이포그래피
```
Desktop:
- Hero: 4xl-6xl (36-60px)
- Heading: 2xl-3xl (24-30px)
- Body: base (16px)
- Caption: sm (14px)

Mobile:
- Hero: 3xl-4xl (30-36px)
- Heading: xl-2xl (20-24px)
- Body: base-lg (16-18px)
- Caption: sm (14px)
```

### 간격
```
Touch target: 최소 44x44px
Padding (mobile): 최소 16px
Card gap: 16-24px
Section gap: 48-64px
```

---

## 🔍 테스트 체크리스트

### 수동 테스트 (배포 전 필수)

#### 모바일 (Chrome DevTools)
- [ ] iPhone SE (375px) - 최소 크기
- [ ] iPhone 14 Pro (393px) - 일반
- [ ] Pixel 7 (412px) - Android

#### 기능 테스트
- [ ] 첫 방문 → 스크롤 → 카드 클릭 → Detail
- [ ] Back → 스크롤 위치 복원
- [ ] Spectrum hover/tap → 설명 표시
- [ ] Country Breakdown 펼치기/접기
- [ ] 로딩 상태 확인 (throttle 3G)
- [ ] 에러 상태 확인 (offline)

#### Dark Mode
- [ ] 모든 텍스트 읽기 가능
- [ ] Contrast ratio 충분
- [ ] 색상 의미 유지

---

## 📊 성능 체크리스트

### Lighthouse 목표 (모바일)
- [ ] Performance: ≥ 85
- [ ] Accessibility: ≥ 90
- [ ] Best Practices: ≥ 90
- [ ] SEO: ≥ 95

### Core Web Vitals
- [ ] LCP (Largest Contentful Paint): < 2.5s
- [ ] FID (First Input Delay): < 100ms
- [ ] CLS (Cumulative Layout Shift): < 0.1

### 번들 크기
- [ ] First Load JS: < 200KB
- [ ] Total bundle: < 500KB

---

## 🚀 배포 전 최종 체크

- [ ] 모바일 테스트 완료 (3개 기기)
- [ ] Dark mode 확인
- [ ] Loading/Error states 테스트
- [ ] Lighthouse score 확인
- [ ] 404/Error 페이지 테스트
- [ ] Sitemap/robots.txt 확인
- [ ] Meta tags 확인 (Open Graph)
- [ ] README 업데이트
- [ ] CHANGELOG 업데이트
- [ ] Knowledge.md 기록

---

## 📝 업데이트 로그

- 2025-11-26: 초안 작성 (C)
