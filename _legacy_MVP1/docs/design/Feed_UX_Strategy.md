# Feed UX Strategy: "Newneek x X.com"

## Core Concept
**"Community Feed with Hidden Depth"**

We are moving away from a static "Dashboard" or "News Aggregator" look towards a dynamic, engaging **Social Feed** metaphor.
- **The Hook**: Looks like a fun, easy-to-read community feed (Newneek style).
- **The Depth**: One tap reveals the "Total Perspective" (Ground News style data), making standard news feel flat by comparison.
- **The Interaction**: Fast, fluid, "X.com" style (scroll -> tap -> expand -> swipe away).

## Design References

### 1. Newneek (The "Grammar")
- **Tone**: Friendly, conversational, witty.
- **Visuals**:
    - Rounded corners (lg/xl).
    - Bold, readable typography (Pretendard/Suit).
    - Emojis as icons/badges.
    - "Card" metaphor: Distinct blocks of content on a light gray background.
- **Layout**:
    - Mobile: Full-width cards.
    - Desktop: Masonry or Grid.

### 2. X.com (The "Usability")
- **Flow**: Infinite vertical scroll.
- **Density**: High but scannable.
- **Interaction**:
    - "Tweet" -> "Thread" expansion.
    - Immediate gratification.
- **Media**: Images/Video take center stage.

### 3. Ground News (The "Seasoning")
- **Data**: Bias distribution, "Blindspot", "Divergence".
- **Integration**: Instead of overwhelming charts, use subtle *micro-indicators* on the feed card.
    - *Example*: A small colored bar at the bottom of the card.
    - *Example*: A "🔥 High Conflict" badge.

## UI Components

### 1. The Feed (`<NewsFeed />`)
- **Layout**: Single column (max-width ~600px on desktop, 100% on mobile) centered.
- **Background**: Light gray / Off-white (Newneek style).
- **Header**: Minimal, sticky. "For You", "Trending".

### 2. The Card (`<FeedCard />`)
- **Structure**:
    - **Header**: Topic/Category (e.g., "🇺🇸 US Politics", "🌍 Climate").
    - **Media**: Large, high-quality image (16:9 or 2:1).
    - **Content**:
        - **Title**: Bold, 2-3 lines max.
        - **Summary**: 1-2 lines (optional, maybe just title for density).
    - **"The Seasoning" (Footer)**:
        - **Divergence Meter**: A small pill showing "Opinion Gap: High".
        - **Source Count**: "24 sources from 5 countries".
        - **Reaction**: "Analysis Ready" (Call to Action).

### 3. The Detail View (`<TopicDetail />`)
- **Transition**: Slide-over or Modal expansion (X.com style) or fast page nav.
- **Content**:
    - The full "Megatopic" view we built (Summary, Country Breakdown, Article List).
    - **Goal**: "Wow, I didn't realize there was this much nuance."

## "Wow" Factors (Aesthetics)
- **Micro-interactions**: Cards lift slightly on hover/touch.
- **Skeleton Loading**: Shimmer effects that match the card layout.
- **Typography**: Switch to a premium sans-serif (Inter or Pretendard).
- **Dark Mode**: Deep blue/gray (not pitch black) for a premium feel.

## Implementation Steps
1.  **Refactor `page.tsx`**: Replace the grid with a centered Feed layout.
2.  **Create `FeedCard`**: New component with the "Seasoning" logic.
3.  **Update Navigation**: Ensure smooth transition to details.
