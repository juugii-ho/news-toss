# 🌍 News Toss (News Spectrum)

> **"See the World, Not Just the Headline."**
>
> News Toss is an AI-powered global news aggregator that clusters diverse perspectives from 13+ countries to provide a balanced "News Spectrum".

![News Toss Hero](/assets/news_toss_hero.png)

## 🚀 About The Project

In a polarized world, News Toss helps you understand global events from multiple angles. Instead of just showing a list of articles, we analyze the **stance** (Pro/Con/Neutral) of news coverage across different countries and visualize the "spectrum" of opinions.

This project is an **Automated AI News Pipeline** that runs daily, collecting thousands of articles, translating them, and synthesizing them into digestible "Megatopics".

### ✨ Key Features

*   **🌐 Global Megatopics**: Automatically clusters related news from 13 countries (US, KR, JP, CN, UK, FR, DE, etc.) into single global narratives.
*   **⚖️ Stance Spectrum**: AI analyzes the tone of each article to show the distribution of perspectives (Supportive vs. Critical vs. Factual).
*   **🥣 Topic Bowl**: An interactive, physics-based UI (using Matter.js) to visualize local trending topics as bouncing balls.
*   **🤖 Fully Automated**: A 9-step data pipeline powered by **Gemini 2.5** and **GitHub Actions** runs every day at 15:00 KST to fetch, analyze, and publish news without human intervention.
*   **⚡ Zero-Downtime Updates**: Atomic publishing ensures users always see consistent data during updates.

---

## 🛠️ Tech Stack

### Frontend
*   **Framework**: Next.js 14 (App Router)
*   **Styling**: Vanilla CSS (Mobile-first, Apple-style aesthetics)
*   **Animation**: Framer Motion
*   **Physics Engine**: Matter.js (for Topic Bowl)

### Backend & Data
*   **Database**: Supabase (PostgreSQL + pgvector for semantic search)
*   **AI/LLM**: Google Gemini 2.5 Pro & Flash (Translation, Summarization, Stance Analysis)
*   **Language**: Python 3.10 (Data Pipeline)

### Infrastructure
*   **CI/CD**: GitHub Actions (Daily Cron Jobs)
*   **Hosting**: Vercel (Frontend)

---

## 🔄 The 9-Step AI Pipeline

Our core engine is a sophisticated Python pipeline that transforms raw RSS feeds into structured insights:

1.  **RSS Collection**: Fetches 5,000+ daily articles from major global outlets.
2.  **Translation**: Translates non-English headlines to Korean/English using Gemini.
3.  **Clustering**: Uses **HDBSCAN** and Embedding vectors to group similar articles into "Topics".
4.  **Enrichment**: AI extracts keywords, categories, and stances for each topic.
5.  **Megatopic Analysis**: Merges local topics into "Global Megatopics" across borders.
6.  **Summarization**: Generates concise 3-line summaries for each topic.
7.  **Editor Comments**: AI "Editor" provides context and insight for global issues.
8.  **Thumbnail Generation**: Selects or generates representative images.
9.  **Atomic Publishing**: Batches updates and publishes them instantly with zero downtime.

---

## 🏃‍♂️ Getting Started

### Prerequisites
*   Node.js 18+
*   Python 3.10+
*   Supabase Account
*   Google Gemini API Key

### Installation

1.  **Clone the repo**
    ```bash
    git clone https://github.com/juugii-ho/news-toss.git
    cd news-toss
    ```

2.  **Setup Environment**
    ```bash
    cp .env.example .env
    # Fill in SUPABASE_URL, SUPABASE_KEY, GOOGLE_API_KEY, etc.
    ```

3.  **Install Dependencies**
    ```bash
    # Frontend
    cd app/frontend
    npm install

    # Data Pipeline
    cd ../../
    python -m venv venv
    source venv/bin/activate
    pip install -r data/pipelines/requirements.txt
    ```

4.  **Run Locally**
    ```bash
    # Frontend
    cd app/frontend
    npm run dev
    ```

---

## 🤝 Contributing

This project is an MVP (Minimum Viable Product) developed to demonstrate the power of AI agents in news curation. Suggestions and Pull Requests are welcome!

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
