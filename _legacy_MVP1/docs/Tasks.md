# Tasks

> IMPORTANT  
> - Tasks link decisions (DTs) to concrete work.  
> - Do NOT delete tasks. If a task is obsolete, mark it as CANCELLED with a reason.  
> - Tools should only change Status and append Notes.

---

## Format

Each task:

- TASK-ID: unique identifier (e.g. TASK-020-1)
- Related DT: which Decision Topic it comes from (e.g. DT-020)
- Owner Tool: C / G / O / S
- Directory: main working directory
- Status: TODO | DOING | DONE | CANCELLED
- Brief: short description
- Notes: optional notes, can grow over time.

---

## Current Tasks (Initial Example Set)

### Topic: Global Megatopics UI (DT-020, hypothetical)

- TASK-020-1  
  - Related DT: DT-020  
  - Owner Tool: G  
  - Directory: docs/design/  
  - Status: TODO  
  - Brief: Write hero copy and subcopy variants (3 options) for the News Spectrum landing page, inspired by Newneek/theSkimm but calmer.  
  - Notes: Include both Korean and English copy.

- TASK-020-2
  - Related DT: DT-020
  - Owner Tool: C
  - Directory: app/frontend/
  - Status: DONE
  - Brief: Implement the B-style hero layout (two-column / image + text) with responsive design.
  - Notes: Use stacked cards style hinted in previous designs; keep Apple-like cleanliness. Implemented on 2025-11-25.

- TASK-020-3  
  - Related DT: DT-020  
  - Owner Tool: O  
  - Directory: infra/  
  - Status: DOING  
  - Brief: Optimize initial page load for the hero section (font loading, image lazy-loading).  
  - Notes: After implementing TASK-020-2, measure Lighthouse and adjust.
  - Notes: Add perf budget + CI check (Lighthouse or Next.js analytics) for hero above-the-fold; prioritize font subsetting/preload decisions and image placeholder strategy.
  - Notes: Coordinate with C on what assets are hosted locally vs. remote (Supabase/Vercel) to align caching strategy.

---

### Topic: Daily Pipeline Stabilization (DT-010, DT-011 etc.)

- TASK-010-1  
  - Related DT: DT-010  
  - Owner Tool: G  
  - Directory: data/pipelines/  
  - Status: DONE  
  - Brief: Ensure daily RSS ingestion for 10+ countries is idempotent and fault-tolerant (retries, logging).  

- TASK-010-2  
  - Related DT: DT-010  
  - Owner Tool: G  
  - Directory: data/pipelines/  
  - Status: DONE  
  - Brief: Implement stance aggregation (supportive/factual/critical counts) per topic and per country, storing results in Supabase `topics` table.  

- TASK-011-1
  - Related DT: DT-011
  - Owner Tool: C
- [x] **Match Topics Across Days (Topic Drift)** <!-- id: 16 -->
    - [x] Implement `match_topics_across_days.py` <!-- id: 17 -->
    - [x] Add `previous_topic_id` column to `mvp_topics` <!-- id: 18 -->
    - [x] Visualize drift (Sankey or flow) <!-- id: 19 -->
    - *Note: Successfully retried and completed on 2025-11-27.*

- [x] **Refine Visualization** <!-- id: 20 -->
    - [x] Verify `visualize_article_map.py` output <!-- id: 21 -->
    - [x] Verify `visualize_topic_bubbles_refined.py` output <!-- id: 22 -->
    - [x] Fix Translation Alignment & Deduplication (2025-11-27) <!-- id: 23 -->5 with configurable minVisiblePercent (default 3%).  

---

### Topic: UX Research Implementation (DT-050, UX Report)

- TASK-050-1
  - Related DT: DT-050 (UX Research)
  - Owner Tool: C
  - Directory: app/frontend/
  - Status: DONE
  - Brief: Implement AI transparency labels based on UX research recommendations (AI-generated badges, source attribution).
  - Notes: Added CONTENT_LABELS constants and integrated into topic detail summary section. Completed 2025-11-26.

- TASK-050-2
  - Related DT: DT-050 (UX Research)
  - Owner Tool: C
  - Directory: app/frontend/
  - Status: DONE
  - Brief: Polish UI details for "beauty vs beauty" competition - country names consistency, micro-interactions, visual hierarchy refinement.
  - Notes: Focus on details that elevate user experience quality. Completed 2025-11-26.
  - Notes: Fixed country name consistency (full names vs codes), enhanced visual hierarchy (emphasized numbers, improved spacing), refined hover effects (smoother shadows, border transitions), added micro-interactions (arrow slide on button hover).

---

> NOTE: This is a starting set. S and the web LLM will keep adding and refining tasks based on DTs and actual progress.

---

### Topic: Topic Drift & Evolution (DT-060)

- TASK-060-1
  - Related DT: DT-060
  - Owner Tool: G
  - Directory: data/pipelines/
  - Status: DONE
  - Brief: Implement backend logic for tracking topic drift (history table, matching script, pipeline integration).
  - Notes: Completed 2025-11-27. Retried successfully after network error.

- TASK-060-2
  - Related DT: DT-060
  - Owner Tool: G
  - Directory: app/frontend/
  - Status: DONE
  - Brief: Implement frontend visualization for topic timeline (API, Component, Page Integration).
  - Notes: Completed 2025-11-27.
