
-- Migration to add missing columns to mvp_articles
ALTER TABLE public.mvp_articles
ADD COLUMN IF NOT EXISTS stance_score INT;

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_articles_stance_score ON public.mvp_articles(stance_score);
