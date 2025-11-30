# Database Schema (Supabase)

This document describes the current database schema for the News Toss MVP2.
Tables are in the `public` schema.

## 1. mvp2_megatopics (Global Topics)
Stores the high-level "Megatopics" that group local topics from multiple countries.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid` | Primary Key |
| `name` | `text` | Internal name (usually Korean headline) |
| `title_ko` | `text` | **[API]** Korean Title (Display) |
| `title_en` | `text` | **[API]** English Title |
| `intro_ko` | `text` | **[API]** Korean Intro/One-liner (VS Card Question) |
| `intro_en` | `text` | **[API]** English Intro |
| `summary` | `text` | Brief summary of the megatopic |
| `content` | `text` | Detailed content (required not-null) |
| `countries` | `text[]` | List of country codes involved (e.g. `['KR', 'US']`) |
| `total_articles` | `int` | Total articles across all linked topics |
| `article_count` | `int` | **[API]** Alias for total_articles |
| `country_count` | `int` | **[API]** Count of countries |
| `rank` | `int` | **[API]** Display rank (1 = Top) |
| `is_pinned` | `boolean` | **[API]** Pinned status (default false) |
| `topic_ids` | `uuid[]` | Array of `mvp2_topics.id` linked to this megatopic |
| `keywords` | `text[]` | Global keywords |
| `category` | `text` | Category (Politics, Economy, etc.) |
| `stances` | `jsonb` | VS Card Stances (Array of objects) |
| `created_at` | `timestamptz` | Creation timestamp |

### `stances` JSON Structure
```json
[
  {
    "stance": "A",
    "name": "Stance A Name",
    "desc": "Description...",
    "countries": ["KR", "US"]
  },
  {
    "stance": "B",
    "name": "Stance B Name",
    "desc": "Description...",
    "countries": ["JP"]
  }
]
```

## 2. mvp2_topics (Local Topics)
Stores clustered topics within a specific country.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid` | Primary Key |
| `country_code` | `text` | Country Code (e.g. 'KR') |
| `topic_name` | `text` | Original Topic Name |
| `topic_name_en` | `text` | English Topic Name |
| `headline` | `text` | Generated Headline (Display Title) |
| `summary` | `text` | Topic Summary |
| `article_ids` | `uuid[]` | Array of `mvp2_articles.id` |
| `article_count` | `int` | Number of articles |
| `source_count` | `int` | Number of unique sources |
| `keywords` | `text[]` | Local keywords |
| `category` | `text` | Category |
| `stances` | `jsonb` | Local Stances (Factual/Critical/Supportive) |
| `created_at` | `timestamptz` | Creation timestamp |

## 3. mvp2_articles (Articles)
Stores individual news articles scraped from RSS feeds.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid` | Primary Key |
| `url` | `text` | Article URL (Unique) |
| `title_original` | `text` | Original Title |
| `title_ko` | `text` | Korean Title (Translated) |
| `title_en` | `text` | English Title (Translated) |
| `summary_original` | `text` | Original Summary/Snippet |
| `summary_ko` | `text` | Korean Summary |
| `summary_en` | `text` | English Summary |
| `country_code` | `text` | Country Code |
| `source_name` | `text` | Source Name (e.g. 'BBC', 'Yonhap') |
| `published_at` | `timestamptz` | Publication Date |
| `collected_at` | `timestamptz` | Collection Date |
| `local_topic_id` | `uuid` | FK to `mvp2_topics` (optional) |
| `global_topic_id` | `uuid` | FK to `mvp2_megatopics` (optional/unused?) |
| `created_at` | `timestamptz` | Creation timestamp |

## Notes
- **Case Sensitivity**: Postgres table names are lowercase (`mvp2_...`). If code uses `MVP2_...`, Supabase/Postgrest might handle it if configured, but lowercase is preferred.
- **Arrays**: `text[]` and `uuid[]` are Postgres array types.
- **JSONB**: Used for flexible structured data like `stances`.
