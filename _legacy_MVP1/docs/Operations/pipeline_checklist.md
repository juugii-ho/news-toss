# Pipeline Checklist (Supabase + Aggregation)

## Targets
- Source table: confirm (`mvp_articles` or `articles`) with fields `title`, `title_en`, `summary`, `country_code`, `stance`, `stance_score`.
- Output tables: `mvp_topics`, `mvp_topic_country_stats` (or chosen pair).
- Schema check: `stance_score` exists, `title_en/title_kr` present.

## Flow (choose one and align GA)
- RSS-based: fetch_rss -> cluster -> classify -> aggregate -> push_megatopics.js
- DB-based: fetch_from_db -> translate -> (optional embed) -> classify -> cluster -> aggregate -> push
- Ensure GA matches the chosen flow; do not mix.

## Steps (per run)
1) Fetch: verify source (RSS vs DB) and env keys (Supabase URL/key, service role if writing).
2) Translate/Embed (if applicable): ensure title_en/title_kr populated before stance.
3) Classify: `classify_stance.py` writes `stance` + `stance_score` to correct table.
4) Cluster/Aggregate: enforce “3+ countries -> megatopic” rule; log how many topics dropped.
5) Push: `push_megatopics.js` target tables (env overrides) align with migrations.

## Success Criteria
- Megatopics count reasonable (e.g., 3–5/day) and each has ≥3 countries.
- No missing critical fields (title/title_kr/summary/thumbnail_url) in output.
- Stance fields populated (not all fallback factual).

## Rollback/Debug
- If GA fails, check env secrets and schema (`stance_score` etc.).
- Validate intermediate JSON (`raw_articles.json`, `classified_topics.json`, `final_megatopics.json`) before push.
- Switch to manual run locally with service role key to isolate RSS/DB issues.
