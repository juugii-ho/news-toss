-- Create table for Local Topics (Country-specific)
CREATE TABLE IF NOT EXISTS mvp2_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_code TEXT NOT NULL,
    topic_name TEXT NOT NULL,
    topic_name_en TEXT, -- Optional: English translation
    summary TEXT, -- Optional: AI summary
    article_ids UUID[] NOT NULL, -- Array of article IDs
    article_count INT NOT NULL,
    source_count INT, -- Number of unique news sources
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadata from analysis
    stances JSONB, -- {factual: [], critical: [], supportive: []}
    keywords TEXT[],
    category TEXT
);

-- Create table for Global Megatopics
CREATE TABLE IF NOT EXISTS mvp2_megatopics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    name_en TEXT, -- Optional
    summary TEXT, -- Optional
    countries TEXT[] NOT NULL, -- List of country codes involved
    total_articles INT NOT NULL,
    
    -- JSONB to store the hierarchy/structure
    -- We store the full structure here for easy frontend rendering without complex joins
    content JSONB NOT NULL, 
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_mvp2_topics_country ON mvp2_topics(country_code);
CREATE INDEX IF NOT EXISTS idx_mvp2_topics_created_at ON mvp2_topics(created_at);
CREATE INDEX IF NOT EXISTS idx_mvp2_megatopics_created_at ON mvp2_megatopics(created_at);
