-- Fix foreign key constraint for global_topic_id
-- Drop the old constraint referencing mvp2_global_topics
ALTER TABLE mvp2_articles 
DROP CONSTRAINT IF EXISTS mvp2_articles_global_topic_id_fkey;

-- Add new constraint referencing mvp2_megatopics
ALTER TABLE mvp2_articles 
ADD CONSTRAINT mvp2_articles_global_topic_id_fkey 
FOREIGN KEY (global_topic_id) 
REFERENCES mvp2_megatopics(id) 
ON DELETE SET NULL;
