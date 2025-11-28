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
  perspectives: Perspective[];
  related_articles: { title: string; url: string }[];
};

export type LocalItem = {
  topic_id: string;
  title: string;
  keyword: string;
  article_count: number;
  display_level: 1 | 2 | 3;
  media_type: "IMAGE" | "VIDEO" | "NONE";
  media_url?: string;
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

export function readGlobalList() {
  return readJson<GlobalListResponse>("outputs/mock_data/global_list.json");
}

export function readVsCard() {
  return readJson<VsCard>("outputs/mock_data/vs_card_01.json");
}

export function readLocalList() {
  return readJson<LocalListResponse>("outputs/mock_data/local_list.json");
}
