-- Add LLM-First pipeline fields to mvp_topics table
--
-- merged_from_topics: Track which country topics were merged into this megatopic
-- map_x, map_y: 2D visualization coordinates for topic map
-- extraction_method: 'llm' or 'vector' to track which pipeline created it

ALTER TABLE public.mvp_topics
  ADD COLUMN IF NOT EXISTS merged_from_topics TEXT[],
  ADD COLUMN IF NOT EXISTS map_x FLOAT,
  ADD COLUMN IF NOT EXISTS map_y FLOAT,
  ADD COLUMN IF NOT EXISTS extraction_method TEXT DEFAULT 'vector';

COMMENT ON COLUMN public.mvp_topics.merged_from_topics IS 'Country topic IDs that were merged into this megatopic (e.g., [''KR-topic-7'', ''US-topic-3''])';
COMMENT ON COLUMN public.mvp_topics.map_x IS '2D visualization X coordinate (t-SNE/UMAP)';
COMMENT ON COLUMN public.mvp_topics.map_y IS '2D visualization Y coordinate (t-SNE/UMAP)';
COMMENT ON COLUMN public.mvp_topics.extraction_method IS 'Topic extraction method: llm or vector';
