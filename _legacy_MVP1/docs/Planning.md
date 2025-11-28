# Planning: MVP & Roadmap

> IMPORTANT FOR ALL LLMS  
> - DO NOT delete, shorten, or aggressively rewrite any bullet points in this file unless S explicitly asks you to.  
> - When updating this file, prefer **adding** new bullets or marking statuses rather than replacing or summarizing existing text.

---

## 1. Current Phase

- Phase: **MVP build (solo founder, ~3 months target)**
- Constraints:
  - Single developer (S) covering product, design, backend, frontend.
  - Cost sensitivity (LLM API usage must be optimized).
  - Existing stack: Next.js (web), Supabase (DB), GitHub Actions (automation), Gemini + Claude + Codex CLIs, Vercel (deployment).

---

## 2. MVP Definition (v1)

### 2.1 Data Pipeline MVP

Goal: **“Daily global megatopics summary for 10+ countries, with a basic stance spectrum.”**

Core components:

1. **News ingestion**
   - RSS feeds for key newspapers in G10 + Russia + China.
   - Initial YouTube channel set (where stance classification is at least moderately feasible).
   - Daily ingestion job via GitHub Actions.

2. **Topic detection**
   - For each country, cluster daily headlines into up to 3 country-level topics.
   - From all country-level topics, detect global megatopics (e.g. using embeddings + clustering + heuristic rules).

3. **Stance classification**
   - For each article/headline, assign supportive / factual / critical.
   - Aggregate per topic and per country.
   - Store counts in Supabase (topics table).

4. **Thumbnail generation (image pipeline)**
   - For each topic, generate 1–4 magazine-style images (no text) for cards.
   - Use Gemini-based image generation with carefully crafted prompts.
   - Support AB testing via `thumbnail_url`, `thumbnail_url2` columns, etc.

5. **Automation**
   - All of the above orchestrated by GitHub Actions (e.g. once per day at KST).

> **Data Architecture Note (2025-11-25)**
> - **Current (MVP Phase 2)**: Pipeline generates static `data.json` which is copied to frontend.
> - **Target (MVP Phase 3+)**: Pipeline will store data in Supabase, and Frontend will fetch via Supabase Client.


### 2.2 Frontend MVP

Goal: **“Within 5 minutes, a user understands today’s global megatopics and their spectra.”**

Pages / sections:

1. **Landing / Hero**
   - “Global Intelligence Platform / News Spectrum” hero copy.
   - Today’s date + short explanation of what the user will see.
   - Call-to-action to scroll into today’s megatopics.

2. **Global Megatopic List (Today)**
   - For each topic:
     - Title
     - Gentle intro text (2–3 paragraphs)
     - 3-way stance spectrum visualization (supportive / factual / critical)
     - Country flags with summary of each country’s stance.

3. **Topic Detail View (v1 simple)**
   - Same as list card but with more text:
     - Why this topic matters
     - Short descriptions of how key countries frame it.

4. **Basic Newsletter View**
   - A “printable / email-friendly” layout for the day’s topics.
   - theSkimm / Newneek-inspired narrative around each topic.

---

## 3. Roadmap (High-level)

### 3.1 Short-term (MVP, 0–3 months)

- Stabilize daily pipeline across 10+ countries.
- Implement robust Supabase schema for topics/articles/videos/channels.
- Build core landing page + megatopic list + topic detail.
- Implement basic 3-way stance bars with minimum visibility rule.
- Ship first “newsletter-style” view (web page).

### 3.2 Mid-term (3–9 months)

- Improve clustering & stance classification:
  - Experiment with language routing (raw language → English processing → Korean/English output).
  - Evaluate accuracy difference between working in English vs Korean.
- Expand to more broadcasters (where ideological stance can be reasonably inferred).
- Introduce simple user features:
  - “Follow topics/countries”
  - “Email newsletter signup”
- Add historical view:
  - Past days’ megatopics list / archive.

### 3.3 Longer-term (9+ months)

- Persona-based newsletters:
  - “Global politics”, “Markets & economy”, “Tech & regulation”, etc.
- Interactive drill-down UI:
  - More granular views for outlet-level and article-level.
- DIKW / personal knowledge integration:
  - Sync curated insights into S’s Notion / Obsidian / Supabase knowledge layer.

---

## 4. Delivery & Sprint Rhythm

- Timebox:  
  - Sprints can be 1 or 2 weeks, but MVP planning should assume **small, shippable increments**.
- For each Sprint:
  - Choose a set of DTs (Decision Topics) from `Unicorn MVP Board Meeting.md`.
  - Translate them into **TASK-xxx** entries in `Tasks.md`.
  - Ensure at least one user-visible improvement per sprint.

---

## 5. Stability Rules (for LLMs)

- Do NOT remove constraints like:
  - “Single developer”
  - “Daily pipeline”
  - “3-way stance spectrum”
- Do NOT change the definition of:
  - Global megatopic
  - Supportive / factual / critical buckets
- If you think a strategic change is needed, propose a new **Decision Topic (DT)** in the Board file instead of silently changing this file.
