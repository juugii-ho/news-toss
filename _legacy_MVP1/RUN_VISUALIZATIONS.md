# 시각화 비교 가이드

세 가지 버전을 만들었습니다. 각각 브라우저로 열어서 비교해보세요.

## 1. Editorial Bubble Chart (Python → HTML)
**파일:** `visualize_editorial_bubbles.py`
**실행:**
```bash
/Users/sml/gemini_env/bin/python visualize_editorial_bubbles.py
```
**출력:** `topic_map_editorial.html`

**특징:**
- ✅ O의 피드백 100% 반영
- ✅ 차분한 파스텔 6색 팔레트
- ✅ 오프화이트 배경, 은은한 그리드
- ✅ Top 15개만 표시 (나머지 배경)
- ✅ Pretendard 폰트 스타일
- ✅ 실제 Supabase 데이터 연동

**장점:** 실제 데이터, 차분한 톤
**단점:** Plotly 기반이라 인터랙션 제한적

---

## 2. Topic Cards + Mini Map (Pure HTML)
**파일:** `topic_cards_with_minimap.html`
**실행:** 브라우저로 바로 열기

**특징:**
- ✅ 제품다운 접근 (데이터 시각화 느낌 ✗)
- ✅ 메인: 깔끔한 토픽 카드
- ✅ 서브: 작은 버블맵 (맥락)
- ✅ 모바일 친화적
- ✅ 명확한 정보 계층

**장점:** 가장 제품다움, 읽기 쉬움
**단점:** "지형도" 컨셉 약함

---

## 3. Sonar Map (Pure HTML/Canvas) ⭐️ 추천
**파일:** `topic_sonar_map.html`
**실행:** 브라우저로 바로 열기

**특징:**
- ✅ 크기가 명확 (중요도 차이 확실)
- ✅ 호버만 제목 표시 (깔끔)
- ✅ 소나 펄스 효과 (탐지되는 느낌)
- ✅ 스프링 애니메이션 (통통 튀는 경쾌함)
- ✅ 차분한 색상 (우리 톤)
- ✅ 자동 움직임 ✗ (인터랙션 중심)
- ✅ 호버 시 확대 + 상세정보

**장점:** 가장 세련됨, 경쾌함, 명쾌함
**단점:** Mock 데이터 (API 연동 필요)

---

## 비교 포인트

### 크기 명확성
1. Editorial: △ (Plotly 기본)
2. Cards: ○ (카드 크기 동일)
3. Sonar: ◎ (크기 차이 확실)

### 호버 인터랙션
1. Editorial: △ (Plotly 툴팁)
2. Cards: ○ (카드 호버)
3. Sonar: ◎ (부드러운 확대 + 툴팁)

### 톤앤매너 일치
1. Editorial: ○ (차분하지만 Plotly 느낌)
2. Cards: ◎ (제품다움)
3. Sonar: ◎ (세련됨)

### 경쾌함
1. Editorial: △ (정적)
2. Cards: ○ (카드 호버)
3. Sonar: ◎ (스프링 애니메이션)

---

## 추천 순서

1. **먼저 보기:** `topic_sonar_map.html`
   - 가장 완성도 높음
   - 요청하신 모든 요소 반영

2. **비교용:** `topic_cards_with_minimap.html`
   - 완전히 다른 접근 (카드 중심)

3. **데이터 확인:** `visualize_editorial_bubbles.py` 실행
   - 실제 Supabase 데이터로 확인

---

## 다음 단계

Sonar Map이 마음에 들면:
1. API 연동 (`/api/topics`에서 데이터 가져오기)
2. 날짜 슬라이더 (과거 데이터 보기)
3. 토픽 클릭 → 상세 페이지 연결
4. 모바일 터치 최적화

궁금한 점이나 수정 요청 있으면 말씀해주세요!
