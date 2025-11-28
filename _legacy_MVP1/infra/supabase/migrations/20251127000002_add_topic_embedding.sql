-- Add centroid_embedding to mvp_topics
ALTER TABLE mvp_topics ADD COLUMN IF NOT EXISTS centroid_embedding VECTOR(768);
