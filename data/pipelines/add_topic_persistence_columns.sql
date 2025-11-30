-- Add columns for topic persistence tracking
ALTER TABLE mvp2_topics 
ADD COLUMN IF NOT EXISTS first_seen_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_topics_active_recent 
ON mvp2_topics(country_code, is_active, created_at DESC) 
WHERE is_active = TRUE;

-- Create thumbnail cache table
CREATE TABLE IF NOT EXISTS mvp2_thumbnail_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_name TEXT NOT NULL,
    country_code TEXT NOT NULL,
    thumbnail_url TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ DEFAULT NOW(),
    use_count INTEGER DEFAULT 1,
    UNIQUE(topic_name, country_code)
);

CREATE INDEX IF NOT EXISTS idx_thumbnail_cache_lookup 
ON mvp2_thumbnail_cache(topic_name, country_code);

CREATE INDEX IF NOT EXISTS idx_thumbnail_cache_created 
ON mvp2_thumbnail_cache(created_at DESC);
