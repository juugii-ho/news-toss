# Session Summary (2025-11-29)

## ✅ Completed Tasks

### 1. Headline System v2 (Context-Aware)
- **Problem**: Headlines were vague or clickbaity (e.g., "충격!").
- **Solution**:
    - Updated `llm_headline_generator.py` to fetch **3 related article titles** for context.
    - Refined prompt to ban sensationalism ("충격", "멘붕" banned).
    - Result: "한화, 156km 신인 투수 영입" (Specific, Factual).

### 2. Global Topic UI
- **Tabs**: Added "Global (All)" vs "Korea Related" tabs.
- **Sorting**: Changed default sort from "Article Count" to **"Country Count"** (Global Reach).
- **API**: Fixed `/api/global/insights` to return all recent data (Last 24h), not just the single latest record.

### 3. Local Trends API
- **Fix**: Corrected table name (`mvp2_topics`) and mapping logic in `/api/local/trends`.
- **Result**: Real local data now flows to the frontend.

### 4. Gravity Bowl Polish
- **Text Rendering**: Fixed invisible text in Matter.js bubbles.
- **Content**: Changed to display **only the Tag (Keyword)** as requested (removed headline from bubble).

---

## 🔜 Next Steps (For G)

### 1. News Constellation (Visualization)
- **Goal**: Visualize topics as a "Star Map" based on semantic similarity.
- **Plan**:
    1.  **DB**: Add `coordinate_x`, `coordinate_y` to `mvp2_topics`.
    2.  **Pipeline**: Update `llm_topic_clustering_embedding.py` to calculate 2D coordinates (t-SNE/UMAP) and save them.
    3.  **Frontend**: Implement `Constellation.tsx` to render these coordinates.

### 2. VS Card Implementation
- **Goal**: Show "Perspectives" (Pro/Con/Neutral) for a selected global topic.
- **Status**: Currently mock data. Needs `llm_stance_analyzer.py` integration.

---
*Recorded by Gemini Agent*
