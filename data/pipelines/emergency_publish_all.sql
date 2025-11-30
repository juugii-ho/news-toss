-- EMERGENCY FIX: Publish all existing NULL data
-- This is a ONE-TIME migration for existing production data

BEGIN;

-- 1. Set all NULL megatopics to published
UPDATE mvp2_megatopics
SET is_published = true
WHERE is_published IS NULL;

-- 2. Set all NULL topics to published  
UPDATE mvp2_topics
SET is_published = true
WHERE is_published IS NULL;

-- 3. Set all FALSE megatopics to published (if any)
-- This handles any draft data that was created during testing
UPDATE mvp2_megatopics
SET is_published = true
WHERE is_published = false;

-- 4. Set all FALSE topics to published (if any)
UPDATE mvp2_topics
SET is_published = true
WHERE is_published = false;

COMMIT;

-- Verify the results
SELECT 
    'megatopics' as table_name,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE is_published = true) as published,
    COUNT(*) FILTER (WHERE is_published = false) as unpublished,
    COUNT(*) FILTER (WHERE is_published IS NULL) as null_count
FROM mvp2_megatopics
UNION ALL
SELECT 
    'topics' as table_name,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE is_published = true) as published,
    COUNT(*) FILTER (WHERE is_published = false) as unpublished,
    COUNT(*) FILTER (WHERE is_published IS NULL) as null_count
FROM mvp2_topics;
