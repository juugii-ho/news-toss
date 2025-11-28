-- Enable pgvector extension
create extension if not exists vector;

-- Add embedding column to mvp_articles
-- Gemini Pro embedding dimension is 768
alter table public.mvp_articles add column if not exists embedding vector(768);

-- Create an index for faster similarity search (optional for MVP but good practice)
create index on public.mvp_articles using ivfflat (embedding vector_cosine_ops)
with (lists = 100);
