# Feed Detail View Design Guide

## Overview
The "Detail View" is the expanded state of a `FeedCard`. It appears when a user clicks "한 번에 보기" (Expand) or taps the card body.
It must feel like a natural extension of the card, not a completely different page.

## Core Principles
1.  **Seamless Expansion**: The card grows vertically to reveal content. No page reload.
2.  **Visual Hierarchy**:
    - **Level 1 (Feed)**: Title, Thumbnail, Divergence Badge.
    - **Level 2 (Expanded)**: Summary ("무슨 일이에요?"), Global Stance ("전체 반응").
    - **Level 3 (Deep Dive)**: Country Breakdown ("국가별 시선"), Articles ("주요 기사").
3.  **"Seasoning" First**: Show the analysis (Stance/Divergence) *before* the raw list of articles.

## Layout Specifications

### 1. Summary Section ("💡 무슨 일이에요?")
- **Background**: White (or dark gray in dark mode).
- **Typography**:
    - Header: `text-sm font-bold mb-3` (Icon + Text).
    - Body: `text-sm leading-relaxed text-zinc-700`.
- **Constraint**: Max 3-4 lines. If longer, truncate with "Read more".

### 2. Global Stance Section ("🌍 전체 반응")
- **Component**: `SpectrumBar` (Large version).
- **Placement**: Immediately after Summary.
- **Caption**: "총 X개의 기사를 분석했어요." (Subtle, gray text).

### 3. Country Breakdown ("🗺️ 국가별 시선")
- **Layout**: Vertical stack of "Mini Cards".
- **Mini Card**:
    - **Left**: Flag + Country Name.
    - **Right**: Mini `SpectrumBar` (simplified, no labels).
    - **Bottom**: "Avg Score" (optional, maybe just color code).
- **Sorting**: Sort by "Most Divergent" or "Most Articles".

### 4. Article List ("📰 주요 기사")
- **Layout**: Compact list.
- **Item**:
    - Title (1 line, truncated).
    - Source + Time (Gray, small).
    - External Link Icon.
- **Interaction**: Opens in new tab.

## Interaction Design
- **Toggle Button**:
    - **Position**: Bottom of the card (Sticky-ish or just at the end).
    - **State**:
        - Collapsed: "한 번에 보기 ↓" (Blue text).
        - Expanded: "접기 ↑" (Gray text).
- **Loading State**:
    - Show a skeleton of the expanded area while fetching `/api/topics/[id]`.
    - Animation: `animate-pulse`.

## Mobile Considerations
- **Padding**: Keep `p-5` consistent with the card body.
- **Touch Targets**: All links/buttons must be >44px height.
- **Typography**: Base font size 15px (not 14px) for better readability on small screens.
