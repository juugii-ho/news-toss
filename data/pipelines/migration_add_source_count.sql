-- Add source_count column to mvp2_topics table
ALTER TABLE mvp2_topics 
ADD COLUMN IF NOT EXISTS source_count INT;

-- Optional: Backfill with 1 for existing rows (or leave null)
UPDATE mvp2_topics SET source_count = 1 WHERE source_count IS NULL;
