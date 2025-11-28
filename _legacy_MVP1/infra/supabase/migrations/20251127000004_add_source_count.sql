-- Add source_count to mvp_topic_country_stats for better ranking
-- This tracks unique news sources covering a topic per country

alter table public.mvp_topic_country_stats 
  add column if not exists source_count int default 0;

-- Add comment
comment on column public.mvp_topic_country_stats.source_count is 'Number of unique news sources covering this topic in this country';
