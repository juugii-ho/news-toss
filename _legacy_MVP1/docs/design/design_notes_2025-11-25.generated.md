# Design & Product Notes (2025-11-25)

> Summary for C/G reference – Calm/Apple-like editorial dashboard for daily megatopics

## Visual Tone & Palette
- Goal: "Calm Intelligence" / Apple-like magazine style (few but clear cards, soft hierarchy).
- Background: off-white (#F5F5F7); cards: white with soft navy-tinted shadow (e.g., 0 18px 40px rgba(15,23,42,0.08)); rounded-2xl.
- Typography: tighten title tracking slightly (-0.02em), strong contrast for titles; body remains neutral.
- Stance palette (muted, accessibility-aware):
  - Supportive: ~#3B7A6F (Sage/Teal)
  - Factual/Neutral: ~#455A64–#64748B (Slate/Blue-gray)
  - Critical: ~#A63B3B (Muted Clay/Brick)
  - Unclassified (optional): very light gray

## Card Structure (Collapsed → Expanded)
- Collapsed (3-line structure):
  1) Title_KR (main) + Title_EN (small) + Last updated (small)
  2) Global SpectrumBar (one line) + one-line insight
  3) Top countries 2–3 (chips/badges)
- Expanded: country-level breakdown (spectrum/summary/headlines) and details. Keep Calm micro-interactions (no big movement; gentle transitions only).
- SpectrumBar UX: optional gentle fill on viewport enter (200–300ms), hover = delayed fade-in tooltip only (no bounce/flash).

## Hero & Page Flow
- Hero: prefer typography + CSS blur/mesh gradient (no heavy images) to protect LCP. Show "Last updated" small.
- Auto-hero copy: derive from top 3 megatopics (KR/EN) — e.g., "오늘은 A, B, 그리고 C 이슈가 뜨겁습니다." / "Today, the world splits along three stories: A, B, C.".
- Page rhythm: "5-minute routine" → Hero one-liner → 3 megatopic cards (collapsed summary) → optional one-line insights below.

## Language Handling
- Default by navigator.language; allow header toggle (KR/EN) storing preference in localStorage; aria-friendly (radiogroup). Collapsed card shows selected language as main, the other as secondary.

## Data & Pipeline Alignment (for UI fidelity)
- Gemini endpoint should use v1 (current 404 on v1beta); fallback: unclassified counts can be absorbed into factual or separately noted in text (not in bar).
- title_kr supported: Supabase upsert can override table/column via env (`SUPABASE_TOPICS_TABLE`, `SUPABASE_TOPIC_STATS_TABLE`, `SUPABASE_TITLE_COLUMN=title_kr`).
- RSS instability: replace 403/404 feeds (France24, DW, Hankyoreh, Xinhua, NHK) with stable alternatives (official RSS variants or site-filtered news APIs).

## Ops/Perf
- Daily pipeline: keep idempotent upsert (date + canonical_id/slug). Add minimal failure notifier (Slack/mail) if possible.
- Performance guard: Lighthouse (perf ≥0.85, LCP ≤2.5s, CLS ≤0.1). Use CSS-only gradients/SVG patterns for Hero/background.

## Quick Implementation Targets
- Tailwind theme: add stance palette tokens.
- MegatopicCard collapsed layout to 3-line structure; top countries chips; last updated.
- Hero background via CSS blur/mesh; inject auto-generated copy from latest topics; show last updated.
- Language toggle in header (KR/EN) with localStorage + aria roles.
