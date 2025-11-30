import { notFound } from "next/navigation";
import Link from "next/link";
import { getLocalTopic } from "@/lib/api";
import { readLocalList } from "@/lib/mock";
import { getCategoryIcon } from "@/lib/categories";

export const revalidate = 600;

type LocalStance = {
  country_code?: string;
  country_name?: string;
  flag_emoji?: string;
  stance?: "POSITIVE" | "NEGATIVE" | "NEUTRAL";
  one_liner_ko?: string;
  source_link?: string;
  source_name?: string;
};

type LocalArticle = {
  id?: string;
  title?: string;
  title_ko?: string;
  title_original?: string;
  source?: string;
  published_at?: string;
  url?: string;
  global_topic_id?: string | null;
  country_code?: string | null;
};

type LocalDetail = {
  topic_id: string;
  title: string;
  keyword: string;
  article_count: number;
  display_level: 1 | 2 | 3;
  media_type?: string;
  media_url?: string | null;
  stances?: LocalStance[];
  keywords?: string[];
  articles?: LocalArticle[];
  global_topic_id?: string | null;
  category?: string | null;
  country_code?: string;
  ai_summary?: string | null;
};

type Props = { params: { id: string } };

export default async function LocalDetailPage({ params }: Props) {
  const id = params.id;

  let topic: LocalDetail | null = null;
  try {
    topic = (await getLocalTopic(id)) as LocalDetail;
  } catch {
    const mock = await readLocalList();
    topic = (mock.items as any as LocalDetail[]).find((i) => i.topic_id === id) ?? null;
  }

  if (!topic) {
    notFound();
  }

  const stancesArray = Array.isArray(topic.stances) ? topic.stances : [];
  const keywords = (topic.keywords?.length ? topic.keywords : [topic.keyword]).filter(Boolean);
  const articles = topic.articles ?? [];
  const relatedGlobalId =
    topic.global_topic_id ||
    articles.find((a) => a.global_topic_id)?.global_topic_id ||
    undefined;
  const category = topic.category;
  const categoryInfo = getCategoryIcon(category);

  const stanceCounts = stancesArray.reduce(
    (acc, s) => {
      const v = (s.stance || "").toUpperCase();
      const raw = s.stance || "";

      if (
        v === "POSITIVE" ||
        v === "SUPPORTIVE" ||
        v === "PRO" ||
        ["긍정", "지지", "환영", "기대", "성장", "우호"].some(k => raw.includes(k))
      ) {
        acc.sup++;
      } else if (
        v === "NEGATIVE" ||
        v === "CRITICAL" ||
        v === "CON" ||
        ["부정", "비판", "반대", "우려", "경고", "규탄"].some(k => raw.includes(k))
      ) {
        acc.cri++;
      } else {
        acc.fac++;
      }
      return acc;
    },
    { sup: 0, fac: 0, cri: 0 }
  );
  const totalStance = stanceCounts.sup + stanceCounts.fac + stanceCounts.cri;

  return (
    <main className="page" style={{ gap: "var(--space-4)" }}>
      <header className="section">
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "var(--space-2)",
            marginBottom: "var(--space-3)",
            width: "100%"
          }}
        >
          {category ? (
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "var(--space-2)",
              }}
            >
              {categoryInfo.image ? (
                <img
                  src={categoryInfo.image}
                  alt={category}
                  width={32}
                  height={32}
                  style={{ objectFit: "contain" }}
                />
              ) : (
                <span style={{ fontSize: 24 }}>{categoryInfo.icon}</span>
              )}
              <span
                style={{
                  fontSize: 14,
                  fontWeight: 700,
                  color: categoryInfo.color,
                  background: categoryInfo.bg,
                  padding: "4px 8px",
                  borderRadius: "var(--radius-sm)"
                }}
              >
                {category}
              </span>
            </div>
          ) : <div />}

          {topic.country_code && (
            <span style={{ fontSize: 32 }}>
              {topic.country_code === "KR" ? "🇰🇷" :
                topic.country_code === "US" ? "🇺🇸" :
                  topic.country_code === "JP" ? "🇯🇵" :
                    topic.country_code === "CN" ? "🇨🇳" :
                      topic.country_code === "GB" ? "🇬🇧" :
                        topic.country_code === "FR" ? "🇫🇷" :
                          topic.country_code === "DE" ? "🇩🇪" :
                            topic.country_code === "IT" ? "🇮🇹" :
                              topic.country_code === "CA" ? "🇨🇦" :
                                topic.country_code === "AU" ? "🇦🇺" :
                                  topic.country_code === "NL" ? "🇳🇱" :
                                    topic.country_code === "BE" ? "🇧🇪" :
                                      topic.country_code === "RU" ? "🇷🇺" : "🌐"}
            </span>
          )}
        </div>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em", lineHeight: 1.3 }}>
          {topic.title}
        </h1>
      </header>

      {topic.media_url && (
        <div style={{ width: "100%", aspectRatio: "16 / 9", borderRadius: "12px", overflow: "hidden", position: "relative" }}>
          <img
            src={topic.media_url}
            alt={topic.title}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
          <div style={{ position: "absolute", bottom: "16px", left: "16px", background: "rgba(0,0,0,0.6)", padding: "0px", borderRadius: "6px" }}>
            <h4 style={{ margin: 0, fontSize: "12px", fontWeight: 600, color: "#ffffff", lineHeight: 1.4 }}>
              AI가 만든 이미지입니다
            </h4>
          </div>
        </div>
      )}

      <section className="rounded-card stack">
        <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800 }}>키워드</h3>
        <div className="chips-row">
          {keywords.length === 0 ? <span className="metric-label">키워드 없음</span> : null}
          {keywords.map((kw) => (
            <span key={kw} className="chip chip-amber">
              #{kw}
            </span>
          ))}
        </div>
      </section>

      {topic.ai_summary && (
        <section className="rounded-card stack gap-12" style={{ background: "linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)", border: "1px solid #bae6fd" }}>
          <div className="section-header" style={{ marginBottom: "8px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "20px" }}>🤖</span>
              <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: "#0369a1" }}>AI가 정리했어요</h3>
            </div>
          </div>
          <p style={{ margin: 0, color: "#0c4a6e", lineHeight: 1.6, fontSize: "15px", whiteSpace: "pre-wrap" }}>
            {topic.ai_summary}
          </p>
        </section>
      )}

      {relatedGlobalId && (
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "-8px" }}>
          <Link
            href={`/global/${relatedGlobalId}`}
            className="hero-link"
            style={{ textDecoration: "none", fontSize: "12px", color: "var(--color-neutral-500)" }}
          >
            연관 글로벌 상세 보기 ↗
          </Link>
        </div>
      )}

      <section className="rounded-card stack gap-12">
        <div className="section-header">
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800 }}>입장 차이</h3>
          <span className="chip chip-white">stance</span>
        </div>

        {stancesArray.length === 0 ? (
          <p className="status-text">아직 분석된 입장 차이가 없습니다.</p>
        ) : (
          <>
            {totalStance > 0 && (
              <div className="stack gap-8">
                {/* Spectrum Bar */}
                <div style={{ display: "flex", width: "100%", height: "12px", borderRadius: "6px", overflow: "hidden", background: "#f1f5f9" }}>
                  <div style={{ width: `${(stanceCounts.sup / totalStance) * 100}%`, background: "#059669" }} />
                  <div style={{ width: `${(stanceCounts.fac / totalStance) * 100}%`, background: "#0284c7" }} />
                  <div style={{ width: `${(stanceCounts.cri / totalStance) * 100}%`, background: "#e11d48" }} />
                </div>

                <div className="chips-row" style={{ justifyContent: "space-between" }}>
                  <span style={{ fontSize: 12, color: "#059669", fontWeight: 700 }}>옹호 {Math.round((stanceCounts.sup / totalStance) * 100)}%</span>
                  <span style={{ fontSize: 12, color: "#0284c7", fontWeight: 700 }}>중립 {Math.round((stanceCounts.fac / totalStance) * 100)}%</span>
                  <span style={{ fontSize: 12, color: "#e11d48", fontWeight: 700 }}>비판 {Math.round((stanceCounts.cri / totalStance) * 100)}%</span>
                </div>
              </div>
            )}

            <div className="stack gap-12">
              {stancesArray.map((stance, idx) => {
                let bubbleClass = "bubble-neutral";
                const sText = (stance.stance as string) || "";
                if (["우려", "반대", "비판", "경고", "부정", "규탄"].some(k => sText.includes(k)) || sText === "NEGATIVE" || sText === "CRITICAL" || sText === "CON") bubbleClass = "bubble-negative";
                else if (["환영", "기대", "지지", "긍정", "성장", "우호"].some(k => sText.includes(k)) || sText === "POSITIVE" || sText === "SUPPORTIVE" || sText === "PRO") bubbleClass = "bubble-positive";

                return (
                  <Link
                    key={stance.country_code || idx}
                    href={stance.source_link || "#"}
                    target="_blank"
                    className={`bubble ${bubbleClass}`}
                    style={{
                      background: "var(--bg-secondary)",
                      border: "1px solid var(--border-color)",
                      color: "var(--text-primary)",
                      textDecoration: "none",
                      display: "flex",
                      flexDirection: "row",
                      alignItems: "flex-start",
                      gap: "var(--space-3)"
                    }}
                  >
                    {stance.flag_emoji && (
                      <span style={{ fontSize: "1.2em", lineHeight: 1, marginTop: "2px" }}>
                        {stance.flag_emoji}
                      </span>
                    )}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "4px" }}>
                        <span style={{ fontWeight: 700, fontSize: "13px" }}>
                          {stance.source_name || stance.country_name || stance.country_code || "언론사"}
                        </span>
                        {stance.stance && <span className="bubble-stance-badge">{stance.stance}</span>}
                      </div>
                      <p className="bubble-line" style={{ margin: 0 }}>
                        {stance.one_liner_ko || "제목 없음"}
                      </p>
                    </div>
                  </Link>
                );
              })}
            </div>
          </>
        )}
      </section>


    </main >
  );
}
