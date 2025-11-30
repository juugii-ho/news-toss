# Headline System V2 Update (2025-11-29)

## 🎯 Objective
To improve the quality of news headlines on the Global Insight dashboard, moving away from vague or clickbaity titles to **informative, factual, and engaging** headlines (Newneek style).

## 🛠 Key Changes

### 1. Database Schema
- **Added `headline` column** to `mvp2_megatopics` and `mvp2_topics` tables.
- This allows us to store a curated/rewritten headline separate from the raw data title.

### 2. Pipeline: Context-Aware Headline Generator
**Script**: `data/pipelines/llm_headline_generator.py`

We evolved the generator through three iterations based on feedback:
1.  **v1 (Basic)**: Rewrote titles based on the topic name alone.
    *   *Problem*: Too vague, hallucinated details.
2.  **v2 (Anti-Clickbait)**: Explicitly banned words like "충격", "멘붕", "썰".
    *   *Problem*: Still lacked specific facts (e.g., "Who resigned?", "Why is it illegal?").
3.  **v3 (Context-Aware - FINAL)**:
    *   **Fetches 3 actual article titles** related to the topic.
    *   Feeds these titles to the LLM as "Context".
    *   **Result**: Headlines now contain specific numbers, names, and reasons (e.g., "156km Pitcher", "Legal Violation").

**Prompt Strategy**:
- **Role**: Professional News Editor for Gen-Z.
- **Rules**: "Fact + Context" structure, No ending with nouns, No sensationalism.
- **Input**: Topic Name + 3 Representative Article Titles.

### 3. Frontend: Global Insight UI
**File**: `app/frontend/components/GlobalSection.tsx` & `supabase-service.ts`

- **Sorting Logic**: Changed from "Total Articles" to **"Country Count" (Global Reach)**.
    - *Why*: A topic covered in 10 countries is more "Global" than a local scandal with 1000 articles in 1 country.
- **Tabs**: Added **"Global (All)"** vs **"Korea Related"**.
    - Allows users to quickly filter for topics involving Korea within the global context.
- **Display**: Prioritizes `headline` field; falls back to `name` if missing.

## 📝 How to Run
The headline generator is designed to run periodically (e.g., every 10-30 mins).

```bash
# Run manually
cd data/pipelines
python llm_headline_generator.py
```

## ✅ Examples of Improvement

| Type | Before (Raw/v1) | After (v3 Context-Aware) |
|------|----------------|--------------------------|
| **Global** | "푸틴 예산안 서명" | **"푸틴, 2026~2028년 예산안 공식 서명 💸"** |
| **Sports** | "한화 이글스 투수 영입" | **"한화, 156km 강속구 신인 투수 영입 + 페라자 컴백! ⚾"** |
| **Legal** | "YTN 인수 승인 위법 논란" | **"법원 2인 방통위 YTN 인수 승인 위법 판결, 민영화 원점 📉"** |

---
*Written by Gemini Agent*
