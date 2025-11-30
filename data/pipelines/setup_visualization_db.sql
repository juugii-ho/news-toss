-- Add visualization columns to Megatopics
ALTER TABLE mvp2_megatopics ADD COLUMN IF NOT EXISTS x float8;
ALTER TABLE mvp2_megatopics ADD COLUMN IF NOT EXISTS y float8;

-- Add visualization columns to Local Topics
ALTER TABLE mvp2_topics ADD COLUMN IF NOT EXISTS x float8;
ALTER TABLE mvp2_topics ADD COLUMN IF NOT EXISTS y float8;
