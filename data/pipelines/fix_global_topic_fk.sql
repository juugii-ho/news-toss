-- Fix foreign key constraint for global_topic_id

-- Step 1: Clear all existing global_topic_id values (they reference wrong table)
UPDATE mvp2_articles SET global_topic_id = NULL WHERE global_topic_id IS NOT NULL;

-- Step 2: Drop the old constraint referencing mvp2_global_topics
ALTER TABLE mvp2_articles 
DROP CONSTRAINT IF EXISTS mvp2_articles_global_topic_id_fkey;

-- Step 3: Add new constraint referencing mvp2_megatopics
ALTER TABLE mvp2_articles 
ADD CONSTRAINT mvp2_articles_global_topic_id_fkey 
FOREIGN KEY (global_topic_id) 
REFERENCES mvp2_megatopics(id) 
ON DELETE SET NULL;
