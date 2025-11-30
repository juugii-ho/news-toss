import { notFound } from "next/navigation";
import Link from "next/link";
import { getVsCard } from "@/lib/api";
import { readVsCard } from "@/lib/mock";
import { getCategoryIcon } from "@/lib/categories";

export const revalidate = 3600;

type Props = {
  params: { id: string };
};

export default async function GlobalDetailPage({ params }: Props) {
  const id = params.id;
  const data = await getVsCard(id).catch(async () => readVsCard());

  if (!data) {
    notFound();
  }

  const keywords = Array.isArray((data as any).keywords) ? (data as any).keywords : [];
  const stances = Array.isArray((data as any).stances) ? (data as any).stances : [];
  const category = (data as any).category;
  const categoryInfo = getCategoryIcon(category);

  const stanceCounts = stances.reduce(
    (acc: any, s: any) => {
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

  console.log("Global Detail Data Debug:", JSON.stringify(data, null, 2));

  return (
    <main className="page" style={{ gap: "var(--space-5)" }}>
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
        </div>
        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 800, letterSpacing: "-0.02em", lineHeight: 1.3 }}>
          {data.title_ko}
        </h1>
        {data.intro_ko ? (
          <p style={{ margin: "var(--space-2) 0 0", color: "var(--color-neutral-700)", lineHeight: 1.5 }}>
            {data.intro_ko}
          </p>
        ) : null}
      </header>

      {(data as any).thumbnail_url && (
        <div style={{ width: "100%", aspectRatio: "16 / 9", borderRadius: "12px", overflow: "hidden", position: "relative" }}>
          <img
            src={(data as any).thumbnail_url}
            alt={(data as any).title}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
          <div style={{ position: "absolute", bottom: "16px", left: "16px", background: "rgba(0,0,0,0.6)", padding: "4px 8px", borderRadius: "6px" }}>
            <h4 style={{ margin: 0, fontSize: "12px", fontWeight: 600, color: "#ffffff", lineHeight: 1.4 }}>
              AI가 만든 이미지입니다
            </h4>
          </div>
        </div>
      )}

      {data.editor_comment && (
        <section className="rounded-card stack gap-12">
          <div className="section-header" style={{ marginBottom: "8px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "20px" }}>🧐</span>
              <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800 }}>에디터의 시선</h3>
            </div>
          </div>

          {(() => {
            const text = data.editor_comment || "";
            // Extract subtitle (bold text in quotes)
            const subtitleMatch = text.match(/\*\*"(.*?)"\*\*/);
            const subtitle = subtitleMatch ? subtitleMatch[1] : "";

            // Extract intro text (text between subtitle and "⚡ 결정적 차이")
            const introStart = subtitleMatch ? subtitleMatch.index! + subtitleMatch[0].length : 0;
            const vsStart = text.indexOf("**⚡ 결정적 차이**");
            const introText = vsStart > -1 ? text.substring(introStart, vsStart).trim() : "";

            // Extract VS lines
            const vsSection = vsStart > -1 ? text.substring(vsStart) : "";
            const vsLines = vsSection.match(/([^\n]+)\("([^"]+)"\)/g) || [];

            // Extract conclusion (text after the last VS line or after VS section header if no lines found)
            // Actually, the prompt format puts detailed explanation after the VS lines.
            // Let's find where the VS lines end.
            let conclusionText = "";
            if (vsStart > -1) {
              const lines = text.substring(vsStart).split('\n');
              let lastVsIndex = -1;
              for (let i = 0; i < lines.length; i++) {
                if (lines[i].includes('vs') || lines[i].includes('⚡') || lines[i].trim().match(/^[^\n]+\("[^"]+"\)$/)) {
                  lastVsIndex = i;
                }
              }
              if (lastVsIndex > -1 && lastVsIndex < lines.length - 1) {
                conclusionText = lines.slice(lastVsIndex + 1).join('\n').trim();
              }
            }

            const colors = [
              { bg: "#eff6ff", border: "#bfdbfe", text: "#1e40af" }, // Blue
              { bg: "#fef2f2", border: "#fecaca", text: "#991b1b" }, // Red
              { bg: "#f0fdf4", border: "#bbf7d0", text: "#166534" }, // Green
              { bg: "#fff7ed", border: "#fed7aa", text: "#9a3412" }, // Orange
            ];

            return (
              <div className="stack gap-12">
                {subtitle && (
                  <h4 style={{ margin: 0, marginBottom: "16px", fontSize: "18px", fontWeight: 800, color: "#111827", lineHeight: 1.4 }}>
                    "{subtitle}"
                  </h4>
                )}

                {introText && (
                  <p style={{ margin: 0, color: "#374151", lineHeight: 1.6, fontSize: "15px", whiteSpace: "pre-wrap" }}>
                    {introText.replace(/^\(.*\)$/gm, '').trim()} {/* Remove parenthesized explanations if any remain */}
                  </p>
                )}

                {vsLines.length > 0 && (
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px", margin: "24px 0" }}>
                    <h5 style={{ margin: "0 0 8px 0", fontSize: "14px", fontWeight: 700, color: "#4b5563" }}>⚡ 결정적 차이</h5>
                    {vsLines.map((line, idx) => {
                      const match = line.match(/([^\(]+)\("([^"]+)"\)/);
                      if (!match) return null;
                      const country = match[1].replace('vs', '').trim();
                      const quote = match[2].trim();
                      const color = colors[idx % colors.length];

                      return (
                        <div key={idx} style={{
                          background: color.bg,
                          border: `1px solid ${color.border}`,
                          borderRadius: "8px",
                          padding: "10px 12px",
                          display: "flex",
                          alignItems: "center",
                          gap: "8px"
                        }}>
                          <span style={{ fontSize: "15px", fontWeight: 600, color: "#1f2937" }}>{country}</span>
                          <span style={{ fontSize: "14px", fontWeight: 500, color: color.text }}>"{quote}"</span>
                        </div>
                      );
                    })}
                  </div>
                )}

                {conclusionText && (
                  <p style={{ margin: 0, color: "#374151", lineHeight: 1.6, fontSize: "15px", whiteSpace: "pre-wrap" }}>
                    {conclusionText.replace(/^\(.*\)$/gm, '').trim()}
                  </p>
                )}
              </div>
            );
          })()}
        </section>
      )}

      {/* {data.ai_summary && (
        <section className="rounded-card stack gap-12" style={{ background: "linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)", border: "1px solid #bae6fd", marginBottom: "var(--space-6)" }}>
          <div className="section-header" style={{ marginBottom: "8px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "20px" }}>🤖</span>
              <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800, color: "#0369a1" }}>AI가 정리했어요</h3>
            </div>
          </div>
          <p style={{ margin: 0, color: "#0c4a6e", lineHeight: 1.6, fontSize: "15px", whiteSpace: "pre-wrap" }}>
            {data.ai_summary}
          </p>
        </section>
      )} */}

      {keywords.length > 0 ? (
        <section className="rounded-card stack gap-12">
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800 }}>키워드</h3>
          <div className="chips-row">
            {keywords.map((kw: string) => (
              <span key={kw} className="chip chip-amber">
                #{kw}
              </span>
            ))}
          </div>
        </section>
      ) : null}

      {(data as any).description_ko ? (
        <section className="rounded-card stack gap-12">
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800 }}>설명</h3>
          <p style={{ margin: 0, color: "var(--color-neutral-700)", lineHeight: 1.6 }}>
            {(data as any).description_ko}
          </p>
        </section>
      ) : null}

      <section className="rounded-card stack gap-12">
        <div className="section-header">
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 800 }}>입장 차이</h3>
          <span className="chip chip-white">stance</span>
        </div>

        {stances.length === 0 ? (
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

            {/* Country Spectrum Grid */}
            {stances.length > 0 && (
              <div style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "8px",
                marginBottom: "16px"
              }}>
                {Object.entries(stances.reduce((acc: any, s: any) => {
                  const cc = s.country_code || "Unknown";
                  if (!acc[cc]) {
                    acc[cc] = {
                      code: cc,
                      flag: s.flag_emoji || "🏳️",
                      sup: 0, fac: 0, cri: 0, total: 0
                    };
                  }

                  const v = (s.stance || "").toUpperCase();
                  const raw = s.stance || "";
                  if (
                    v === "POSITIVE" || v === "SUPPORTIVE" || v === "PRO" ||
                    ["긍정", "지지", "환영", "기대", "성장", "우호"].some(k => raw.includes(k))
                  ) {
                    acc[cc].sup++;
                  } else if (
                    v === "NEGATIVE" || v === "CRITICAL" || v === "CON" ||
                    ["부정", "비판", "반대", "우려", "경고", "규탄"].some(k => raw.includes(k))
                  ) {
                    acc[cc].cri++;
                  } else {
                    acc[cc].fac++;
                  }
                  acc[cc].total++;
                  return acc;
                }, {})).map(([code, data]: any) => (
                  <div key={code} style={{
                    background: "var(--bg-secondary)",
                    borderRadius: "8px",
                    padding: "10px",
                    border: "1px solid var(--border-color)"
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px" }}>
                      <span style={{ fontSize: "16px" }}>{data.flag}</span>
                      <span style={{ fontSize: "13px", fontWeight: 700 }}>{code}</span>
                      <span style={{ fontSize: "11px", color: "var(--color-neutral-500)", marginLeft: "auto" }}>
                        {data.total}건
                      </span>
                    </div>
                    <div style={{ display: "flex", width: "100%", height: "6px", borderRadius: "3px", overflow: "hidden", background: "#e2e8f0" }}>
                      {data.total > 0 && (
                        <>
                          <div style={{ width: `${(data.sup / data.total) * 100}%`, background: "#059669" }} />
                          <div style={{ width: `${(data.fac / data.total) * 100}%`, background: "#0284c7" }} />
                          <div style={{ width: `${(data.cri / data.total) * 100}%`, background: "#e11d48" }} />
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="stack gap-12">
              {stances.map((stance: any, idx: number) => {
                let bubbleClass = "bubble-neutral";
                const sText = (stance.stance as string) || "";
                if (["우려", "반대", "비판", "경고", "부정", "규탄"].some(k => sText.includes(k)) || sText === "NEGATIVE" || sText === "CRITICAL" || sText === "CON") bubbleClass = "bubble-negative";
                else if (["환영", "기대", "지지", "긍정", "성장", "우호"].some(k => sText.includes(k)) || sText === "POSITIVE" || sText === "SUPPORTIVE" || sText === "PRO") bubbleClass = "bubble-positive";

                // Calculate country stats for this article
                const cc = stance.country_code || "Unknown";
                // We need to re-calculate or access the stats. Since we didn't save the map to a variable in the previous render, we'll re-calculate quickly or just use the logic inline if efficient.
                // Actually, let's just re-use the logic we used for the grid.
                // To avoid re-calculating inside the map, we should have stored it. 
                // But for now, let's assume we can filter the stances array for this country.
                const countryStances = stances.filter((s: any) => (s.country_code || "Unknown") === cc);
                const total = countryStances.length;
                let sup = 0, fac = 0, cri = 0;
                countryStances.forEach((s: any) => {
                  const v = (s.stance || "").toUpperCase();
                  const raw = s.stance || "";
                  if (v === "POSITIVE" || v === "SUPPORTIVE" || v === "PRO" || ["긍정", "지지", "환영", "기대", "성장", "우호"].some(k => raw.includes(k))) sup++;
                  else if (v === "NEGATIVE" || v === "CRITICAL" || v === "CON" || ["부정", "비판", "반대", "우려", "경고", "규탄"].some(k => raw.includes(k))) cri++;
                  else fac++;
                });

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
    </main>
  );
}
