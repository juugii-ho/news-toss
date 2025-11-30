"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import type { GlobalItem } from "../lib/mock";
import Link from "next/link";
import React from "react";
import { useSearchParams } from "next/navigation";

type Props = {
  items: GlobalItem[];
};

export function GlobalSection({ items }: Props) {
  const params = useSearchParams();
  const includeKr = params.get("kr") !== "exclude";

  const filteredItems = React.useMemo(() => {
    const hasKr = (item: GlobalItem) => (item.countries || []).includes("KR");
    if (includeKr) {
      // KR 반영 모드: KR을 포함한 토픽만 노출
      return items.filter(hasKr);
    }
    // KR 무시 모드: 정렬 그대로 전체 노출
    return items;
  }, [items, includeKr]);

  // Re-rank for display
  const displayItems = filteredItems.map((item, idx) => ({
    ...item,
    displayRank: idx + 1,
  }));



  const renderStanceBar = (stances: any) => {
    if (!stances) return null;

    let sup = 0, fac = 0, cri = 0;

    if (Array.isArray(stances)) {
      stances.forEach((s: any) => {
        const v = (s.stance || "").toUpperCase();
        const raw = s.stance || "";
        if (v === "POSITIVE" || v === "SUPPORTIVE" || v === "PRO" || ["긍정", "지지", "환영", "기대", "성장", "우호"].some(k => raw.includes(k))) sup++;
        else if (v === "NEGATIVE" || v === "CRITICAL" || v === "CON" || ["부정", "비판", "반대", "우려", "경고", "규탄"].some(k => raw.includes(k))) cri++;
        else fac++;
      });
    } else if (typeof stances === "object") {
      sup = (stances.supportive || []).length;
      cri = (stances.critical || []).length;
      fac = (stances.factual || []).length;
    }

    const total = sup + fac + cri;
    if (total === 0) return null;

    return (
      <div style={{ display: "flex", width: "100%", height: "4px", borderRadius: "2px", overflow: "hidden", background: "rgba(0,0,0,0.1)", marginTop: "6px" }}>
        <div style={{ width: `${(sup / total) * 100}%`, background: "#059669" }} />
        <div style={{ width: `${(fac / total) * 100}%`, background: "#0284c7" }} />
        <div style={{ width: `${(cri / total) * 100}%`, background: "#e11d48" }} />
      </div>
    );
  };

  return (
    <section className="section">
      <div className="section-header">
        <h2 style={{ margin: 0 }}>Global Insight</h2>
      </div>

      <div className="stack gap-12">
        {displayItems.map((item, idx) => (
          <Link key={item.id} href={`/global/${item.id}`} style={{ textDecoration: "none" }}>
            <motion.article
              className="hero-card"
              initial={{ y: 24, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.4, delay: idx * 0.08 }}
            >
              <div className="hero-image">
                {item.hero_image_url || item.thumbnail_url ? (
                  <img
                    src={item.hero_image_url || item.thumbnail_url || ""}
                    alt={item.title_ko}
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                ) : (
                  <div className="hero-placeholder" />
                )}
                <div className="hero-gradient" />
              </div>
              <div className="hero-badges">
                <span
                  className="chip"
                  style={{
                    background: "#f1f5f9", // neutral-100
                    color: "#475569", // neutral-600
                    border: "1px solid #e2e8f0", // neutral-200
                    boxShadow: "none"
                  }}
                >
                  메가토픽 #{item.displayRank}
                </span>
                <span className="chip chip-amber">{item.country_count ?? 0}개국</span>
                {item.is_pinned ? <span className="chip chip-white">PINNED</span> : null}
              </div>
              <div className="hero-text">
                {item.category ? (
                  <p className="hero-category">{item.category}</p>
                ) : null}
                <h3 style={{ fontSize: "30px" }}>{item.title_ko}</h3>
                {renderStanceBar(item.stances)}
              </div>
            </motion.article>
          </Link>
        ))}
      </div>
    </section>
  );
}
