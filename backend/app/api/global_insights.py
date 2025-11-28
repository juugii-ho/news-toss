"""
Global Insights API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.core.database import get_db
from app.schemas.api import GlobalInsightSchema, PerspectiveSchema, ErrorResponse


router = APIRouter(prefix="/global", tags=["Global Insights"])


@router.get(
    "/insights",
    response_model=list[GlobalInsightSchema],
    summary="Get top 10 global insights",
    description="글로벌 인사이트 Top 10 목록을 조회합니다.",
)
async def get_global_insights(db: Client = Depends(get_db)):
    """Get top 10 global insights with perspectives"""
    try:
        # Query global topics with perspectives
        response = db.table("mvp2_global_topics").select(
            """
            id,
            title_ko,
            title_en,
            intro_ko,
            intro_en,
            article_count,
            country_count,
            perspectives:mvp2_perspectives(
                country_code,
                stance,
                one_liner_ko,
                one_liner_en,
                source_link,
                country:mvp2_countries(
                    name_ko,
                    name_en,
                    flag_emoji
                )
            )
            """
        ).order("rank", desc=False, nulls_last=True).order(
            "article_count", desc=True
        ).limit(10).execute()
        
        if not response.data:
            return []
        
        # Transform data
        insights = []
        for topic in response.data:
            # Transform perspectives
            perspectives = []
            for p in topic.get("perspectives", []):
                country = p.get("country", {})
                perspectives.append(
                    PerspectiveSchema(
                        country_code=p["country_code"],
                        country_name_ko=country.get("name_ko", ""),
                        country_name_en=country.get("name_en", ""),
                        flag_emoji=country.get("flag_emoji", ""),
                        stance=p["stance"],
                        one_liner_ko=p["one_liner_ko"],
                        one_liner_en=p["one_liner_en"],
                        source_link=p.get("source_link"),
                    )
                )
            
            insights.append(
                GlobalInsightSchema(
                    id=topic["id"],
                    title_ko=topic["title_ko"],
                    title_en=topic["title_en"],
                    intro_ko=topic.get("intro_ko", ""),
                    intro_en=topic.get("intro_en", ""),
                    article_count=topic["article_count"],
                    country_count=topic["country_count"],
                    perspectives=perspectives,
                )
            )
        
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal Server Error", "message": str(e)},
        )


@router.get(
    "/insights/{insight_id}",
    response_model=GlobalInsightSchema,
    summary="Get global insight detail",
    description="특정 글로벌 인사이트의 상세 정보를 조회합니다 (VS 카드).",
    responses={404: {"model": ErrorResponse}},
)
async def get_global_insight_detail(insight_id: str, db: Client = Depends(get_db)):
    """Get specific global insight detail"""
    try:
        # Query single topic with perspectives
        response = db.table("mvp2_global_topics").select(
            """
            id,
            title_ko,
            title_en,
            intro_ko,
            intro_en,
            article_count,
            country_count,
            perspectives:mvp2_perspectives(
                country_code,
                stance,
                one_liner_ko,
                one_liner_en,
                source_link,
                country:mvp2_countries(
                    name_ko,
                    name_en,
                    flag_emoji
                )
            )
            """
        ).eq("id", insight_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=404,
                detail={"error": "Not Found", "message": "Global insight not found"},
            )
        
        topic = response.data[0]
        
        # Transform perspectives
        perspectives = []
        for p in topic.get("perspectives", []):
            country = p.get("country", {})
            perspectives.append(
                PerspectiveSchema(
                    country_code=p["country_code"],
                    country_name_ko=country.get("name_ko", ""),
                    country_name_en=country.get("name_en", ""),
                    flag_emoji=country.get("flag_emoji", ""),
                    stance=p["stance"],
                    one_liner_ko=p["one_liner_ko"],
                    one_liner_en=p["one_liner_en"],
                    source_link=p.get("source_link"),
                )
            )
        
        return GlobalInsightSchema(
            id=topic["id"],
            title_ko=topic["title_ko"],
            title_en=topic["title_en"],
            intro_ko=topic.get("intro_ko", ""),
            intro_en=topic.get("intro_en", ""),
            article_count=topic["article_count"],
            country_count=topic["country_count"],
            perspectives=perspectives,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal Server Error", "message": str(e)},
        )
