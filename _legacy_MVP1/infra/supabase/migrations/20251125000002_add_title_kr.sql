-- Add title_kr column to mvp_topics
alter table public.mvp_topics add column if not exists title_kr text;
