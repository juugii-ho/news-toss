-- Add headline field for news-style titles (뉴닉 스타일)
-- This is separate from title_kr which is used for backend/factual reference

ALTER TABLE public.mvp_topics 
  ADD COLUMN IF NOT EXISTS headline TEXT;

-- Add comment
COMMENT ON COLUMN public.mvp_topics.headline IS '뉴닉 스타일 뉴스 제목 (프론트엔드 노출용, 50자 이내, 궁금증 유발형)';
