"""
Local Trends API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from app.core.database import get_db
from app.schemas.api import LocalTrendsResponse, LocalTopicSchema, ErrorResponse


router = APIRouter(prefix="/local", tags=["Local Trends"])


def calculate_display_level(index: int, total: int) -> int:
    """Calculate display level based on article count ranking"""
    # 상위 20%: Lv 1 (큰 카드)
    # 중간 30%: Lv 2 (중간 카드)
    # 하위 50%: Lv 3 (작은 카드)
    lv1_threshold = int(total * 0.2)
    lv2_threshold = int(total * 0.5)
    
    if index < lv1_threshold:
        return 1
    elif index < lv2_threshold:
        return 2
    else:
        return 3


@router.get(
    "/trends",
    response_model=LocalTrendsResponse,
    summary="Get local trends by country",
    description="국가별 트렌드 토픽 목록을 조회합니다 (Mosaic 레이아웃).",
    responses={400: {"model": ErrorResponse}},
)
async def get_local_trends(
    country: str = Query(..., description="국가 코드 (예: KR, US, GB)", min_length=2, max_length=2),
    page: int = Query(1, description="페이지 번호", ge=1),
    limit: int = Query(20, description="페이지당 항목 수", ge=1, le=50),
    db: Client = Depends(get_db),
):
    """Get local trends for a specific country"""
    try:
        # Validate country code
        country_response = db.table("mvp2_countries").select("name_ko, name_en").eq(
            "code", country.upper()
        ).execute()
        
        if not country_response.data:
            raise HTTPException(
                status_code=400,
                detail={"error": "Bad Request", "message": "Invalid country code"},
            )
        
        country_data = country_response.data[0]
        
        # Get total count
        count_response = db.table("mvp2_local_topics").select(
            "id", count="exact"
        ).eq("country_code", country.upper()).execute()
        
        total_count = count_response.count or 0
        
        # Get topics with pagination
        start = (page - 1) * limit
        end = start + limit - 1
        
        topics_response = db.table("mvp2_local_topics").select(
            "id, title, keyword, article_count, media_type, media_url"
        ).eq("country_code", country.upper()).order(
            "article_count", desc=True
        ).order("created_at", desc=True).range(start, end).execute()
        
        # Transform topics with display_level
        topics = []
        for index, topic in enumerate(topics_response.data):
            # Calculate global index for display level
            global_index = start + index
            display_level = calculate_display_level(global_index, total_count)
            
            topics.append(
                LocalTopicSchema(
                    topic_id=topic["id"],
                    title=topic["title"],
                    keyword=topic.get("keyword"),
                    article_count=topic["article_count"],
                    display_level=display_level,
                    media_type=topic.get("media_type"),
                    media_url=topic.get("media_url"),
                )
            )
        
        return LocalTrendsResponse(
            country_code=country.upper(),
            country_name_ko=country_data["name_ko"],
            country_name_en=country_data["name_en"],
            topics=topics,
            page=page,
            total_count=total_count,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal Server Error", "message": str(e)},
        )
