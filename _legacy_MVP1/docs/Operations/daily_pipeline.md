# Daily Data Pipeline Runbook (MVP)

## What this does
- Runs the RSS → cluster → Gemini stance classification → aggregate pipeline.
- Upserts results into Supabase tables `topics` and `topic_country_stats` via `infra/scripts/push_megatopics.js`.
- Triggered daily at **23:30 KST (14:30 UTC)** and manually via `workflow_dispatch`.

## GitHub Actions
- Workflow: `.github/workflows/daily_pipeline.yml`
- Secrets required:
  - `GEMINI_API_KEY`
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY` (service role key; anon key will fail inserts)
  - Optional (schema differences): `SUPABASE_TOPICS_TABLE` (default `topics`), `SUPABASE_TOPIC_STATS_TABLE` (default `topic_country_stats`), `SUPABASE_TITLE_COLUMN` (default `title`; set to `title_kr` if your table uses that).
- Runtimes:
  - Python 3.11 for `data/pipelines/*.py`
  - Node 20 for Supabase upsert script

## Manual run (local)
```bash
cd data/pipelines
pip install -r requirements.txt
GEMINI_API_KEY=... python fetch_rss.py
python cluster_topics.py
python classify_stance.py
python aggregate_megatopics.py

# From repo root (needs service role key)
SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... \
  SUPABASE_TOPICS_TABLE=topics \
  SUPABASE_TOPIC_STATS_TABLE=topic_country_stats \
  SUPABASE_TITLE_COLUMN=title \
  node infra/scripts/push_megatopics.js data/pipelines/final_megatopics.json
```

## Failure handling (TBD)
- Alerts channel: **TBD (S to choose)**
- If GitHub Actions fails:
  - Check logs for missing secrets or API errors.
  - Re-run with `workflow_dispatch` after fixing secrets/connectivity.
- If Supabase upsert fails:
  - Verify service role key and table schema (see `infra/supabase/migrations/20251125000000_initial_schema.sql`).
- If Gemini API fails:
  - Pipeline falls back to mock stance classification; quality drops but run completes.
