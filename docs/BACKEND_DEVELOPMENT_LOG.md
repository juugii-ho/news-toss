# FastAPI 백엔드 개발 완료 기록

**일시**: 2025-11-29 00:11  
**작성자**: C (Claude Code)  
**상태**: ✅ 완료

---

## 📋 작업 요약

### 완료된 작업
1. ✅ FastAPI 프로젝트 구조 설정
2. ✅ 3개 API 엔드포인트 구현
3. ✅ Pydantic 스키마 정의
4. ✅ Supabase 연동
5. ✅ 가상환경 설정 및 의존성 설치
6. ✅ 서버 실행 성공

---

## 🗂️ 생성된 파일 (10개)

### 핵심 파일
1. `backend/app/main.py` - FastAPI 메인 애플리케이션
2. `backend/app/api/global_insights.py` - Global Insights API
3. `backend/app/api/local_trends.py` - Local Trends API
4. `backend/app/schemas/api.py` - Pydantic 스키마
5. `backend/app/core/config.py` - 설정 관리
6. `backend/app/core/database.py` - Supabase 클라이언트
7. `backend/requirements.txt` - 의존성 목록
8. `backend/.env.example` - 환경변수 예시
9. `backend/README.md` - 문서
10. `backend/venv/` - Python 가상환경

---

## 🚀 구현된 API 엔드포인트

### 1. Global Insights
- **GET /api/global/insights**
  - 글로벌 인사이트 Top 10 목록 조회
  - 국가별 관점(perspectives) 포함
  - 정렬: rank → article_count

- **GET /api/global/insights/{insight_id}**
  - 특정 글로벌 인사이트 상세 조회
  - VS 카드용 데이터
  - 404 에러 처리

### 2. Local Trends
- **GET /api/local/trends**
  - 국가별 트렌드 토픽 목록 조회
  - Query Parameters:
    - `country` (required): 국가 코드
    - `page` (optional): 페이지 번호 (기본값: 1)
    - `limit` (optional): 페이지당 항목 수 (기본값: 20, 최대: 50)
  - Display Level 자동 계산 (1/2/3)
  - 페이지네이션 지원

### 3. Health Check
- **GET /** - Root endpoint
- **GET /health** - Health check

---

## 🔧 기술 스택

### Backend Framework
- **FastAPI** 0.104.1
- **Uvicorn** 0.24.0 (ASGI 서버)
- **Pydantic** 2.5.0 (데이터 검증)

### Database
- **Supabase** 2.0.3 (PostgreSQL)
- **asyncpg** 0.29.0

### Development
- **pytest** 7.4.3
- **httpx** 0.24.1

---

## 🐛 해결한 문제

### 문제 1: 가상환경 필요
**에러**: `externally-managed-environment`

**해결**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 문제 2: 의존성 충돌
**에러**: `supabase 2.0.3` vs `httpx==0.25.2` 충돌

**해결**: `httpx==0.24.1`로 다운그레이드

### 문제 3: 환경변수 누락
**에러**: `Field required [type=missing]`

**해결**: `.env` 파일을 `backend/` 폴더로 복사

### 문제 4: 추가 환경변수 거부
**에러**: `Extra inputs are not permitted`

**해결**: `config.py`에 `extra = "ignore"` 추가
```python
class Config:
    env_file = ".env"
    case_sensitive = False
    extra = "ignore"  # 추가 환경변수 무시
```

### 문제 5: 환경변수 이름 불일치
**에러**: `supabase_key` vs `SUPABASE_SERVICE_ROLE_KEY`

**해결**: `config.py`에서 `supabase_service_role_key`로 변경

---

## 📊 Supabase 연동

### 환경변수
```bash
SUPABASE_URL=https://gusmxyyzlchkdusmbsdk.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
```

### 쿼리 예시
```python
# Global Insights
response = db.table("MVP2_global_topics").select("""
    id, title_ko, title_en, intro_ko, intro_en,
    article_count, country_count,
    perspectives:MVP2_perspectives(
        country_code, stance, one_liner_ko, one_liner_en,
        country:MVP2_countries(name_ko, name_en, flag_emoji)
    )
""").order("rank").limit(10).execute()

# Local Trends
response = db.table("MVP2_local_topics").select(
    "id, title, keyword, article_count, media_type, media_url"
).eq("country_code", country).order(
    "article_count", desc=True
).range(start, end).execute()
```

---

## 🧪 테스트 방법

### 1. 서버 실행
```bash
cd /Users/sml/Downloads/code/MVP2/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 2. API 문서 확인
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. 엔드포인트 테스트
```bash
# Health Check
curl http://localhost:8000/health

# Global Insights
curl http://localhost:8000/api/global/insights

# Local Trends
curl "http://localhost:8000/api/local/trends?country=KR&page=1&limit=20"
```

---

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 앱
│   ├── api/
│   │   ├── __init__.py
│   │   ├── global_insights.py  # Global API
│   │   └── local_trends.py     # Local API
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # 설정
│   │   └── database.py         # Supabase 클라이언트
│   └── schemas/
│       ├── __init__.py
│       └── api.py              # Pydantic 스키마
├── venv/                       # 가상환경
├── requirements.txt            # 의존성
├── .env                        # 환경변수 (gitignore)
├── .env.example                # 환경변수 예시
└── README.md                   # 문서
```

---

## 🎯 다음 단계

### Phase 2 완료 체크리스트
- [x] Supabase 테이블 마이그레이션 파일 작성
- [x] FastAPI 프로젝트 구조 설정
- [x] GET /api/global/insights 엔드포인트 구현
- [x] GET /api/global/insights/{id} 엔드포인트 구현
- [x] GET /api/local/trends 엔드포인트 구현
- [ ] 백엔드 API 테스트 (실제 데이터로)

### 다음 작업
1. **G (Gemini)**: 데이터 파이프라인 개발
   - RSS 수집 스크립트
   - LLM 번역/생성
   - 스탠스 분석
   - 임베딩 생성
   - 토픽 추출/병합

2. **O (Codex)**: 프론트엔드 개발
   - Next.js API 연결
   - Global 탭 UI
   - VS 카드 상세 페이지
   - Local 탭 Mosaic 레이아웃

3. **C (Claude)**: 통합 테스트
   - 실제 데이터로 API 테스트
   - 성능 측정
   - 에러 처리 검증

---

## 📝 주요 코드 스니펫

### FastAPI 앱 초기화
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="News Spectrum API",
    version="1.0.0",
    description="News Spectrum MVP2 Backend API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Supabase 클라이언트
```python
from supabase import create_client, Client
from functools import lru_cache

@lru_cache()
def get_supabase_client() -> Client:
    settings = get_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )
```

### API 엔드포인트 예시
```python
@router.get("/insights", response_model=list[GlobalInsightSchema])
async def get_global_insights(db: Client = Depends(get_db)):
    response = db.table("MVP2_global_topics").select("""
        id, title_ko, title_en, article_count, country_count,
        perspectives:MVP2_perspectives(...)
    """).order("rank").limit(10).execute()
    
    return [transform(topic) for topic in response.data]
```

---

## ⚠️ 주의사항

### 1. 환경변수 보안
- `.env` 파일은 절대 Git에 커밋하지 않음
- `.gitignore`에 포함되어 있음
- Service Role Key는 서버에서만 사용

### 2. CORS 설정
- 현재 `localhost:3000` 허용
- 프로덕션 배포 시 실제 도메인 추가 필요

### 3. 에러 처리
- 모든 엔드포인트에 try-except 구현
- 적절한 HTTP 상태 코드 반환
- 에러 메시지 표준화

### 4. 성능
- Supabase 클라이언트 캐싱 (`@lru_cache`)
- 필요한 필드만 SELECT
- 페이지네이션 구현

---

## 📊 성능 목표

### API 응답 시간
- Global Insights: < 500ms
- Global Detail: < 300ms
- Local Trends: < 400ms

### 동시 접속
- 목표: 100 req/s
- 현재: 테스트 필요

---

**작업 완료**: 2025-11-29 00:11  
**서버 상태**: ✅ Running on http://127.0.0.1:8000  
**API 문서**: http://localhost:8000/docs
