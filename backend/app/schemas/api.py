"""
Pydantic schemas for API responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


# ============================================================================
# Global Insights Schemas
# ============================================================================

class PerspectiveSchema(BaseModel):
    """국가별 관점 (VS 카드)"""
    country_code: str = Field(..., description="국가 코드 (예: US, KR)")
    country_name_ko: str = Field(..., description="국가명 (한국어)")
    country_name_en: str = Field(..., description="국가명 (영어)")
    flag_emoji: str = Field(..., description="국기 이모지")
    stance: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"] = Field(..., description="스탠스")
    one_liner_ko: str = Field(..., description="한 줄 요약 (한국어)")
    one_liner_en: str = Field(..., description="한 줄 요약 (영어)")
    source_link: Optional[str] = Field(None, description="출처 링크")
    
    class Config:
        json_schema_extra = {
            "example": {
                "country_code": "US",
                "country_name_ko": "미국",
                "country_name_en": "United States",
                "flag_emoji": "🇺🇸",
                "stance": "POSITIVE",
                "one_liner_ko": "경제 회복의 필수 조치",
                "one_liner_en": "Essential for economic recovery",
                "source_link": "https://example.com/article"
            }
        }


class GlobalInsightSchema(BaseModel):
    """글로벌 인사이트"""
    id: str = Field(..., description="토픽 ID (UUID)")
    title_ko: str = Field(..., description="제목 (한국어)")
    title_en: str = Field(..., description="제목 (영어)")
    intro_ko: str = Field(..., description="소개 (한국어)")
    intro_en: str = Field(..., description="소개 (영어)")
    article_count: int = Field(..., description="관련 기사 수")
    country_count: int = Field(..., description="관련 국가 수")
    perspectives: list[PerspectiveSchema] = Field(..., description="국가별 관점")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title_ko": "트럼프 관세 정책",
                "title_en": "Trump Tariff Policy",
                "intro_ko": "미국 트럼프 대통령의 새로운 관세 정책이 전 세계 경제에 미치는 영향",
                "intro_en": "Impact of President Trump's new tariff policy on global economy",
                "article_count": 150,
                "country_count": 8,
                "perspectives": []
            }
        }


# ============================================================================
# Local Trends Schemas
# ============================================================================

class LocalTopicSchema(BaseModel):
    """로컬 트렌드 토픽"""
    topic_id: str = Field(..., description="토픽 ID (UUID)")
    title: str = Field(..., description="제목")
    keyword: Optional[str] = Field(None, description="키워드")
    article_count: int = Field(..., description="관련 기사 수")
    display_level: Literal[1, 2, 3] = Field(..., description="표시 레벨 (1=큰, 2=중간, 3=작은)")
    media_type: Optional[Literal["image", "video"]] = Field(None, description="미디어 타입")
    media_url: Optional[str] = Field(None, description="미디어 URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic_id": "660e8400-e29b-41d4-a716-446655440001",
                "title": "윤석열 대통령 계엄령 선포",
                "keyword": "계엄령",
                "article_count": 45,
                "display_level": 1,
                "media_type": "image",
                "media_url": "https://example.com/image.jpg"
            }
        }


class LocalTrendsResponse(BaseModel):
    """로컬 트렌드 응답"""
    country_code: str = Field(..., description="국가 코드")
    country_name_ko: str = Field(..., description="국가명 (한국어)")
    country_name_en: str = Field(..., description="국가명 (영어)")
    topics: list[LocalTopicSchema] = Field(..., description="토픽 목록")
    page: int = Field(..., description="현재 페이지")
    total_count: int = Field(..., description="전체 토픽 수")
    
    class Config:
        json_schema_extra = {
            "example": {
                "country_code": "KR",
                "country_name_ko": "한국",
                "country_name_en": "South Korea",
                "topics": [],
                "page": 1,
                "total_count": 156
            }
        }


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str = Field(..., description="에러 타입")
    message: str = Field(..., description="에러 메시지")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Not Found",
                "message": "Global insight not found"
            }
        }
