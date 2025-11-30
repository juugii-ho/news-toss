import { readGlobalList, readLocalList, readVsCard } from "./mock";
import type { GlobalListResponse, VsCard, LocalListResponse } from "./mock";

const REVALIDATE_SECONDS = 0;

async function fetchJson<T>(url: string): Promise<T> {
  const absoluteUrl =
    url.startsWith("http") || url.startsWith("https")
      ? url
      : `${process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:3000"}${url}`;
  const res = await fetch(absoluteUrl, { next: { revalidate: REVALIDATE_SECONDS } });
  if (!res.ok) throw new Error(`Failed fetch: ${url}`);
  return (await res.json()) as T;
}

export async function getGlobalList(): Promise<GlobalListResponse> {
  try {
    const data = await fetchJson<any>("/api/global/insights");
    // API spec returns array; wrap into { items }
    if (Array.isArray(data)) {
      if (data.length === 0) {
        const fallback = await readGlobalList();
        return fallback;
      }
      return { items: data };
    }
    if (data?.items) return data as GlobalListResponse;
    return { items: [] };
  } catch (err) {
    console.warn("Falling back to mock global list:", err);
    return readGlobalList();
  }
}

export async function getVsCard(id = "global_001"): Promise<VsCard> {
  try {
    return await fetchJson<VsCard>(`/api/global/insights/${id}`);
  } catch (err) {
    console.warn("Falling back to mock VS card:", err);
    return readVsCard();
  }
}

export async function getLocalList(params?: { country?: string; page?: number }): Promise<LocalListResponse> {
  const country = params?.country ?? "KR";
  const page = params?.page ?? 1;
  const query = new URLSearchParams({ country, page: String(page) }).toString();
  try {
    const data = await fetchJson<any>(`/api/local/trends?${query}`);
    // API spec returns topics[]; map to items[] shape for UI compatibility
    if (data?.topics) {
      return {
        country: data.country_code ?? country,
        page: data.page ?? page,
        items: data.topics.map((t: any) => ({
          topic_id: t.topic_id ?? t.id,
          title: t.title,
          keyword: t.keyword,
          article_count: t.article_count,
          display_level: t.display_level,
          ai_summary: t.ai_summary,
          media_type:
            (t.media_type as any) === "IMAGE"
              ? "IMAGE"
              : (t.media_type as any) === "VIDEO"
                ? "VIDEO"
                : t.media_type === "NONE"
                  ? "NONE"
                  : "NONE",
          media_url: t.media_url,
          is_global: Boolean(t.is_global)
        })),
        hasNextPage: Boolean(
          data.total_count
            ? (data.page ?? 1) * (data.limit ?? data.topics.length ?? 20) < data.total_count
            : data.hasNextPage ?? false
        )
      };
    }
    return data as LocalListResponse;
  } catch (err) {
    console.warn("Falling back to mock local list:", err);
    return readLocalList();
  }
}

export async function getLocalTopic(id: string): Promise<LocalItem> {
  try {
    return await fetchJson<LocalItem>(`/api/local/topics/${id}`);
  } catch (err) {
    console.warn("Falling back to mock local topic:", err);
    const mock = await readLocalList();
    const found = mock.items.find((i) => i.topic_id === id);
    if (found) return found;
    throw err;
  }
}
