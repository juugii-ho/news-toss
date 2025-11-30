"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import type { LocalItem } from "../lib/mock";

type Props = {
    item: LocalItem; // Added back as it's essential for the component
    viewMode?: "grid" | "list";
    sentinelRef?: React.RefObject<HTMLDivElement>;
};

function formatRelativeTime(dateStr?: string) {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = diffMs / (1000 * 60 * 60);
    const diffDays = diffHours / 24;
    const diffWeeks = diffDays / 7;
    const diffMonths = diffDays / 30;

    if (diffHours < 24) return `${Math.floor(diffHours)}시간 전`;
    if (diffDays < 10) return `${Math.floor(diffDays)}일 전`;
    if (diffWeeks < 5) return `${Math.floor(diffWeeks)}주 전`;
    if (diffMonths < 10) return `${Math.floor(diffMonths)}달 전`;

    return `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`;
}

function getCategoryIcon(category?: string) {
    if (!category) return "/assets/news_toss_3d_icon.png";

    const lower = category.toLowerCase();
    if (lower.includes("politic") || lower.includes("정치")) return "/assets/categories/politics.png";
    if (lower.includes("econom") || lower.includes("경제")) return "/assets/categories/economy.png";
    if (lower.includes("societ") || lower.includes("사회")) return "/assets/categories/society.png";
    if (lower.includes("tech") || lower.includes("it") || lower.includes("기술")) return "/assets/categories/tech.png";
    if (lower.includes("world") || lower.includes("국제") || lower.includes("세계")) return "/assets/categories/world.png";
    if (lower.includes("sport") || lower.includes("스포츠")) return "/assets/categories/sports.png";
    if (lower.includes("entertain") || lower.includes("연예") || lower.includes("문화")) return "/assets/categories/entertainment.png";
    if (lower.includes("cultur") || lower.includes("문화")) return "/assets/categories/culture.png";

    return "/assets/news_toss_3d_icon.png";
}

export function LocalTile({ item, sentinelRef, viewMode = "list" }: Props) {
    const sizeClass =
        item.display_level === 1
            ? "tile tile-lg"
            : item.display_level === 2
                ? "tile tile-md"
                : "tile tile-sm";

    const categoryIcon = getCategoryIcon(item.category);

    if (viewMode === "grid") {
        return (
            <Link href={`/local/${item.topic_id}`} className={sizeClass}>
                {sentinelRef ? (
                    <div
                        ref={sentinelRef}
                        style={{ position: "absolute", inset: 0, pointerEvents: "none", opacity: 0 }}
                    />
                ) : null}
                <div className="tile-media">
                    {item.media_type === "IMAGE" && item.media_url ? (
                        <img
                            src={item.media_url}
                            alt={item.title}
                            style={{ width: "100%", height: "100%", objectFit: "cover" }}
                        />
                    ) : item.media_type === "VIDEO" && item.media_url ? (
                        <video
                            className="video-cover"
                            src={item.media_url}
                            autoPlay
                            muted
                            loop
                            playsInline
                            preload="metadata"
                        />
                    ) : (
                        <div className="tile-placeholder" />
                    )}
                </div>
                <div className="tile-text">
                    <div className="tile-keywords" style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginBottom: "4px" }}>
                        {(item.keywords && item.keywords.length > 0 ? item.keywords : [item.keyword]).slice(0, 3).map((kw, i) => (
                            <span key={i} className="tile-keyword" style={{ marginRight: 0, fontSize: "14px" }}>#{kw}</span>
                        ))}
                    </div>
                    <p className="tile-title" style={{ fontSize: "17px" }}>{item.title}</p>

                    {item.summary && (
                        <p style={{ fontSize: "14px", color: "#666", margin: "4px 0 8px 0", lineHeight: "1.4", display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                            {item.summary}
                        </p>
                    )}
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "4px" }}>
                        <p className="tile-count" style={{ margin: 0 }}>{item.article_count.toLocaleString()} articles</p>
                        {(() => {
                            const stances = item.stances;
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
                                <div style={{ flex: 1, height: "4px", borderRadius: "2px", overflow: "hidden", background: "rgba(0,0,0,0.1)", display: "flex" }}>
                                    <div style={{ width: `${(sup / total) * 100}%`, background: "#059669" }} />
                                    <div style={{ width: `${(fac / total) * 100}%`, background: "#0284c7" }} />
                                    <div style={{ width: `${(cri / total) * 100}%`, background: "#e11d48" }} />
                                </div>
                            );
                        })()}
                    </div>
                </div>
            </Link>
        );
    }

    // List Mode (YouTube Style)
    return (
        <Link href={`/local/${item.topic_id}`} style={{ display: "flex", flexDirection: "column", gap: "12px", textDecoration: "none", cursor: "pointer", paddingBottom: "24px" }}>
            {sentinelRef ? (
                <div
                    ref={sentinelRef}
                    style={{ position: "absolute", inset: 0, pointerEvents: "none", opacity: 0 }}
                />
            ) : null}

            {/* Thumbnail Section - Full Bleed */}
            <div style={{ position: "relative", width: "calc(100% + 40px)", marginLeft: "-20px", marginRight: "-20px", aspectRatio: "16/9", overflow: "hidden", background: "#f1f5f9" }}>
                {item.media_type === "IMAGE" && item.media_url ? (
                    <img
                        src={item.media_url}
                        alt={item.title}
                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                ) : item.media_type === "VIDEO" && item.media_url ? (
                    <video
                        className="video-cover"
                        src={item.media_url}
                        autoPlay
                        muted
                        loop
                        playsInline
                        preload="metadata"
                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                ) : (
                    <div className="tile-placeholder" style={{ width: "100%", height: "100%", background: "linear-gradient(135deg, #e0e7ff, #f1f5f9)" }} />
                )}
            </div>

            {/* Info Row */}
            <div style={{ display: "flex", gap: "12px", alignItems: "flex-start", padding: "0 4px" }}>
                {/* Asset / Icon (Left) - No circle, just asset */}
                <div style={{ flexShrink: 0, width: "40px", height: "40px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <img
                        src={categoryIcon}
                        alt={item.category || "News"}
                        style={{ width: "100%", height: "100%", objectFit: "contain" }}
                        onError={(e) => {
                            // Fallback if specific category icon fails
                            const target = e.target as HTMLImageElement;
                            if (!target.src.includes("news_toss_3d_icon.png")) {
                                target.src = "/assets/news_toss_3d_icon.png";
                            } else {
                                target.style.display = 'none';
                            }
                        }}
                    />
                </div>

                {/* Text Content (Right) */}
                <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "4px" }}>
                    <p style={{
                        margin: 0,
                        fontSize: "16px",
                        fontWeight: 600,
                        color: "#0f172a",
                        lineHeight: "1.3",
                        wordBreak: "keep-all",
                        overflowWrap: "break-word",
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden"
                    }}>
                        {item.title}
                    </p>

                    <div style={{ display: "flex", alignItems: "center", gap: "4px", flexWrap: "wrap" }}>
                        <span style={{ fontSize: "12px", color: "#64748b" }}>
                            {formatRelativeTime(item.created_at)}
                        </span>
                        <span style={{ fontSize: "12px", color: "#64748b" }}>•</span>
                        <div style={{ display: "flex", gap: "4px" }}>
                            {(item.keywords && item.keywords.length > 0 ? item.keywords : [item.keyword]).slice(0, 3).map((kw, i) => (
                                <span key={i} style={{ fontSize: "12px", color: "#64748b" }}>#{kw}</span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </Link>
    );
}
