import path from "node:path";
import { promises as fs } from "node:fs";

export type GlobalItem = {
  id: string;
  rank: number;
  is_pinned: boolean;
  title_ko: string;
  category?: string;
  hero_image_url?: string;
  hot_topic_badge?: string | null;
  keywords?: string[];
  thumbnail_url?: string;
  countries?: string[];
  country_count?: number;
  article_count?: number;
  summary?: string;
  x?: number;
  y?: number;
  localTopics?: LocalTopic[];
  stances?: any;
};

export type LocalTopic = {
  id: string;
  topic_name: string;
  country_code: string;
  x?: number;
  y?: number;
};

export type GlobalListResponse = {
  items: GlobalItem[];
};

export type Perspective = {
  country_code: string;
  country_name: string;
  flag_emoji: string;
  stance: "POSITIVE" | "NEGATIVE" | "NEUTRAL";
  one_liner_ko: string;
  source_link: string;
};

export type VsCard = {
  id: string;
  title_ko: string;
  intro_ko: string;
  description_ko?: string;
  perspectives: Perspective[];
  related_articles: { title: string; url: string; source?: string; published_at?: string }[];
  ai_summary?: string;
  editor_comment?: string;
};

export type LocalItem = {
  topic_id: string;
  title: string;
  keyword: string;
  article_count: number;
  display_level: 1 | 2 | 3;
  media_type: "IMAGE" | "VIDEO" | "NONE";
  media_url?: string;
  keywords?: string[];
  stances?: any;
  summary?: string;
  category?: string;
  published_at?: string;
};

export type LocalListResponse = {
  country: string;
  page: number;
  items: LocalItem[];
  hasNextPage: boolean;
};

async function readJson<T>(relativePath: string): Promise<T> {
  const cwd = process.cwd();
  const repoRoot = cwd.includes("/app/frontend")
    ? path.resolve(cwd, "..", "..")
    : cwd.includes("/app")
      ? path.resolve(cwd, "..")
      : cwd;
  const filePath = path.join(repoRoot, relativePath);
  const file = await fs.readFile(filePath, "utf-8");
  return JSON.parse(file) as T;
}

export async function readGlobalList() {
  const data = await readJson<GlobalListResponse>("outputs/mock_data/global_list.json");
  // Inject random coords for visualization testing
  data.items = data.items.map((item, i) => ({
    ...item,
    x: (Math.random() - 0.5) * 160, // [-80, 80]
    y: (Math.random() - 0.5) * 160,
    localTopics: Array(3).fill(null).map((_, j) => ({
      id: `mock-local-${i}-${j}`,
      topic_name: `Mock Local Topic ${j + 1}`,
      country_code: ["KR", "US", "JP"][j % 3],
      x: (Math.random() - 0.5) * 160,
      y: (Math.random() - 0.5) * 160
    }))
  }));
  return data;
}

export function readVsCard() {
  return readJson<VsCard>("outputs/mock_data/vs_card_01.json");
}

export function readLocalList() {
  return readJson<LocalListResponse>("outputs/mock_data/local_list.json");
}
