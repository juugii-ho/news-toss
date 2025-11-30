"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { LocalTile } from "./LocalTile";
import type { LocalListResponse } from "../lib/mock";
import Link from "next/link";

type Props = {
    countryOptions: { code: string; label: string }[];
    viewMode?: "grid" | "list";
};

const PRIORITY_COUNTRIES = ["KR", "US", "CN", "JP"];

export function LocalOverview({ countryOptions, viewMode = "list" }: Props) {
    const priorityOptions = PRIORITY_COUNTRIES.map(code =>
        countryOptions.find(opt => opt.code === code) || { code, label: code }
    );

    const otherOptions = countryOptions.filter(opt => !PRIORITY_COUNTRIES.includes(opt.code));

    return (
        <div className="stack gap-24">
            {priorityOptions.map(opt => (
                <CountrySection key={opt.code} code={opt.code} label={opt.label} viewMode={viewMode} />
            ))}

            <div className="stack gap-12">
                <div style={{ marginTop: 24 }} />
                {otherOptions.map(opt => (
                    <CountrySection key={opt.code} code={opt.code} label={opt.label} viewMode={viewMode} />
                ))}
            </div>
        </div>
    );
}

function CountrySection({ code, label, viewMode }: { code: string; label: string; viewMode: "grid" | "list" }) {
    const { data } = useQuery<LocalListResponse>({
        queryKey: ["local-trends", code, "overview"],
        queryFn: async () => {
            // Fetch top 20 items to determine top 20%
            const res = await fetch(`/api/local/trends?page=1&country=${code}&limit=20`);
            if (!res.ok) throw new Error("failed");
            return (await res.json()) as LocalListResponse;
        }
    });

    // Filter for display_level === 1 (Top 20%)
    // If no items have display_level === 1 (e.g. small dataset), fallback to top 4
    let topItems = data?.items.filter(item => item.display_level === 1) || [];
    if (topItems.length === 0 && data?.items) {
        topItems = data.items.slice(0, 4);
    }

    return (
        <section className="section" style={{ marginBottom: "48px" }}>
            <div className="section-header">
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%", marginBottom: "4px" }}>
                    <h2 style={{ margin: 0, fontSize: 24, lineHeight: 1 }}>{label}</h2>
                    <Link
                        href={`/local?country=${code}`}
                        style={{
                            border: "1px solid #e2e8f0",
                            background: "#fff",
                            borderRadius: 10,
                            padding: "0 12px",
                            fontWeight: 800,
                            fontSize: 14,
                            color: "var(--color-neutral-900)",
                            textDecoration: "none",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            height: "36px"
                        }}
                    >
                        더보기
                    </Link>
                </div>
            </div>
            <div className={viewMode === "grid" ? "mosaic" : "stack gap-12"}>
                {topItems.map(item => (
                    <LocalTile key={item.topic_id} item={item} viewMode={viewMode} />
                ))}
            </div>
        </section>
    );
}
