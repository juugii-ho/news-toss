# Position: Global Intelligence Platform / News Spectrum

> IMPORTANT FOR ALL LLMS  
> - DO NOT rewrite, summarize, or delete content in this file unless "S" (the founder) explicitly instructs you to do so.  
> - Treat this file as SOURCE OF TRUTH for product vision and positioning.  
> - If a shorter version is needed, create a separate summary file (e.g. `Position.summary.generated.md`) instead of editing this file.

---

## 1. Product Family Overview

This repository represents the main product family of **S** (solo founder):

1. **News Spectrum / Global Intelligence Platform**  
   - A service that aggregates news from ~G10 + Russia + China (and more later),  
   - Detects **global megatopics**,  
   - Shows how different countries and media outlets position themselves along a **three-way stance spectrum** (supportive / factual / critical),  
   - And delivers this in a calm, clear, almost “editorial magazine + Apple-style” interface and newsletter.

2. **(Secondary projects – context only, separate repos or phases)**  
   - Smart Calendar Viewer (Google Calendar/Tasks based daily view for S).  
   - AI copyright & data-governance research (academic/long-term).

For this repo, assume **News Spectrum is the primary focus**.

---

## 2. Core Mission & Value

**Mission:**  
Help people understand global issues not as a single headline, but as a spectrum of perspectives across countries, blocs, and media outlets – in a way that is **easy, calm, and non-overwhelming**.

**Core value proposition:**

- There is too much information; people give up before they even start reading.  
- Foreign coverage is often reduced to a few big headlines or gossip-level curiosity.  
- News Spectrum:
  - Picks **a few “global megatopics” per day**,  
  - Shows **how different countries and ideological blocs talk about them**,  
  - And lets the user zoom in from **topic → country → outlet → article** if they want more depth.

Key phrase S often uses internally:

> “Don’t be biased. Understand completely.”  
> “같은 사건도 바라보는 위치에 따라 전혀 다른 모습이 됩니다.”

---

## 3. Target Users

### 3.1 Primary Targets

1. **Curious global citizens**  
   - People interested in geopolitics, international relations, or global business,  
   - Who want to see “how each country reacts” without wading through 50 tabs.

2. **Knowledge workers / students / journalists / analysts**  
   - Need a quick but nuanced overview of global topics,  
   - Use the stance breakdown and country comparison as a starting point for deeper work.

3. **Foreigners in Korea / Koreans abroad**  
   - Want to understand how their home country and other countries see the same topic differently.

### 3.2 Secondary Targets

- People who enjoy services like **Newneek**, **theSkimm**, but want more of a global, comparative angle.
- People who want a soft, guided “newsletter” that combines storytelling with structured data.

---

## 4. Core Concepts & Data Model

### 4.1 Global Megatopic

- A **daily or near-daily macro topic** that appears across multiple countries’ major media.  
- Examples:
  - “US rate cut and global market reactions”
  - “EU–Russia security negotiations”
  - “Major conflict / climate / tech regulation issues”

Each Megatopic has:

- Date
- Topic name (human-readable)
- List of related articles (by country and outlet)
- Country-level stance distribution
- Short summary + explanation of why this is important now

### 4.2 Three-way Stance Spectrum

Instead of simple positive/negative, News Spectrum uses **three buckets**:

1. **Supportive (or generally favorable / aligned)**
2. **Factual (informational / neutral tone)**
3. **Critical (concerned / opposing)**

These are currently implemented as:

- Supportive / Factual / Critical counts per topic and country  
- Represented visually as a stacked bar spectrum (with e.g. minimum 3% display so tiny segments still appear as visible slivers).

> IMPORTANT: The spectrum is **about the media stance**, not about “truth” or “who is right”.  
> The service aims to **show the landscape**, not to judge it.

### 4.3 Drill-down Layers

The user can choose to stay at a shallow layer, or go deeper:

1. Topic-level:  
   - “For this global topic, how is the world split overall?”
2. Country-level:  
   - “How does Country A vs Country B vs Country C frame this?”
3. Outlet-level:  
   - “Within Country A, which outlets are more supportive or more critical?”
4. Article-level (future / extended):  
   - Specific headlines and links.

---

## 5. Product Principles

These principles must guide UX, content, and automation:

1. **Few but clear topics per day**  
   - Prioritize **clarity over coverage**.  
   - It is better to have 3 excellent megatopics than 30 noisy cards.

2. **Non-overwhelming layouts**  
   - The service should feel **calm, structured, almost like reading a well-designed magazine**.  
   - Avoid noisy dashboards that look like a trading screen.

3. **Soft guidance text before data**  
   - Before showing spectra and charts, lead with 2–3 gentle paragraphs that explain:
     - Why this topic matters now  
     - How countries are generally positioned
   - The tone should be friendly and accessible, similar to Newneek/theSkimm but slightly more “editorial”.

4. **Drill-down is optional, not required**  
   - A casual user should understand the gist in **under 5 minutes** without drilling into all levels.
   - Power users can dig into country/outlet/article levels when they want.

5. **Daily automation as a backbone**  
   - RSS and YouTube ingestion should run automatically (GitHub Actions + Supabase + scripts).  
   - The UI should reflect the latest available pipeline output, even if only partially refined.

6. **Explainable structure, LLM-assisted content**  
   - Core structure (clustering, stance classification framework, etc.) is algorithmic and explainable.  
   - LLMs “assist” with summarization, naming, and narrative, but do not silently override structure.

---

## 6. Scope & Non-goals (for MVP)

**In scope (MVP):**

- G10 + Russia + China news sources (RSS-based), plus a small curated set of YouTube channels.
- Daily pipeline that:
  - Collects headlines per country
  - Detects 1–3 megatopics per country
  - Aggregates these into global megatopics
  - Attaches stance distributions per country.
- Basic web UI:
  - Hero with “Today’s Global Megatopics”
  - Cards for each topic with 3-way spectrum and country flags
  - Links to “Newsletter-like” text view.

**Out of scope (MVP, may come later):**

- Full-text crawling of every article (heavy scraping).
- Real-time intraday updates (start with daily).
- Deep personalized recommendation (per-user profiles, etc.).
- Full coverage of broadcasters where ideological classification is unclear (YouTube broadcaster stance classification is a later-stage problem).

---

## 7. Brand, Tone & Visual Identity

### 7.1 Tone

- Calm, empathetic, and slightly editorial.  
- Not sensational, not clickbait.  
- Gentle humor is allowed but never at the expense of serious issues.

Internal inspirations:

- **Newneek** and **theSkimm** for approachable newsletter tone.
- **Apple-like clarity** for hero and landing page layouts.

### 7.2 Visual

- Light, spacious layouts (Apple-esque).
- Retro color ideas can be used, but overall feeling should remain “modern, clean, calm”.
- Spectrum visualizations:
  - Simple, readable stacked bars
  - Minimum segment percentage for visibility (e.g. 3%) to avoid disappearing minorities.

---

## 8. Long-term Vision

- Expand beyond 12 countries to more regions and languages.
- Offer historical timelines of how stances shift over time.
- Build persona-based newsletters (e.g. “global markets watcher”, “international politics”, “tech & regulation”) using the same pipeline.
- Integrate with S’s broader personal knowledge ecosystem (Notion, Supabase, Obsidian, etc.) so that News Spectrum becomes a core **“global DIKW engine”** in S’s life.
