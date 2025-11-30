
"use client";

import React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { LocalGravityBowl } from "./LocalGravityBowl";
import { LocalMosaic } from "./LocalMosaic";
import { LocalOverview } from "./LocalOverview";
import type { LocalListResponse } from "@/lib/mock";

type Props = {
  country: string;
  data: LocalListResponse;
};

const countryOptions = [
  { code: "ALL", label: "전체 보기" },
  { code: "AU", label: "🇦🇺 호주" },
  { code: "BE", label: "🇧🇪 벨기에" },
  { code: "CA", label: "🇨🇦 캐나다" },
  { code: "CN", label: "🇨🇳 중국" },
  { code: "DE", label: "🇩🇪 독일" },
  { code: "FR", label: "🇫🇷 프랑스" },
  { code: "GB", label: "🇬🇧 영국" },
  { code: "IT", label: "🇮🇹 이탈리아" },
  { code: "JP", label: "🇯🇵 일본" },
  { code: "KR", label: "🇰🇷 대한민국" },
  { code: "NL", label: "🇳🇱 네덜란드" },
  { code: "RU", label: "🇷🇺 러시아" },
  { code: "US", label: "🇺🇸 미국" }
].sort((a, b) => {
  if (a.code === "ALL") return -1;
  if (b.code === "ALL") return 1;
  // Remove emoji and space to sort by Korean name
  const nameA = a.label.split(" ")[1] || a.label;
  const nameB = b.label.split(" ")[1] || b.label;
  return nameA.localeCompare(nameB, "ko");
});

export function LocalPageClient({ country, data }: Props) {
  const router = useRouter();
  const params = useSearchParams();
  const [showBottle, setShowBottle] = React.useState(false);
  const [countryState, setCountryState] = React.useState(country);

  const [viewMode, setViewMode] = React.useState<"grid" | "list">("list");

  React.useEffect(() => {
    setCountryState(country);
  }, [country]);

  const headerLabel = countryOptions.find((c) => c.code === countryState)?.label || countryState;

  return (
    <>
      <section className="section">
        {countryState !== "ALL" && (
          <div className="section-header" style={{ alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <h2 style={{ margin: 0, fontSize: 24, lineHeight: 1 }}>{headerLabel} 뉴스 순위</h2>
            </div>
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                onClick={() => setViewMode(prev => prev === "list" ? "grid" : "list")}
                style={{
                  border: "1px solid #e2e8f0",
                  background: "#fff",
                  borderRadius: 10,
                  width: "36px",
                  height: "36px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: 0
                }}
              >
                {viewMode === "list" ? (
                  // Show Grid Icon to switch to Grid
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="7" height="7" />
                    <rect x="14" y="3" width="7" height="7" />
                    <rect x="14" y="14" width="7" height="7" />
                    <rect x="3" y="14" width="7" height="7" />
                  </svg>
                ) : (
                  // Show List Icon to switch to List
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="8" y1="6" x2="21" y2="6" />
                    <line x1="8" y1="12" x2="21" y2="12" />
                    <line x1="8" y1="18" x2="21" y2="18" />
                    <line x1="3" y1="6" x2="3.01" y2="6" />
                    <line x1="3" y1="12" x2="3.01" y2="12" />
                    <line x1="3" y1="18" x2="3.01" y2="18" />
                  </svg>
                )}
              </button>
              <button
                onClick={() => setShowBottle(true)}
                style={{
                  border: "1px solid #e2e8f0",
                  background: "#fff",
                  borderRadius: 10,
                  width: "36px",
                  height: "36px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: 0
                }}
              >
                <img src="/assets/Topic Bowl.png" alt="Topic Bowl" width={20} height={20} style={{ objectFit: "contain" }} />
              </button>
            </div>
          </div>
        )}

        {countryState === "ALL" ? (
          <LocalOverview countryOptions={countryOptions.filter(o => o.code !== "ALL")} viewMode={viewMode} />
        ) : (
          <LocalMosaic
            key={countryState}
            initial={countryState === country ? data : undefined}
            country={countryState}
            viewMode={viewMode}
          />
        )}
      </section>

      {showBottle ? (
        <div
          onClick={() => setShowBottle(false)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(15,23,42,0.28)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 16,
            zIndex: 50
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "90vw",
              maxWidth: 420,
              height: "auto",
              maxHeight: "650px",
              background: "#fff",
              borderRadius: 18,
              padding: "16px",
              boxShadow: "0 18px 40px rgba(15,23,42,0.18)",
              position: "relative",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column"
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <img src="/assets/Topic Bowl.png" alt="" width={24} height={24} style={{ objectFit: "contain" }} />
                <h2 style={{ fontSize: 18, fontWeight: 700, letterSpacing: "-0.03em", margin: 0 }}>
                  {new Date().getMonth() + 1}월 {new Date().getDate()}일 {headerLabel.replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, "").trim()} Topic Bowl
                </h2>
              </div>
              <button
                onClick={() => setShowBottle(false)}
                style={{
                  border: "1px solid #e2e8f0",
                  background: "#fff",
                  borderRadius: 10,
                  padding: "6px 12px",
                  fontWeight: 700,
                  cursor: "pointer",
                  fontSize: "14px"
                }}
              >
                닫기
              </button>
            </div>
            <div style={{ flex: 1, position: "relative" }}>
              <LocalGravityBowl items={data.items} showStatus={false} showHeader={false} />
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}

