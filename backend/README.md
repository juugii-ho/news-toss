# FastAPI Backend

## 🚀 Quick Start

### 1. 환경 설정
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 환경변수 설정
```bash
cp .env.example .env
# .env 파일에 Supabase 정보 입력
```

### 3. 서버 실행
```bash
# 개발 모드 (auto-reload)
uvicorn app.main:app --reload --port 8000

# 또는
python -m app.main
```

### 4. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── api/                    # API 엔드포인트
│   │   ├── global_insights.py  # Global Insights API
│   │   └── local_trends.py     # Local Trends API
│   ├── core/                   # 핵심 설정
│   │   ├── config.py           # 앱 설정
│   │   └── database.py         # Supabase 클라이언트
│   ├── schemas/                # Pydantic 스키마
│   │   └── api.py              # API 응답 스키마
│   └── main.py                 # FastAPI 앱
├── requirements.txt            # 의존성
├── .env.example                # 환경변수 예시
└── README.md                   # 이 파일
```

---

## 🌐 API 엔드포인트

### Global Insights

#### GET /api/global/insights
글로벌 인사이트 Top 10 목록 조회

**Response:**
```json
[
  {
    "id": "uuid",
    "title_ko": "트럼프 관세 정책",
    "title_en": "Trump Tariff Policy",
    "intro_ko": "...",
    "intro_en": "...",
    "article_count": 150,
    "country_count": 8,
    "perspectives": [...]
  }
]
```

#### GET /api/global/insights/{id}
특정 글로벌 인사이트 상세 조회

**Response:**
```json
{
  "id": "uuid",
  "title_ko": "트럼프 관세 정책",
  "perspectives": [
    {
      "country_code": "US",
      "country_name_ko": "미국",
      "flag_emoji": "🇺🇸",
      "stance": "POSITIVE",
      "one_liner_ko": "경제 회복의 필수 조치"
    }
  ]
}
```

### Local Trends

#### GET /api/local/trends?country=KR&page=1&limit=20
국가별 트렌드 토픽 목록 조회

**Query Parameters:**
- `country` (required): 국가 코드 (예: KR, US, GB)
- `page` (optional): 페이지 번호 (기본값: 1)
- `limit` (optional): 페이지당 항목 수 (기본값: 20, 최대: 50)

**Response:**
```json
{
  "country_code": "KR",
  "country_name_ko": "한국",
  "country_name_en": "South Korea",
  "topics": [
    {
      "topic_id": "uuid",
      "title": "윤석열 대통령 계엄령 선포",
      "article_count": 45,
      "display_level": 1
    }
  ],
  "page": 1,
  "total_count": 156
}
```

---

## 🔧 개발 가이드

### 새 엔드포인트 추가

1. `app/api/` 에 새 파일 생성
2. `APIRouter` 생성 및 엔드포인트 정의
3. `app/main.py` 에 라우터 추가

```python
# app/api/new_endpoint.py
from fastapi import APIRouter

router = APIRouter(prefix="/new", tags=["New"])

@router.get("/")
async def get_new():
    return {"message": "Hello"}

# app/main.py
from app.api import new_endpoint
app.include_router(new_endpoint.router, prefix="/api")
```

### 스키마 추가

`app/schemas/api.py` 에 Pydantic 모델 추가

```python
class NewSchema(BaseModel):
    field1: str
    field2: int
```

---

## 🧪 테스트

```bash
# 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app
```

---

## 📊 성능 최적화

### 1. 데이터베이스 쿼리 최적화
- 필요한 필드만 SELECT
- 적절한 인덱스 사용
- JOIN 최소화

### 2. 캐싱
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_data(key: str):
    # ...
```

### 3. 비동기 처리
```python
async def fetch_data():
    # 비동기 DB 쿼리
```

---

## 🚀 배포

### Vercel (권장)
```bash
# vercel.json 설정 후
vercel deploy
```

### Docker
```bash
docker build -t newsspectrum-api .
docker run -p 8000:8000 newsspectrum-api
```

---

## 📝 환경변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `SUPABASE_URL` | Supabase 프로젝트 URL | https://xxx.supabase.co |
| `SUPABASE_KEY` | Supabase Anon Key | eyJhbGc... |
| `DEBUG` | 디버그 모드 | True/False |

---

**작성일**: 2025-11-28  
**작성자**: C (Claude Code)
